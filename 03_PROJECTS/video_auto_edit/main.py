#!/usr/bin/env python3
"""
動画自動編集パイプライン
========================
入力動画 → 無音カット → テンポ調整 → 字幕生成 → 書き出し

Usage:
    python main.py                    # config.yaml を使用
    python main.py --config my.yaml   # 別の設定ファイルを指定
    python main.py --input video.mp4  # 単一ファイル指定
"""

import argparse
import json
import os
import shutil
import sys
import time
import traceback
from glob import glob
from pathlib import Path

import yaml

from modules.assembler import (
    add_bgm,
    burn_subtitles,
    concat_intro_outro,
    cut_and_tempo,
    normalize_audio,
)
from modules.silence_detector import compute_keep_segments, detect_silence
from modules.subtitle_builder import (
    build_subtitle_entries,
    write_srt,
    write_transcript,
)
from modules.tempo_adjuster import (
    analyze_segments_for_tempo,
    build_time_mapping,
    estimate_final_duration,
)
from modules.transcriber import (
    compute_word_density,
    extract_audio,
    transcribe_audio,
)
from modules.utils import (
    StepTimer,
    check_dependencies,
    get_logger,
    get_video_duration,
    get_video_info,
    load_terms_dict,
)


def load_config(config_path: str = "config.yaml") -> dict:
    """設定ファイルを読み込む"""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def process_video(video_path: str, config: dict, logger) -> dict:
    """
    1本の動画を処理するメイン関数。

    Returns:
        edit_log dict
    """
    timer = StepTimer()
    basename = Path(video_path).stem
    out_dir = config["output_dir"]
    temp_dir = config.get("temp_dir", "./tmp")

    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(temp_dir, exist_ok=True)

    # 出力パス
    final_mp4 = os.path.join(out_dir, f"{basename}_final.mp4")
    final_srt = os.path.join(out_dir, f"{basename}_final.srt")
    transcript_txt = os.path.join(out_dir, f"{basename}_transcript.txt")
    edit_log_path = os.path.join(out_dir, f"{basename}_edit_log.json")

    # 中間ファイル
    audio_wav = os.path.join(temp_dir, f"{basename}_audio.wav")
    cut_mp4 = os.path.join(temp_dir, f"{basename}_cut.mp4")
    norm_mp4 = os.path.join(temp_dir, f"{basename}_norm.mp4")
    bgm_mp4 = os.path.join(temp_dir, f"{basename}_bgm.mp4")
    intro_mp4 = os.path.join(temp_dir, f"{basename}_intro.mp4")

    edit_log = {
        "input": video_path,
        "basename": basename,
        "start_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "steps": [],
    }

    try:
        # ============================
        # Step 0: 動画情報取得
        # ============================
        timer.start("video_info")
        video_duration = get_video_duration(video_path, logger)
        video_info = get_video_info(video_path, logger)
        logger.info(
            f"Input: {video_path} | "
            f"{video_duration:.1f}s | "
            f"{video_info['width']}x{video_info['height']} | "
            f"{video_info['fps']:.1f}fps"
        )
        timer.stop(extra={"duration": video_duration, "info": video_info})

        # ============================
        # Step 1: 音声抽出
        # ============================
        timer.start("extract_audio")
        logger.info("=" * 50)
        logger.info("Step 1: Extracting audio...")
        extract_audio(video_path, audio_wav, logger)
        timer.stop()

        # ============================
        # Step 2: 無音検出
        # ============================
        timer.start("silence_detection")
        logger.info("=" * 50)
        logger.info("Step 2: Detecting silence...")
        silence_cfg = config.get("silence", {})
        silences = detect_silence(
            video_path,
            noise_db=silence_cfg.get("noise_threshold_db", -35),
            min_duration=silence_cfg.get("min_silence_duration", 0.35),
            logger=logger,
        )
        keep_segments = compute_keep_segments(
            video_duration,
            silences,
            padding_before=silence_cfg.get("padding_before", 0.08),
            padding_after=silence_cfg.get("padding_after", 0.05),
            min_segment_duration=silence_cfg.get("min_segment_duration", 0.3),
            logger=logger,
        )
        timer.stop(extra={
            "silence_count": len(silences),
            "keep_segments": len(keep_segments),
        })

        # ============================
        # Step 3: 文字起こし
        # ============================
        timer.start("transcription")
        logger.info("=" * 50)
        logger.info("Step 3: Transcribing audio...")
        trans_cfg = config.get("transcription", {})
        transcription = transcribe_audio(
            audio_wav,
            model_size=trans_cfg.get("model_size", "base"),
            language=trans_cfg.get("language", "ja"),
            device=trans_cfg.get("device", "cpu"),
            compute_type=trans_cfg.get("compute_type", "int8"),
            beam_size=trans_cfg.get("beam_size", 5),
            vad_filter=trans_cfg.get("vad_filter", True),
            logger=logger,
        )
        transcription = compute_word_density(transcription)
        timer.stop(extra={"segments": len(transcription)})

        # ============================
        # Step 4: テンポ調整分析
        # ============================
        timer.start("tempo_analysis")
        logger.info("=" * 50)
        logger.info("Step 4: Analyzing tempo...")
        tempo_cfg = config.get("tempo", {})

        if tempo_cfg.get("enabled", True):
            tempo_segments = analyze_segments_for_tempo(
                keep_segments,
                transcription,
                low_density_threshold=tempo_cfg.get("low_density_threshold", 1.5),
                fast_speech_threshold=tempo_cfg.get("fast_speech_threshold", 4.5),
                min_segment_for_tempo=tempo_cfg.get("min_segment_for_tempo", 2.0),
                speedup_factor=tempo_cfg.get("speedup_factor", 1.25),
                max_speed=tempo_cfg.get("max_speed", 1.35),
                logger=logger,
            )
        else:
            # テンポ調整無効 — 等速のまま
            tempo_segments = [
                {"start": s["start"], "end": s["end"], "speed": 1.0, "reason": "disabled"}
                for s in keep_segments
            ]

        time_mapping = build_time_mapping(tempo_segments)
        estimated_duration = estimate_final_duration(time_mapping)
        logger.info(
            f"Estimated output: {estimated_duration:.1f}s "
            f"(original {video_duration:.1f}s, "
            f"reduction {(1 - estimated_duration / video_duration) * 100:.1f}%)"
        )
        timer.stop(extra={
            "tempo_segments": len(tempo_segments),
            "estimated_duration": estimated_duration,
        })

        # ============================
        # Step 5: カット＋テンポ適用
        # ============================
        timer.start("cut_and_tempo")
        logger.info("=" * 50)
        logger.info("Step 5: Cutting and applying tempo...")
        out_cfg = config.get("output", {})
        cut_and_tempo(
            video_path,
            tempo_segments,
            cut_mp4,
            temp_dir=temp_dir,
            video_codec=out_cfg.get("video_codec", "libx264"),
            audio_codec=out_cfg.get("audio_codec", "aac"),
            video_bitrate=out_cfg.get("video_bitrate", "5M"),
            audio_bitrate=out_cfg.get("audio_bitrate", "192k"),
            pixel_format=out_cfg.get("pixel_format", "yuv420p"),
            logger=logger,
        )
        timer.stop()

        # ============================
        # Step 6: 音声正規化
        # ============================
        timer.start("audio_normalize")
        logger.info("=" * 50)
        logger.info("Step 6: Normalizing audio...")
        audio_cfg = config.get("audio", {})
        normalize_audio(
            cut_mp4,
            norm_mp4,
            target_lufs=audio_cfg.get("target_lufs", -16),
            true_peak=audio_cfg.get("true_peak", -1.5),
            lra=audio_cfg.get("lra", 11),
            logger=logger,
        )
        timer.stop()

        # ============================
        # Step 6.5: BGM（オプション）
        # ============================
        current_video = norm_mp4
        bgm_cfg = config.get("bgm", {})
        if bgm_cfg.get("enabled", False):
            timer.start("bgm")
            logger.info("Step 6.5: Adding BGM...")
            current_video = add_bgm(
                norm_mp4, bgm_cfg["file"], bgm_mp4,
                bgm_volume_db=bgm_cfg.get("volume_db", -22),
                logger=logger,
            )
            timer.stop()

        # ============================
        # Step 6.6: イントロ・アウトロ（オプション）
        # ============================
        intro_cfg = config.get("intro", {})
        outro_cfg = config.get("outro", {})
        if intro_cfg.get("enabled", False) or outro_cfg.get("enabled", False):
            timer.start("intro_outro")
            logger.info("Step 6.6: Concatenating intro/outro...")
            current_video = concat_intro_outro(
                current_video,
                intro_mp4,
                intro_path=intro_cfg.get("file") if intro_cfg.get("enabled") else None,
                outro_path=outro_cfg.get("file") if outro_cfg.get("enabled") else None,
                temp_dir=temp_dir,
                logger=logger,
            )
            timer.stop()

        # ============================
        # Step 7: 字幕生成
        # ============================
        timer.start("subtitle_generation")
        logger.info("=" * 50)
        logger.info("Step 7: Generating subtitles...")
        sub_cfg = config.get("subtitle", {})
        dict_path = config.get("dict_file", "./dict/terms.csv")
        terms = load_terms_dict(dict_path)
        if terms:
            logger.info(f"Loaded {len(terms)} terms from dictionary")

        subtitle_entries = build_subtitle_entries(
            transcription,
            time_mapping=time_mapping,
            max_chars=sub_cfg.get("max_chars_per_line", 22),
            min_chars=sub_cfg.get("min_chars_per_line", 15),
            max_lines=sub_cfg.get("max_lines", 2),
            min_display=sub_cfg.get("min_display_sec", 0.8),
            max_display=sub_cfg.get("max_display_sec", 4.0),
            terms=terms,
            logger=logger,
        )

        write_srt(subtitle_entries, final_srt, logger)
        write_transcript(transcription, transcript_txt, terms, logger)
        timer.stop(extra={"subtitle_count": len(subtitle_entries)})

        # ============================
        # Step 8: 字幕焼き込み
        # ============================
        timer.start("burn_subtitles")
        logger.info("=" * 50)
        logger.info("Step 8: Burning subtitles...")
        style = sub_cfg.get("style", {})
        burn_subtitles(
            current_video,
            final_srt,
            final_mp4,
            style=style,
            video_codec=out_cfg.get("video_codec", "libx264"),
            video_bitrate=out_cfg.get("video_bitrate", "5M"),
            audio_codec=out_cfg.get("audio_codec", "aac"),
            audio_bitrate=out_cfg.get("audio_bitrate", "192k"),
            pixel_format=out_cfg.get("pixel_format", "yuv420p"),
            logger=logger,
        )
        timer.stop()

        # ============================
        # 完了
        # ============================
        edit_log["status"] = "success"
        edit_log["output"] = {
            "video": final_mp4,
            "srt": final_srt,
            "transcript": transcript_txt,
        }
        edit_log["original_duration"] = video_duration
        edit_log["output_duration"] = estimated_duration
        edit_log["reduction_percent"] = round(
            (1 - estimated_duration / video_duration) * 100, 1
        ) if video_duration > 0 else 0
        edit_log["silence_segments"] = silences
        edit_log["tempo_segments"] = tempo_segments
        edit_log["time_mapping"] = time_mapping

    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        logger.error(traceback.format_exc())
        edit_log["status"] = "error"
        edit_log["error"] = str(e)
        edit_log["traceback"] = traceback.format_exc()

    finally:
        edit_log["end_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
        edit_log["steps"] = timer.to_dict()

        # edit_log 書き出し
        with open(edit_log_path, "w", encoding="utf-8") as f:
            json.dump(edit_log, f, ensure_ascii=False, indent=2, default=str)
        logger.info(f"Edit log: {edit_log_path}")

    return edit_log


def cleanup_temp(temp_dir: str, logger):
    """一時ファイルを削除する"""
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir, ignore_errors=True)
        logger.info(f"Temp dir cleaned: {temp_dir}")


