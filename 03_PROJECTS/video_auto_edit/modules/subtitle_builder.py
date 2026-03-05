"""字幕生成 — 文字起こし結果から SRT を生成する"""

import os
from typing import Any

from .utils import (
    apply_terms_dict,
    get_logger,
    load_terms_dict,
    seconds_to_srt_time,
)


def split_text_to_lines(
    text: str,
    max_chars: int = 22,
    min_chars: int = 15,
    max_lines: int = 2,
) -> list[str]:
    """
    テキストを字幕用に行分割する。
    日本語は句読点・助詞の位置で分割を試みる。
    """
    text = text.strip()
    if len(text) <= max_chars:
        return [text]

    if max_lines == 1:
        return [text[:max_chars]]

    # 2行に分割
    # 分割候補位置を探す（句読点、助詞、空白）
    split_chars = "、。！？,.!? 　"
    particles = "はがをにでとのもへやかけ"

    best_pos = len(text) // 2  # デフォルト: 中央
    best_score = float("inf")

    for i in range(min(min_chars, len(text) - 1), min(max_chars + 1, len(text))):
        # 中央に近いほどスコアが良い
        center_dist = abs(i - len(text) / 2)
        score = center_dist

        # 句読点の直後は最良の分割位置
        if i > 0 and text[i - 1] in split_chars:
            score -= 10
        # 助詞の直後も良い分割位置
        elif i > 0 and text[i - 1] in particles:
            score -= 5

        if score < best_score:
            best_score = score
            best_pos = i

    line1 = text[:best_pos].strip()
    line2 = text[best_pos:].strip()

    # 2行目がさらに長い場合は切る
    if len(line2) > max_chars:
        line2 = line2[:max_chars]

    lines = []
    if line1:
        lines.append(line1)
    if line2:
        lines.append(line2)

    return lines if lines else [text[:max_chars]]


def adjust_timing(
    start: float,
    end: float,
    min_display: float = 0.8,
    max_display: float = 4.0,
) -> tuple[float, float]:
    """字幕の表示時間を調整する"""
    duration = end - start

    if duration < min_display:
        end = start + min_display

    if duration > max_display:
        end = start + max_display

    return round(start, 3), round(end, 3)


def build_subtitle_entries(
    segments: list[dict[str, Any]],
    time_mapping: list[dict] | None = None,
    max_chars: int = 22,
    min_chars: int = 15,
    max_lines: int = 2,
    min_display: float = 0.8,
    max_display: float = 4.0,
    terms: dict[str, str] | None = None,
    logger=None,
) -> list[dict[str, Any]]:
    """
    文字起こしセグメントから字幕エントリを生成する。

    time_mapping が指定された場合、元の時間を編集後の時間に変換する。

    Returns:
        [{"index": int, "start": float, "end": float, "text": str, "lines": [str]}, ...]
    """
    if logger is None:
        logger = get_logger("subtitle")

    entries = []
    idx = 1

    for seg in segments:
        text = seg["text"]
        if not text.strip():
            continue

        # 辞書適用
        if terms:
            text = apply_terms_dict(text, terms)

        # 時間マッピング適用
        start = seg["start"]
        end = seg["end"]
        if time_mapping:
            start = map_time(start, time_mapping)
            end = map_time(end, time_mapping)
            if start is None or end is None:
                continue  # カットされた区間

        # タイミング調整
        start, end = adjust_timing(start, end, min_display, max_display)

        # 行分割
        lines = split_text_to_lines(text, max_chars, min_chars, max_lines)

        entries.append({
            "index": idx,
            "start": start,
            "end": end,
            "text": text,
            "lines": lines,
        })
        idx += 1

    # 時間の単調増加を保証
    entries = enforce_monotonic(entries)

    logger.info(f"Subtitle entries: {len(entries)}")
    return entries


def map_time(original_time: float, time_mapping: list[dict]) -> float | None:
    """
    元の動画時間を、編集後の動画時間に変換する。

    time_mapping: [
        {"orig_start": float, "orig_end": float,
         "edit_start": float, "edit_end": float, "speed": float},
        ...
    ]
    """
    for m in time_mapping:
        if m["orig_start"] <= original_time <= m["orig_end"]:
            # この区間に含まれる
            offset_in_orig = original_time - m["orig_start"]
            speed = m.get("speed", 1.0)
            offset_in_edit = offset_in_orig / speed
            return m["edit_start"] + offset_in_edit
    return None  # カットされた区間


def enforce_monotonic(entries: list[dict]) -> list[dict]:
    """字幕の時間が単調増加であることを保証する"""
    result = []
    prev_end = 0.0
    for e in entries:
        if e["start"] < prev_end:
            e["start"] = prev_end + 0.001
        if e["end"] <= e["start"]:
            e["end"] = e["start"] + 0.5
        result.append(e)
        prev_end = e["end"]
    return result


def entries_to_srt(entries: list[dict]) -> str:
    """字幕エントリを SRT 形式のテキストに変換する"""
    lines = []
    for e in entries:
        lines.append(str(e["index"]))
        start_ts = seconds_to_srt_time(e["start"])
        end_ts = seconds_to_srt_time(e["end"])
        lines.append(f"{start_ts} --> {end_ts}")
        lines.append("\n".join(e["lines"]))
        lines.append("")  # 空行

    return "\n".join(lines)


def write_srt(entries: list[dict], output_path: str, logger=None):
    """SRT ファイルを書き出す"""
    if logger is None:
        logger = get_logger("subtitle")
    srt_text = entries_to_srt(entries)
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(srt_text)
    logger.info(f"SRT written: {output_path} ({len(entries)} entries)")


def write_transcript(segments: list[dict], output_path: str, terms: dict | None = None, logger=None):
    """全文テキストを書き出す"""
    if logger is None:
        logger = get_logger("subtitle")
    texts = []
    for seg in segments:
        text = seg["text"]
        if terms:
            text = apply_terms_dict(text, terms)
        texts.append(text)

    full_text = "\n".join(texts)
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_text)
    logger.info(f"Transcript written: {output_path} ({len(texts)} lines)")
