"""動画アセンブラ — ffmpeg を使用してカット・テンポ調整・字幕焼き込み・音声正規化を実行する"""

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from .utils import get_logger, run_ffmpeg


def cut_and_tempo(
    video_path: str,
    tempo_segments: list[dict],
    output_path: str,
    temp_dir: str = "./tmp",
    video_codec: str = "libx264",
    audio_codec: str = "aac",
    video_bitrate: str = "5M",
    audio_bitrate: str = "192k",
    pixel_format: str = "yuv420p",
    logger=None,
) -> str:
    """
    テンポセグメントに従い、動画をカット＋速度変更して結合する。
    セグメント単位で切り出し → 速度調整 → 結合（concat demuxer）
    """
    if logger is None:
        logger = get_logger("assembler")

    os.makedirs(temp_dir, exist_ok=True)
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    segment_files = []

    for i, seg in enumerate(tempo_segments):
        seg_file = os.path.join(temp_dir, f"seg_{i:04d}.mp4")
        speed = seg.get("speed", 1.0)
        start = seg["start"]
        end = seg["end"]
        duration = end - start

        if duration <= 0:
            continue

        if abs(speed - 1.0) < 0.01:
            # 等速 — stream copy で高速処理
            run_ffmpeg(
                ["-ss", str(start), "-to", str(end),
                 "-i", video_path,
                 "-c", "copy",
                 "-avoid_negative_ts", "make_zero",
                 seg_file],
                logger,
                desc=f"seg {i} (copy, {start:.2f}-{end:.2f})",
            )
        else:
            # 速度変更 — re-encode
            # atempo は 0.5〜2.0 の範囲のみ対応
            video_speed = 1.0 / speed  # setpts は PTS * factor
            audio_speed = speed

            # atempo フィルタチェーン（0.5〜2.0 制約）
            atempo_chain = _build_atempo_chain(audio_speed)

            run_ffmpeg(
                ["-ss", str(start), "-to", str(end),
                 "-i", video_path,
                 "-filter_complex",
                 f"[0:v]setpts={video_speed}*PTS[v];"
                 f"[0:a]{atempo_chain}[a]",
                 "-map", "[v]", "-map", "[a]",
                 "-c:v", video_codec, "-b:v", video_bitrate,
                 "-c:a", audio_codec, "-b:a", audio_bitrate,
                 "-pix_fmt", pixel_format,
                 "-r", "30",
                 seg_file],
                logger,
                desc=f"seg {i} (speed={speed}x, {start:.2f}-{end:.2f})",
            )

        if os.path.exists(seg_file) and os.path.getsize(seg_file) > 0:
            segment_files.append(seg_file)

    if not segment_files:
        logger.error("No segments produced!")
        raise RuntimeError("No video segments were created")

    # concat demuxer で結合
    concat_list = os.path.join(temp_dir, "concat_list.txt")
    with open(concat_list, "w", encoding="utf-8") as f:
        for sf in segment_files:
            # Windows パス対応
            safe_path = sf.replace("\\", "/")
            f.write(f"file '{safe_path}'\n")

    # concat — stream copy だとずれるので re-encode
    run_ffmpeg(
        ["-f", "concat", "-safe", "0",
         "-i", concat_list,
         "-c:v", video_codec, "-b:v", video_bitrate,
         "-c:a", audio_codec, "-b:a", audio_bitrate,
         "-pix_fmt", pixel_format,
         "-movflags", "+faststart",
         output_path],
        logger,
        desc="concat segments",
    )

    logger.info(f"Cut & tempo done: {output_path} ({len(segment_files)} segments)")
    return output_path


def normalize_audio(
    video_path: str,
    output_path: str,
    target_lufs: float = -16,
    true_peak: float = -1.5,
    lra: float = 11,
    logger=None,
) -> str:
    """2パスの loudnorm で音声を正規化する"""
    if logger is None:
        logger = get_logger("assembler")

    # Pass 1: 測定
    result = run_ffmpeg(
        ["-i", video_path,
         "-af", f"loudnorm=I={target_lufs}:TP={true_peak}:LRA={lra}:print_format=json",
         "-f", "null", "-"],
        logger,
        desc="loudnorm pass 1 (measure)",
    )

    # stderr から JSON を抽出
    stderr = result.stderr
    json_start = stderr.rfind("{")
    json_end = stderr.rfind("}") + 1

    if json_start >= 0 and json_end > json_start:
        measured = json.loads(stderr[json_start:json_end])
        measured_i = measured.get("input_i", target_lufs)
        measured_tp = measured.get("input_tp", true_peak)
        measured_lra = measured.get("input_lra", lra)
        measured_thresh = measured.get("input_thresh", -24)
        target_offset = measured.get("target_offset", 0)
    else:
        logger.warning("Could not parse loudnorm measurement, using defaults")
        measured_i = target_lufs
        measured_tp = true_peak
        measured_lra = lra
        measured_thresh = -24
        target_offset = 0

    # Pass 2: 適用
    run_ffmpeg(
        ["-i", video_path,
         "-af",
         f"loudnorm=I={target_lufs}:TP={true_peak}:LRA={lra}"
         f":measured_I={measured_i}:measured_TP={measured_tp}"
         f":measured_LRA={measured_lra}:measured_thresh={measured_thresh}"
         f":offset={target_offset}:linear=true",
         "-c:v", "copy",
         output_path],
        logger,
        desc="loudnorm pass 2 (apply)",
    )

    logger.info(f"Audio normalized: {output_path}")
    return output_path


