"""無音検出 — ffmpeg silencedetect を使用して無音区間を特定し、カット区間を計算する"""

import re
import subprocess
from typing import Any

from .utils import get_logger, get_video_duration


def detect_silence(
    video_path: str,
    noise_db: float = -35,
    min_duration: float = 0.35,
    logger=None,
) -> list[dict[str, float]]:
    """
    ffmpeg silencedetect で無音区間を検出する。

    Returns:
        [{"start": float, "end": float, "duration": float}, ...]
    """
    if logger is None:
        logger = get_logger("silence")

    cmd = [
        "ffmpeg", "-hide_banner", "-i", video_path,
        "-af", f"silencedetect=noise={noise_db}dB:d={min_duration}",
        "-f", "null", "-",
    ]
    logger.info(f"Detecting silence: noise={noise_db}dB, min_dur={min_duration}s")

    result = subprocess.run(
        cmd, capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )

    stderr = result.stderr
    silences = []

    # パース: silence_start / silence_end / silence_duration
    starts = re.findall(r"silence_start:\s*([\d.]+)", stderr)
    ends = re.findall(r"silence_end:\s*([\d.]+)\s*\|\s*silence_duration:\s*([\d.]+)", stderr)

    for i, start_str in enumerate(starts):
        start = float(start_str)
        if i < len(ends):
            end = float(ends[i][0])
            dur = float(ends[i][1])
        else:
            # 末尾まで無音が続くケース
            end = get_video_duration(video_path, logger)
            dur = end - start

        silences.append({"start": start, "end": end, "duration": dur})

    logger.info(f"Detected {len(silences)} silence segments")
    return silences


def compute_keep_segments(
    video_duration: float,
    silences: list[dict[str, float]],
    padding_before: float = 0.08,
    padding_after: float = 0.05,
    min_segment_duration: float = 0.3,
    logger=None,
) -> list[dict[str, Any]]:
    """
    無音区間から「保持する区間」を計算する。

    Returns:
        [{"start": float, "end": float, "type": "keep"}, ...]
    """
    if logger is None:
        logger = get_logger("silence")

    if not silences:
        logger.info("No silence detected — keeping entire video")
        return [{"start": 0.0, "end": video_duration, "type": "keep"}]

    keep_segments = []
    prev_end = 0.0

    for silence in silences:
        seg_start = prev_end
        # 無音開始にパディングを加える（少しだけ残す）
        seg_end = silence["start"] + padding_before

        if seg_end > seg_start and (seg_end - seg_start) >= min_segment_duration:
            keep_segments.append({
                "start": round(seg_start, 3),
                "end": round(seg_end, 3),
                "type": "keep",
            })

        # 次のセグメントの開始位置（無音終了からパディング分だけ戻す）
        prev_end = max(silence["end"] - padding_after, silence["start"])

    # 最後の無音以降の部分
    if prev_end < video_duration:
        keep_segments.append({
            "start": round(prev_end, 3),
            "end": round(video_duration, 3),
            "type": "keep",
        })

    # 極端に短いセグメントを除去（ノイズ対策）
    keep_segments = [
        s for s in keep_segments
        if (s["end"] - s["start"]) >= min_segment_duration
    ]

    # 隣接セグメントのマージ（間が極小の場合）
    merged = []
    for seg in keep_segments:
        if merged and (seg["start"] - merged[-1]["end"]) < 0.05:
            merged[-1]["end"] = seg["end"]
        else:
            merged.append(seg)

    total_keep = sum(s["end"] - s["start"] for s in merged)
    cut_ratio = (1 - total_keep / video_duration) * 100 if video_duration > 0 else 0
    logger.info(
        f"Keep segments: {len(merged)} | "
        f"Total keep: {total_keep:.1f}s / {video_duration:.1f}s | "
        f"Cut: {cut_ratio:.1f}%"
    )

    return merged
