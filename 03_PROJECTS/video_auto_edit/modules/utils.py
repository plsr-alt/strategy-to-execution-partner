"""共通ユーティリティ"""

import csv
import json
import logging
import os
import platform
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any


def get_logger(name: str, level: str = "INFO", log_file: str | None = None) -> logging.Logger:
    """ロガーを作成する"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)-7s %(name)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # コンソール
    if not logger.handlers:
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        # ファイル
        if log_file:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            fh = logging.FileHandler(log_file, encoding="utf-8")
            fh.setFormatter(formatter)
            logger.addHandler(fh)

    return logger


def run_ffmpeg(args: list[str], logger: logging.Logger, desc: str = "") -> subprocess.CompletedProcess:
    """ffmpeg コマンドを実行してログに記録する"""
    cmd = ["ffmpeg", "-hide_banner", "-y"] + args
    logger.debug(f"ffmpeg cmd: {' '.join(cmd)}")
    t0 = time.time()
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    elapsed = time.time() - t0
    if result.returncode != 0:
        logger.error(f"ffmpeg failed ({desc}): {result.stderr[-500:]}")
        raise RuntimeError(f"ffmpeg error ({desc}): {result.stderr[-300:]}")
    logger.info(f"ffmpeg OK ({desc}) — {elapsed:.1f}s")
    return result


def run_ffprobe(args: list[str], logger: logging.Logger) -> str:
    """ffprobe コマンドを実行して stdout を返す"""
    cmd = ["ffprobe", "-hide_banner"] + args
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        logger.error(f"ffprobe failed: {result.stderr[-300:]}")
        raise RuntimeError(f"ffprobe error: {result.stderr[-300:]}")
    return result.stdout


def get_video_duration(video_path: str, logger: logging.Logger) -> float:
    """動画の長さ（秒）を取得する"""
    out = run_ffprobe(
        ["-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", video_path],
        logger,
    )
    return float(out.strip())


def get_video_info(video_path: str, logger: logging.Logger) -> dict:
    """動画のメタ情報を取得する"""
    out = run_ffprobe(
        ["-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height,r_frame_rate,codec_name",
         "-of", "json", video_path],
        logger,
    )
    data = json.loads(out)
    stream = data.get("streams", [{}])[0]
    # フレームレート解析
    fps_str = stream.get("r_frame_rate", "30/1")
    if "/" in fps_str:
        num, den = fps_str.split("/")
        fps = float(num) / float(den) if float(den) else 30.0
    else:
        fps = float(fps_str)
    return {
        "width": int(stream.get("width", 1920)),
        "height": int(stream.get("height", 1080)),
        "fps": fps,
        "codec": stream.get("codec_name", "h264"),
    }


def load_terms_dict(dict_path: str) -> dict[str, str]:
    """固有名詞辞書を読み込む"""
    terms = {}
    if not os.path.exists(dict_path):
        return terms
    with open(dict_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            before = row.get("before", "").strip()
            after = row.get("after", "").strip()
            if before and after:
                terms[before] = after
    return terms


def apply_terms_dict(text: str, terms: dict[str, str]) -> str:
    """テキストに辞書を適用して表記揺れを統一する"""
    for before, after in terms.items():
        text = text.replace(before, after)
    return text


def seconds_to_srt_time(seconds: float) -> str:
    """秒を SRT タイムスタンプに変換する (HH:MM:SS,mmm)"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def check_dependencies(logger: logging.Logger) -> dict:
    """必要な外部ツールの存在を確認する"""
    info = {
        "os": platform.system(),
        "platform": platform.platform(),
        "python": platform.python_version(),
    }

    # ffmpeg
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        result = subprocess.run(
            ["ffmpeg", "-version"], capture_output=True, text=True
        )
        version_line = result.stdout.split("\n")[0] if result.stdout else "unknown"
        info["ffmpeg"] = version_line
        logger.info(f"ffmpeg found: {version_line}")
    else:
        info["ffmpeg"] = None
        logger.error("ffmpeg not found! Please install ffmpeg.")

    # ffprobe
    ffprobe_path = shutil.which("ffprobe")
    info["ffprobe"] = "found" if ffprobe_path else None
    if not ffprobe_path:
        logger.error("ffprobe not found!")

    return info


class StepTimer:
    """各工程の処理時間を計測するユーティリティ"""

    def __init__(self):
        self.steps: list[dict[str, Any]] = []
        self._current: dict | None = None

    def start(self, step_name: str):
        self._current = {"step": step_name, "start": time.time()}

    def stop(self, extra: dict | None = None):
        if self._current:
            self._current["end"] = time.time()
            self._current["duration_sec"] = round(
                self._current["end"] - self._current["start"], 2
            )
            if extra:
                self._current.update(extra)
            self.steps.append(self._current)
            self._current = None

    def to_dict(self) -> list[dict]:
        return self.steps