def burn_subtitles(
    video_path: str,
    srt_path: str,
    output_path: str,
    style: dict | None = None,
    video_codec: str = "libx264",
    video_bitrate: str = "5M",
    audio_codec: str = "aac",
    audio_bitrate: str = "192k",
    pixel_format: str = "yuv420p",
    logger=None,
) -> str:
    """SRT 字幕を動画に焼き込む"""
    if logger is None:
        logger = get_logger("assembler")

    # パスをエスケープ（Windows 対応: バックスラッシュとコロンをエスケープ）
    srt_escaped = srt_path.replace("\\", "/").replace(":", "\\\\:")

    # スタイル文字列を構築
    style_str = ""
    if style:
        parts = []
        if style.get("font_name"):
            parts.append(f"FontName={style['font_name']}")
        if style.get("font_size"):
            parts.append(f"FontSize={style['font_size']}")
        if style.get("primary_color"):
            parts.append(f"PrimaryColour={style['primary_color']}")
        if style.get("outline_color"):
            parts.append(f"OutlineColour={style['outline_color']}")
        if style.get("outline_width"):
            parts.append(f"Outline={style['outline_width']}")
        if style.get("shadow") is not None:
            parts.append(f"Shadow={style['shadow']}")
        if style.get("alignment"):
            parts.append(f"Alignment={style['alignment']}")
        if style.get("margin_v"):
            parts.append(f"MarginV={style['margin_v']}")
        if parts:
            style_str = ":force_style='" + ",".join(parts) + "'"

    vf = f"subtitles={srt_escaped}{style_str}"

    run_ffmpeg(
        ["-i", video_path,
         "-vf", vf,
         "-c:v", video_codec, "-b:v", video_bitrate,
         "-c:a", audio_codec, "-b:a", audio_bitrate,
         "-pix_fmt", pixel_format,
         "-movflags", "+faststart",
         output_path],
        logger,
        desc="burn subtitles",
    )

    logger.info(f"Subtitles burned: {output_path}")
    return output_path


def add_bgm(
    video_path: str,
    bgm_path: str,
    output_path: str,
    bgm_volume_db: float = -22,
    logger=None,
) -> str:
    """BGM を動画に合成する"""
    if logger is None:
        logger = get_logger("assembler")

    if not os.path.exists(bgm_path):
        logger.warning(f"BGM file not found: {bgm_path}, skipping")
        return video_path

    run_ffmpeg(
        ["-i", video_path, "-i", bgm_path,
         "-filter_complex",
         f"[1:a]volume={bgm_volume_db}dB,aloop=loop=-1:size=2e+09[bgm];"
         f"[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[a]",
         "-map", "0:v", "-map", "[a]",
         "-c:v", "copy",
         "-shortest",
         output_path],
        logger,
        desc="add BGM",
    )

    logger.info(f"BGM added: {output_path}")
    return output_path


def concat_intro_outro(
    video_path: str,
    output_path: str,
    intro_path: str | None = None,
    outro_path: str | None = None,
    temp_dir: str = "./tmp",
    logger=None,
) -> str:
    """イントロ・アウトロを結合する"""
    if logger is None:
        logger = get_logger("assembler")

    parts = []
    if intro_path and os.path.exists(intro_path):
        parts.append(intro_path)
    parts.append(video_path)
    if outro_path and os.path.exists(outro_path):
        parts.append(outro_path)

    if len(parts) == 1:
        return video_path

    concat_list = os.path.join(temp_dir, "intro_outro_list.txt")
    with open(concat_list, "w", encoding="utf-8") as f:
        for p in parts:
            safe = p.replace("\\", "/")
            f.write(f"file '{safe}'\n")

    run_ffmpeg(
        ["-f", "concat", "-safe", "0",
         "-i", concat_list,
         "-c", "copy",
         "-movflags", "+faststart",
         output_path],
        logger,
        desc="concat intro/outro",
    )

    logger.info(f"Intro/outro concatenated: {output_path}")
    return output_path


def _build_atempo_chain(speed: float) -> str:
    """atempo フィルタのチェーンを構築する（0.5〜2.0 制約対応）"""
    filters = []
    remaining = speed
    while remaining > 2.0:
        filters.append("atempo=2.0")
        remaining /= 2.0
    while remaining < 0.5:
        filters.append("atempo=0.5")
        remaining /= 0.5
    filters.append(f"atempo={remaining:.4f}")
    return ",".join(filters)
