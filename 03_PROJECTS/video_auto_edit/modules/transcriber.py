"""文字起こし — faster-whisper を使用した音声認識"""

import os
import time
from typing import Any

from .utils import get_logger, run_ffmpeg


def extract_audio(video_path: str, output_path: str, logger=None) -> str:
    """動画から WAV 音声を抽出する"""
    if logger is None:
        logger = get_logger("transcriber")

    run_ffmpeg(
        ["-i", video_path, "-vn", "-acodec", "pcm_s16le",
         "-ar", "16000", "-ac", "1", output_path],
        logger,
        desc="extract audio",
    )
    return output_path


def transcribe_audio(
    audio_path: str,
    model_size: str = "base",
    language: str = "ja",
    device: str = "cpu",
    compute_type: str = "int8",
    beam_size: int = 5,
    vad_filter: bool = True,
    logger=None,
) -> list[dict[str, Any]]:
    """
    faster-whisper で文字起こしを行う。

    Returns:
        [{
            "start": float,
            "end": float,
            "text": str,
            "words": [{"start": float, "end": float, "word": str}, ...] | None
        }, ...]
    """
    if logger is None:
        logger = get_logger("transcriber")

    logger.info(f"Loading faster-whisper model: {model_size} (device={device}, compute={compute_type})")
    t0 = time.time()

    try:
        from faster_whisper import WhisperModel
    except ImportError:
        logger.error("faster-whisper not installed. Run: pip install faster-whisper")
        raise

    model = WhisperModel(model_size, device=device, compute_type=compute_type)
    load_time = time.time() - t0
    logger.info(f"Model loaded in {load_time:.1f}s")

    logger.info("Transcribing...")
    t1 = time.time()

    segments_iter, info = model.transcribe(
        audio_path,
        language=language,
        beam_size=beam_size,
        vad_filter=vad_filter,
        word_timestamps=True,
    )

    segments = []
    for seg in segments_iter:
        words = None
        if seg.words:
            words = [
                {"start": w.start, "end": w.end, "word": w.word}
                for w in seg.words
            ]
        segments.append({
            "start": seg.start,
            "end": seg.end,
            "text": seg.text.strip(),
            "words": words,
        })

    transcribe_time = time.time() - t1
    logger.info(
        f"Transcription done: {len(segments)} segments, "
        f"{transcribe_time:.1f}s | "
        f"Detected language: {info.language} (prob={info.language_probability:.2f})"
    )

    return segments


def compute_word_density(segments: list[dict]) -> list[dict]:
    """各セグメントの単語密度（words/sec）を計算する"""
    for seg in segments:
        duration = seg["end"] - seg["start"]
        if duration > 0 and seg.get("words"):
            seg["word_density"] = len(seg["words"]) / duration
        elif duration > 0 and seg.get("text"):
            # words がない場合は文字数ベースで推定
            seg["word_density"] = len(seg["text"]) / duration
        else:
            seg["word_density"] = 0.0
    return segments
