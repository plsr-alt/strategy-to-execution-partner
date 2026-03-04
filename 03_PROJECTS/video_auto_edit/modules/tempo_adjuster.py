"""テンポ調整（ハイパースキップ） — 冗長区間を検出し速度変更リストを生成する"""

from typing import Any

from .utils import get_logger


def analyze_segments_for_tempo(
    keep_segments: list[dict],
    transcription: list[dict],
    low_density_threshold: float = 1.5,
    fast_speech_threshold: float = 4.5,
    min_segment_for_tempo: float = 2.0,
    speedup_factor: float = 1.25,
    max_speed: float = 1.35,
    logger=None,
) -> list[dict[str, Any]]:
    """
    保持セグメントと文字起こし結果を照合し、各セグメントの速度を決定する。

    Returns:
        [{
            "start": float, "end": float,
            "speed": float,
            "reason": str,
        }, ...]
    """
    if logger is None:
        logger = get_logger("tempo")

    result = []
    for seg in keep_segments:
        seg_start = seg["start"]
        seg_end = seg["end"]
        seg_duration = seg_end - seg_start

        # このセグメントに含まれる文字起こしを探す
        overlapping_trans = []
        for t in transcription:
            # 重なり判定
            if t["end"] > seg_start and t["start"] < seg_end:
                overlapping_trans.append(t)

        # 単語密度を計算
        total_words = 0
        for t in overlapping_trans:
            if t.get("words"):
                total_words += len(t["words"])
            elif t.get("text"):
                total_words += len(t["text"])

        density = total_words / seg_duration if seg_duration > 0 else 0

        # 速度決定ロジック
        speed = 1.0
        reason = "normal"

        if seg_duration < min_segment_for_tempo:
            # 短いセグメントはそのまま
            speed = 1.0
            reason = "short_segment"
        elif density > fast_speech_threshold:
            # 早口 → そのまま（速度上げると破綻）
            speed = 1.0
            reason = "fast_speech"
        elif density < low_density_threshold and seg_duration > min_segment_for_tempo:
            # 冗長（単語密度が低い）→ 速度アップ
            speed = min(speedup_factor, max_speed)
            reason = "low_density"
        elif len(overlapping_trans) == 0:
            # 文字起こしなし（間？）→ カット優先だが残ってる場合は速度アップ
            speed = min(speedup_factor, max_speed)
            reason = "no_speech"

        result.append({
            "start": seg_start,
            "end": seg_end,
            "speed": round(speed, 2),
            "reason": reason,
            "word_density": round(density, 2),
        })

    # ログ
    tempo_changed = [s for s in result if s["speed"] != 1.0]
    logger.info(
        f"Tempo analysis: {len(result)} segments, "
        f"{len(tempo_changed)} with speed change"
    )

    return result


def build_time_mapping(
    tempo_segments: list[dict],
) -> list[dict[str, float]]:
    """
    テンポ調整後の時間マッピングを構築する。
    これにより、元の時間 → 編集後の時間 の変換が可能になる。

    Returns:
        [{
            "orig_start": float, "orig_end": float,
            "edit_start": float, "edit_end": float,
            "speed": float,
        }, ...]
    """
    mapping = []
    edit_cursor = 0.0

    for seg in tempo_segments:
        orig_duration = seg["end"] - seg["start"]
        speed = seg.get("speed", 1.0)
        edit_duration = orig_duration / speed

        mapping.append({
            "orig_start": seg["start"],
            "orig_end": seg["end"],
            "edit_start": round(edit_cursor, 3),
            "edit_end": round(edit_cursor + edit_duration, 3),
            "speed": speed,
        })

        edit_cursor += edit_duration

    return mapping


def estimate_final_duration(time_mapping: list[dict]) -> float:
    """編集後の最終的な動画長を推定する"""
    if not time_mapping:
        return 0.0
    return time_mapping[-1]["edit_end"]