def main():
    parser = argparse.ArgumentParser(description="動画自動編集パイプライン")
    parser.add_argument("--config", default="config.yaml", help="設定ファイルパス")
    parser.add_argument("--input", default=None, help="入力ファイル（単一指定）")
    parser.add_argument("--keep-temp", action="store_true", help="一時ファイルを残す")
    args = parser.parse_args()

    # 設定読み込み
    config = load_config(args.config)

    # ロガー初期化
    log_cfg = config.get("logging", {})
    logger = get_logger(
        "pipeline",
        level=log_cfg.get("level", "INFO"),
        log_file=log_cfg.get("log_file", "./out/pipeline.log"),
    )

    logger.info("=" * 60)
    logger.info("動画自動編集パイプライン — 開始")
    logger.info("=" * 60)

    # 依存チェック
    deps = check_dependencies(logger)
    if not deps.get("ffmpeg"):
        logger.error("ffmpeg is required. Aborting.")
        sys.exit(1)

    # 入力ファイル収集
    if args.input:
        video_files = [args.input]
    else:
        input_dir = config.get("input_dir", "./in")
        extensions = ["*.mp4", "*.mov", "*.avi", "*.mkv", "*.webm", "*.m4v"]
        video_files = []
        for ext in extensions:
            video_files.extend(glob(os.path.join(input_dir, ext)))
            video_files.extend(glob(os.path.join(input_dir, ext.upper())))

    if not video_files:
        logger.warning("No input videos found!")
        sys.exit(0)

    logger.info(f"Found {len(video_files)} video(s) to process")

    # 各ファイルを処理
    results = []
    for i, vf in enumerate(video_files):
        logger.info(f"\n{'#' * 60}")
        logger.info(f"Processing [{i + 1}/{len(video_files)}]: {vf}")
        logger.info(f"{'#' * 60}")

        try:
            result = process_video(vf, config, logger)
            results.append(result)
            if result["status"] == "success":
                logger.info(f"✓ Done: {vf} → {result['output']['video']}")
            else:
                logger.error(f"✗ Failed: {vf} — {result.get('error', 'unknown')}")
        except Exception as e:
            logger.error(f"✗ Unhandled error for {vf}: {e}")
            results.append({"input": vf, "status": "error", "error": str(e)})

    # 一時ファイルクリーンアップ
    if not args.keep_temp:
        cleanup_temp(config.get("temp_dir", "./tmp"), logger)

    # サマリー
    logger.info("\n" + "=" * 60)
    logger.info("パイプライン完了 — サマリー")
    logger.info("=" * 60)
    success = sum(1 for r in results if r.get("status") == "success")
    failed = len(results) - success
    logger.info(f"Total: {len(results)} | Success: {success} | Failed: {failed}")

    for r in results:
        status = "✓" if r.get("status") == "success" else "✗"
        logger.info(f"  {status} {r.get('input', '?')}")

    # 終了コード
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
