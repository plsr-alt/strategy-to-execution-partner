#!/usr/bin/env python3
# ============================================================
# YouTube自動化パイプライン — メインスクリプト
# ============================================================
# Usage: python youtube_pipeline.py [--theme <theme>] [--output <dir>] [--log-file <path>]

import argparse
import json
import logging
import os
import re
import subprocess
import sys
import time
import traceback
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional

import requests
from dotenv import load_dotenv
from groq import Groq

# Pillow 10+ で ANTIALIAS が削除された問題の互換パッチ
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

# ============================================================
# 設定・定数
# ============================================================

load_dotenv()

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logger = logging.getLogger("youtube_pipeline")

OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "/home/ec2-user/task/out"))
TEMP_DIR   = Path(os.getenv("TEMP_DIR",   "/home/ec2-user/task/tmp"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)

YOUTUBE_PUBLISH_MODE = os.getenv("YOUTUBE_PUBLISH_MODE", "SCHEDULE")
YOUTUBE_PUBLISH_HOUR = int(os.getenv("YOUTUBE_PUBLISH_HOUR", "6"))

TARGET_THEME      = os.getenv("TARGET_THEME", "auto")
VIDEO_DURATION_MIN = int(os.getenv("VIDEO_DURATION_MIN", "20"))
VIDEO_DURATION_MAX = int(os.getenv("VIDEO_DURATION_MAX", "25"))
LANGUAGE          = os.getenv("LANGUAGE", "ja")

GROQ_API_KEY    = os.getenv("GROQ_API_KEY", "")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
PEXELS_API_KEY  = os.getenv("PEXELS_API_KEY", "")
VOICEVOX_URL    = os.getenv("VOICEVOX_URL", "http://localhost:50021")

GROQ_MODEL = "llama-3.3-70b-versatile"

CHANNEL_NAME = os.getenv("CHANNEL_NAME", "マネー研究所")

REQUIRED_ENV_VARS = ["GROQ_API_KEY", "YOUTUBE_API_KEY", "PEXELS_API_KEY"]

VIDEO_AUTO_EDIT_PATH = Path("/home/ec2-user/task/03_PROJECTS/video_auto_edit/main.py")


# ============================================================
# ロギング設定
# ============================================================

def setup_logging(log_file: Optional[str] = None) -> logging.Logger:
    level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    formatter = logging.Formatter(
        fmt='[%(asctime)s] [%(levelname)s] %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    _logger = logging.getLogger("youtube_pipeline")
    _logger.setLevel(level)
    _logger.handlers.clear()
    _logger.addHandler(console_handler)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(log_path, encoding='utf-8')
        fh.setLevel(level)
        fh.setFormatter(formatter)
        _logger.addHandler(fh)
    return _logger


# ============================================================
# バリデーション
# ============================================================

def validate_env_vars() -> bool:
    missing = [v for v in REQUIRED_ENV_VARS if not os.getenv(v)]
    if missing:
        logger.error(f"❌ 必須環境変数が未設定: {', '.join(missing)}")
        return False
    logger.info("✅ 環境変数チェック完了")
    return True


def validate_dependencies() -> bool:
    required = ['groq', 'pydantic', 'requests', 'PIL', 'moviepy', 'google.auth']
    missing = []
    for mod in required:
        try:
            __import__(mod)
        except ImportError:
            missing.append(mod)
    if missing:
        logger.error(f"❌ 依存パッケージ不足: {', '.join(missing)}")
        return False
    logger.info("✅ 依存パッケージチェック完了")
    return True


# ============================================================
# Step 1: 企画エンジン — テーマ生成
# ============================================================

def generate_theme(theme_mode: str = "auto") -> dict:
    """Groq API でトレンドテーマを分析・生成"""
    client = Groq(api_key=GROQ_API_KEY)

    theme_map = {
        "auto":     "金融・テック・ビジネス から最もトレンドなジャンル",
        "finance":  "金融・投資・節約・家計管理",
        "tech":     "AI・テクノロジー・ガジェット",
        "business": "ビジネス・自己啓発・副業",
    }
    genre = theme_map.get(theme_mode, theme_map["auto"])

    prompt = f"""あなたはYouTubeチャンネル「{CHANNEL_NAME}」のプロデューサーです。
日本のサラリーマン向けに「{genre}」ジャンルの動画ネタを1つ提案してください。

【重要な条件】
- {VIDEO_DURATION_MIN}〜{VIDEO_DURATION_MAX}分の長尺動画を前提とすること
- 5セクション構成（導入→本題3パート→まとめ）で深掘り解説すること
- フックは視聴者が最初の5秒で「見なきゃ」と思う衝撃的な一文にすること
- 具体的な数字（金額・%・期間）を必ず含めること
- サムネイル映えする短いタイトル（20文字以内推奨）にすること

以下のJSON形式のみで出力してください（説明不要）:
{{
  "theme": "具体的な動画タイトル案（20文字以内・数字・意外性を含む）",
  "keywords": ["キーワード1", "キーワード2", "キーワード3", "キーワード4", "キーワード5"],
  "hook": "視聴者を引きつける衝撃的な最初の一言（数字入り・25文字以内）",
  "duration_min": {VIDEO_DURATION_MIN},
  "category": "{theme_mode if theme_mode != 'auto' else 'finance'}",
  "audience": "日本のサラリーマン"
}}"""

    resp = client.chat.completions.create(
        model=GROQ_MODEL,
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = resp.choices[0].message.content.strip()

    # JSON 抽出
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if match:
        return json.loads(match.group())

    raise ValueError(f"テーマ生成: JSON パース失敗\n{raw}")


# ============================================================
# Step 2: 台本生成
# ============================================================

def _groq_generate(client, prompt: str, max_tokens: int = 4096) -> str:
    """Groq API を呼び出してテキストを生成"""
    resp = client.chat.completions.create(
        model=GROQ_MODEL,
        max_tokens=max_tokens,
        temperature=0.9,
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.choices[0].message.content.strip()


def generate_script(theme: dict, language: str = "ja") -> str:
    """Groq Llama で YouTube 動画台本を5セクション別に生成（20-25分長尺対応）"""
    client = Groq(api_key=GROQ_API_KEY)

    theme_text = theme['theme']
    keywords = ', '.join(theme['keywords'])
    hook = theme['hook']
    audience = theme.get('audience', '日本のサラリーマン')
    duration = f"{VIDEO_DURATION_MIN}〜{VIDEO_DURATION_MAX}分"

    base_context = f"チャンネル名: {CHANNEL_NAME}\nテーマ: {theme_text}\nキーワード: {keywords}\n対象: {audience}\n動画尺: {duration}"

    # --- セクション1: フック + 導入（0:00〜3:00）≈400文字 ---
    logger.info("      📝 セクション1/5: フック+導入 生成中...")
    sec1 = _groq_generate(client, f"""あなたは視聴維持率の高いYouTubeクリエイターです。{duration}の長尺動画の台本の「フック」と「導入」パートを書いてください。

{base_context}
フック: {hook}

【最重要】冒頭15秒で視聴者を完全に掴むこと。離脱されたら終わり。
【文字数目安】合計500文字（読み上げ約3分）

以下の形式で出力してください:

## --- セクション 1: フック + 導入 ---

[フック — 0:00〜0:30]
冒頭の掴み。視聴者が「え？マジ？」と思う衝撃的な事実や数字から始める。
- 最初の1文は必ず具体的な数字を含めること
- 2文目で「この動画を見れば〜」と視聴の価値を明示
- 計3〜5文

[導入 — 0:30〜2:00]
テーマの背景・なぜ今このテーマが重要かを簡潔に説明。
- 「この動画では5つのポイントに分けて解説します」と全体像を予告
- 5〜8文

各文の末尾には「...」を付けて間を示してください。""")

    # --- セクション2: ポイント1〜2（3:00〜11:00）≈2400文字 ---
    logger.info("      📝 セクション2/5: ポイント1〜2 生成中...")
    sec2 = _groq_generate(client, f"""あなたは視聴維持率の高いYouTubeクリエイターです。{duration}の長尺動画の台本の本題（前半）を書いてください。

{base_context}

【文字数目安】合計1800文字（各ポイント900文字≒4-5分、合計約8-10分）

## --- セクション 2: ポイント1〜2 ---

【ポイント1: 基本・前提知識 — 3:00〜8:00】
- 初心者にもわかるように基礎から説明
- 具体的な数字やデータを5つ以上含める（金額、割合、期間など）
- 「例えば〜」で始まる具体例を3つ以上入れる
- 実際のケースを挙げて共感を得る
- 18文以上（約900文字）
- ★最後に次ポイントへの橋渡し

【ポイント2: 実践的なノウハウ — 8:00〜13:00】
- ステップバイステップで説明（3〜5ステップ）
- 成功事例と失敗事例を対比して具体的に解説
- 「よくある間違い」を3つ紹介
- 18文以上（約900文字）
- ★最後に「多くの人はここまでで満足しますが...」と煽り

各文の末尾には「...」を付けて間を示してください。
セクションタイトルは「ポイント1: 〇〇」の形式で出力してください。""", max_tokens=3000)

    # --- セクション3: ポイント3〜4（11:00〜19:00）≈2400文字 ---
    logger.info("      📝 セクション3/5: ポイント3〜4 生成中...")
    sec3 = _groq_generate(client, f"""あなたは視聴維持率の高いYouTubeクリエイターです。{duration}の長尺動画の台本の本題（後半）を書いてください。

{base_context}

【文字数目安】合計1800文字（各ポイント900文字≒4-5分、合計約8-10分）

## --- セクション 3: ポイント3〜4 ---

【ポイント3: 意外な落とし穴・注意点 — 13:00〜17:00】
- 多くの人が見落としがちなポイントを3つ紹介
- データや統計で裏付け（具体的な数字を5つ以上）
- 「実はこれが原因で〜」というストーリーで解説
- 18文以上（約900文字）
- ★最後に「ここからが本番です」

【ポイント4: 上級テクニック・差がつく方法 — 17:00〜21:00】
- 知っている人だけが得をする情報を3つ
- 具体的な比較表やケーススタディで詳しく解説
- 「プロが実際にやっている方法」として説得力を持たせる
- 18文以上（約900文字）
- ★最後に「最後のセクションでは実践アクションプランをお伝えします」

各文の末尾には「...」を付けて間を示してください。
セクションタイトルは「ポイント3: 〇〇」「ポイント4: 〇〇」の形式で出力してください。""", max_tokens=3000)

    # --- セクション4: ポイント5 — 実践アドバイス（19:00〜22:00）≈900文字 ---
    logger.info("      📝 セクション4/5: ポイント5 生成中...")
    sec4 = _groq_generate(client, f"""あなたは視聴維持率の高いYouTubeクリエイターです。{duration}の長尺動画の台本の実践パートを書いてください。

{base_context}

【文字数目安】約800文字（読み上げ約3-4分）

## --- セクション 4: ポイント5 実践アクション ---

【ポイント5: すぐに始められる実践アドバイス — 21:00〜24:00】
- 今日から始められる具体的なアクション5つ
- 各アクションの期待される効果（具体的な数字付き・「○週間で○%改善」等）
- 優先順位をつけて説明（最も簡単で効果が高いものから）
- 「まずはこれだけやってください」と1つだけ選んで強調
- 15文以上

各文の末尾には「...」を付けて間を示してください。""", max_tokens=3000)

    # --- セクション5: まとめ + CTA（22:00〜25:00）≈300文字 ---
    logger.info("      📝 セクション5/5: まとめ+CTA 生成中...")
    sec5 = _groq_generate(client, f"""あなたは視聴維持率の高いYouTubeクリエイターです。{duration}の長尺動画の台本の「まとめ」と「CTA」を書いてください。

{base_context}

【文字数目安】約400文字（読み上げ約2分）

## --- セクション 5: まとめ + CTA ---

[まとめ — 22:00〜24:00]
- 「では、今日お伝えした5つのポイントを振り返りましょう」で始める
- 5つのポイントを各1-2文で簡潔に整理
- 「この中で1つでも実践すれば、確実に結果が変わります」と励まし
- 10文以上

[CTA — 24:00〜25:00]
- 「{CHANNEL_NAME}では毎週このような動画を配信しています」
- 「この動画が参考になったら高評価とチャンネル登録をお願いします」
- 「コメント欄で一番参考になったポイント番号を教えてください」
- 次回の動画テーマの予告
- 5文以上

各文の末尾には「...」を付けて間を示してください。""")

    # 全セクションを結合
    full_script = f"{sec1}\n\n{sec2}\n\n{sec3}\n\n{sec4}\n\n{sec5}"
    lines = [l for l in full_script.split('\n') if l.strip()]
    char_count = sum(len(l) for l in lines)
    logger.info(f"      📊 台本合計: {len(lines)}行 / {char_count}文字（目標5000文字）")

    return full_script


# ============================================================
# Step 3: 音声生成（Kokoro TTS）
# ============================================================

def generate_voiceover(script: str, speaker_id: int = 3) -> str:
    """Kokoro TTS で高品質日本語音声を生成"""
    # 台本を文単位に分割
    lines = [l.strip() for l in script.split('\n') if l.strip()
             and not l.startswith('[') and not l.startswith('#')
             and not l.startswith('---') and len(l.strip()) > 2]

    if not lines:
        logger.warning("⚠️ 台本に有効な行がありません")
        return ""

    logger.info(f"   📝 音声化対象: {len(lines)}行")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # --- Kokoro TTS ---
    return _try_kokoro_tts(lines, timestamp)


def _try_kokoro_tts(lines: list, timestamp: str) -> str:
    """Kokoro ONNX で自然な日本語音声を生成"""
    import numpy as np

    # kokoro-onnx (Python 3.10+) を試行
    try:
        from kokoro_onnx import Kokoro
        import soundfile as sf
    except ImportError:
        # フォールバック: kokoro (PyTorch版)
        try:
            from kokoro import KPipeline
            import soundfile as sf
            return _try_kokoro_pytorch(lines, timestamp, KPipeline, sf)
        except ImportError:
            raise ImportError("kokoro-onnx も kokoro も未インストール")

    logger.info("   🎙️ Kokoro ONNX で音声生成中...")

    # モデルファイルパス
    model_dir = Path.home() / ".kokoro_onnx"
    model_dir.mkdir(exist_ok=True)
    model_file = model_dir / "kokoro-v1.0.int8.onnx"
    voices_file = model_dir / "voices-v1.0.bin"

    # モデルが未ダウンロードなら GitHub Releases からDL
    GH_BASE = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0"
    for fname, fpath in [("kokoro-v1.0.int8.onnx", model_file),
                         ("voices-v1.0.bin", voices_file)]:
        if not fpath.exists():
            logger.info(f"      📥 ダウンロード中: {fpath.name}...")
            resp = requests.get(f"{GH_BASE}/{fname}", timeout=600, allow_redirects=True)
            resp.raise_for_status()
            fpath.write_bytes(resp.content)
            logger.info(f"      ✅ {fpath.name} ({len(resp.content) // 1024 // 1024}MB)")

    kokoro = Kokoro(str(model_file), str(voices_file))

    all_audio = []
    sample_rate = 24000
    pause_samples = int(sample_rate * 0.4)
    pause = np.zeros(pause_samples, dtype=np.float32)

    # Kokoro ONNX は 510トークン上限。日本語は1文字≈3-5トークンなので30文字が安全圏
    def _split_text(text, max_chars=30):
        if len(text) <= max_chars:
            return [text]
        # 句読点で優先分割
        for sep in ['。', '、', '！', '？', '．', '，', '・']:
            if sep in text:
                parts = text.split(sep)
                chunks, cur = [], ""
                for p in parts:
                    piece = p + sep
                    if len(cur) + len(piece) > max_chars and cur:
                        chunks.append(cur)
                        cur = piece
                    else:
                        cur += piece
                if cur:
                    chunks.append(cur)
                result = []
                for c in [x.strip() for x in chunks if x.strip()]:
                    if len(c) > max_chars:
                        result.extend([c[j:j+max_chars] for j in range(0, len(c), max_chars)])
                    else:
                        result.append(c)
                return result
        return [text[j:j+max_chars] for j in range(0, len(text), max_chars)]

    def _kokoro_safe_create(kokoro_inst, text, max_chars=30):
        """トークン超過時に自動リトライ（さらに小さく分割）"""
        try:
            return kokoro_inst.create(text, voice='jf_alpha', speed=1.3, lang='ja')
        except (IndexError, Exception) as e:
            if "510" in str(e) or "out of bounds" in str(e):
                if len(text) > 15:
                    half = len(text) // 2
                    r1 = _kokoro_safe_create(kokoro_inst, text[:half], max_chars)
                    r2 = _kokoro_safe_create(kokoro_inst, text[half:], max_chars)
                    if r1 and r2:
                        return (np.concatenate([r1[0], r2[0]]), r1[1])
            raise

    for i, line in enumerate(lines):
        if i % 20 == 0:
            logger.info(f"      🔊 音声生成中... {i}/{len(lines)}行")
        sub_lines = _split_text(line)
        for sub in sub_lines:
            try:
                samples, sr = _kokoro_safe_create(kokoro, sub)
                all_audio.append(samples)
                sample_rate = sr
            except Exception as e:
                logger.warning(f"      ⚠️ 行{i}一部スキップ({len(sub)}字): {e}")
                continue
        all_audio.append(pause)

    if not all_audio:
        raise ValueError("音声データが生成されませんでした")

    wav_path = TEMP_DIR / f"voiceover_{timestamp}.wav"
    combined = np.concatenate(all_audio)
    sf.write(str(wav_path), combined, sample_rate)

    # WAV → MP3 変換
    output_path = TEMP_DIR / f"voiceover_{timestamp}.mp3"
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(wav_path), "-codec:a", "libmp3lame",
             "-qscale:a", "2", str(output_path)],
            check=True, capture_output=True, timeout=300
        )
        wav_path.unlink(missing_ok=True)
    except Exception:
        output_path = wav_path

    duration_sec = len(combined) / sample_rate
    logger.info(f"✅ Kokoro ONNX 音声生成完了: {output_path} ({duration_sec:.0f}秒)")
    return str(output_path)


def _try_kokoro_pytorch(lines, timestamp, KPipeline, sf):
    """Kokoro PyTorch版 フォールバック"""
    import numpy as np
    pipeline = KPipeline(lang_code='j')

    logger.info("   🎙️ Kokoro PyTorch で音声生成中...")
    all_audio = []
    sample_rate = 24000
    pause = np.zeros(int(sample_rate * 0.4), dtype=np.float32)

    for i, line in enumerate(lines):
        if i % 20 == 0:
            logger.info(f"      🔊 音声生成中... {i}/{len(lines)}行")
        try:
            for _, _, audio in pipeline(line, voice='jf_alpha', speed=1.3):
                all_audio.append(audio)
            all_audio.append(pause)
        except Exception as e:
            logger.warning(f"      ⚠️ 行{i}スキップ: {e}")

    if not all_audio:
        raise ValueError("音声データが生成されませんでした")

    wav_path = TEMP_DIR / f"voiceover_{timestamp}.wav"
    combined = np.concatenate(all_audio)
    sf.write(str(wav_path), combined, sample_rate)

    output_path = TEMP_DIR / f"voiceover_{timestamp}.mp3"
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(wav_path), "-codec:a", "libmp3lame",
             "-qscale:a", "2", str(output_path)],
            check=True, capture_output=True, timeout=300
        )
        wav_path.unlink(missing_ok=True)
    except Exception:
        output_path = wav_path

    duration_sec = len(combined) / sample_rate
    logger.info(f"✅ Kokoro PyTorch 音声生成完了: {output_path} ({duration_sec:.0f}秒)")
    return str(output_path)


# ============================================================
# Step 4: 映像素材収集
# ============================================================

def collect_footage(keywords: list, num_clips: int = 5) -> list:
    """Pexels API で映像素材を取得"""
    footage = []

    headers = {"Authorization": PEXELS_API_KEY}

    for keyword in keywords[:3]:
        try:
            resp = requests.get(
                "https://api.pexels.com/videos/search",
                headers=headers,
                params={"query": keyword, "per_page": 2, "orientation": "landscape"},
                timeout=30
            )
            resp.raise_for_status()
            data = resp.json()

            for video in data.get("videos", []):
                # HD以上のファイルを取得
                files = sorted(
                    [f for f in video.get("video_files", []) if f.get("quality") in ("hd", "sd")],
                    key=lambda x: x.get("width", 0),
                    reverse=True
                )
                if not files:
                    continue

                url = files[0]["link"]
                duration = video.get("duration", 10)

                # ダウンロード
                filename = TEMP_DIR / f"footage_{keyword}_{video['id']}.mp4"
                if not filename.exists():
                    dl = requests.get(url, timeout=60)
                    filename.write_bytes(dl.content)

                footage.append({"path": str(filename), "duration": duration, "type": "video"})
                logger.info(f"   📥 素材取得: {filename.name}")

        except Exception as e:
            logger.warning(f"⚠️ Pexels '{keyword}' 取得失敗: {e}")

    # 素材が足りない場合はインフォグラフィック生成
    if len(footage) < 3:
        logger.info("   🎨 素材不足 → インフォグラフィック生成へ")
        footage += generate_infographics({"keywords": keywords})

    return footage


def generate_infographics(theme: dict) -> list:
    """matplotlib で図解スライドを自動生成（ブランドカラー統一・7枚版）"""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches

    try:
        import matplotlib.font_manager as fm
        for font in ['Noto Sans CJK JP', 'IPAGothic', 'TakaoPGothic', 'DejaVu Sans']:
            if any(font.lower() in f.name.lower() for f in fm.fontManager.ttflist):
                plt.rcParams['font.family'] = font
                break
    except Exception:
        pass

    slides = []
    keywords = theme.get("keywords", ["AI", "節約", "自動化"])
    theme_title = theme.get("theme", "今週のトレンド")
    BG_DARK = '#0f0a1e'
    BRAND_YELLOW = '#FFCC00'
    BRAND_PURPLE = '#6432B4'

    point_colors = ['#ff6b6b', '#feca57', '#48dbfb', '#ff9ff3', '#54a0ff']
    point_labels = [
        "基本・前提知識",
        "実践的なノウハウ",
        "意外な落とし穴",
        "上級テクニック",
        "実践アクション",
    ]

    def _make_slide(filename, draw_func, duration=7.0):
        fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=100)
        fig.patch.set_facecolor(BG_DARK)
        ax.set_facecolor(BG_DARK)
        ax.axis('off')
        draw_func(fig, ax)
        path = TEMP_DIR / filename
        plt.savefig(str(path), bbox_inches='tight', facecolor=fig.get_facecolor())
        plt.close()
        slides.append({"path": str(path), "duration": duration, "type": "image"})

    # --- スライド1: タイトル + キーワード一覧 ---
    def _draw_title(fig, ax):
        rect_top = mpatches.FancyBboxPatch((0.0, 0.88), 1.0, 0.12,
                                            boxstyle="square", facecolor=BRAND_YELLOW,
                                            transform=ax.transAxes)
        ax.add_patch(rect_top)
        ax.text(0.5, 0.94, CHANNEL_NAME, color='black', fontsize=20,
                ha='center', va='center', fontweight='bold', transform=ax.transAxes)
        ax.text(0.5, 0.65, theme_title[:25],
                color='white', fontsize=32, ha='center', va='center',
                fontweight='bold', wrap=True, transform=ax.transAxes)
        for i, kw in enumerate(keywords[:5]):
            ax.text(0.5, 0.4 - i * 0.08, f"▶ {kw}",
                    color=BRAND_YELLOW, fontsize=16, ha='center',
                    transform=ax.transAxes)
    _make_slide("slide_title.png", _draw_title, 8.0)

    # --- スライド2: 5ポイント一覧 ---
    def _draw_overview(fig, ax):
        ax.text(0.5, 0.92, "今日の5つのポイント", color=BRAND_YELLOW, fontsize=28,
                ha='center', fontweight='bold', transform=ax.transAxes)
        for i in range(5):
            y = 0.75 - i * 0.14
            rect = mpatches.FancyBboxPatch((0.08, y - 0.05), 0.84, 0.10,
                                            boxstyle="round,pad=0.02",
                                            facecolor=point_colors[i], alpha=0.25,
                                            transform=ax.transAxes)
            ax.add_patch(rect)
            ax.text(0.15, y, f"{i+1}.", color=point_colors[i], fontsize=22,
                    ha='left', va='center', fontweight='bold', transform=ax.transAxes)
            ax.text(0.22, y, point_labels[i], color='white', fontsize=18,
                    ha='left', va='center', transform=ax.transAxes)
    _make_slide("slide_overview.png", _draw_overview, 8.0)

    # --- スライド3-7: 各ポイントの詳細スライド ---
    for p_idx in range(5):
        def _draw_point(fig, ax, idx=p_idx):
            color = point_colors[idx]
            label = point_labels[idx]
            kw = keywords[idx] if idx < len(keywords) else ""

            # 上部にポイント番号帯
            rect = mpatches.FancyBboxPatch((0.0, 0.85), 1.0, 0.15,
                                            boxstyle="square", facecolor=color,
                                            alpha=0.4, transform=ax.transAxes)
            ax.add_patch(rect)

            ax.text(0.5, 0.92, f"POINT {idx + 1}", color='white', fontsize=36,
                    ha='center', va='center', fontweight='bold', transform=ax.transAxes)

            # ポイントタイトル
            ax.text(0.5, 0.68, label, color='white', fontsize=28,
                    ha='center', va='center', fontweight='bold', transform=ax.transAxes)

            # キーワードとの関連
            if kw:
                ax.text(0.5, 0.52, f"#{kw}", color=BRAND_YELLOW, fontsize=22,
                        ha='center', va='center', transform=ax.transAxes)

            # 装飾的な要素（横線）
            ax.plot([0.2, 0.8], [0.42, 0.42], color=color, linewidth=2,
                    transform=ax.transAxes, alpha=0.5)

            # チェックマーク付きメッセージ
            messages = [
                "✓ 具体的な数字とデータ",
                "✓ 実践的なステップ",
                "✓ すぐに使えるノウハウ",
            ]
            for m_idx, msg in enumerate(messages):
                ax.text(0.5, 0.32 - m_idx * 0.08, msg, color='white',
                        fontsize=16, ha='center', va='center',
                        transform=ax.transAxes, alpha=0.8)

            # 下部バー
            rect_bot = mpatches.FancyBboxPatch((0.0, 0.0), 1.0, 0.08,
                                                boxstyle="square", facecolor=BRAND_PURPLE,
                                                transform=ax.transAxes)
            ax.add_patch(rect_bot)
            ax.text(0.5, 0.04, CHANNEL_NAME, color=BRAND_YELLOW, fontsize=14,
                    ha='center', va='center', fontweight='bold', transform=ax.transAxes)

        _make_slide(f"slide_point{p_idx + 1}.png", _draw_point, 7.0)

    # --- スライド8: まとめ（CTA付き）---
    def _draw_summary(fig, ax):
        ax.text(0.5, 0.85, "まとめ", color=BRAND_YELLOW, fontsize=36,
                ha='center', fontweight='bold', transform=ax.transAxes)

        # 5ポイントの振り返り（コンパクト版）
        for i in range(5):
            y = 0.68 - i * 0.10
            ax.text(0.15, y, f"✓ {i+1}.", color=point_colors[i], fontsize=18,
                    ha='left', va='center', fontweight='bold', transform=ax.transAxes)
            ax.text(0.22, y, point_labels[i], color='white', fontsize=16,
                    ha='left', va='center', transform=ax.transAxes)

        ax.text(0.5, 0.15, "1つでも実践すれば\n確実に結果が変わります！",
                color='white', fontsize=20, ha='center', va='center',
                linespacing=1.5, transform=ax.transAxes)

        rect_bottom = mpatches.FancyBboxPatch((0.0, 0.0), 1.0, 0.10,
                                               boxstyle="square", facecolor=BRAND_PURPLE,
                                               transform=ax.transAxes)
        ax.add_patch(rect_bottom)
        ax.text(0.5, 0.05, f"チャンネル登録 → {CHANNEL_NAME}",
                color=BRAND_YELLOW, fontsize=18, ha='center', va='center',
                fontweight='bold', transform=ax.transAxes)
    _make_slide("slide_summary.png", _draw_summary, 8.0)

    logger.info(f"   ✅ インフォグラフィック生成完了: {len(slides)}枚")
    return slides


# ============================================================
# Step 5: 動画編集
# ============================================================

def _wrap_japanese_text(text: str, max_chars: int = 22) -> list:
    """日本語テキストを句読点・区切りで自然に折り返す"""
    if len(text) <= max_chars:
        return [text]

    lines = []
    current = ""
    # 句読点で優先分割
    for char in text:
        current += char
        if len(current) >= max_chars:
            # 区切り文字を探す
            lines.append(current)
            current = ""
        elif char in '。、！？．，':
            if len(current) >= max_chars * 0.5:  # 半分以上書いたら改行
                lines.append(current)
                current = ""
    if current:
        lines.append(current)
    return lines[:4]  # 最大4行


def _create_section_header_image(section_title: str, point_num: int,
                                  theme: dict, size: tuple) -> 'Image':
    """セクション見出しスライドを生成（視覚的に目立つデザイン）"""
    from PIL import Image, ImageDraw

    BRAND_YELLOW = (255, 204, 0)
    BRAND_PURPLE = (100, 50, 180)
    BG_DARK = (15, 10, 30)

    img = Image.new("RGB", size, color=BG_DARK)
    draw = ImageDraw.Draw(img)

    # 上下にブランドカラー帯
    draw.rectangle([0, 0, size[0], 8], fill=BRAND_YELLOW)
    draw.rectangle([0, size[1] - 8, size[0], size[1]], fill=BRAND_YELLOW)

    # 中央にポイント番号の大きな円
    cx, cy = size[0] // 2, size[1] // 2 - 40
    radius = 80
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
                 fill=BRAND_YELLOW)
    font_num = _get_font(72)
    draw.text((cx, cy), str(point_num), font=font_num,
              fill=(10, 10, 10), anchor="mm")

    # セクションタイトル
    font_title = _get_font(48)
    title_display = section_title[:25]
    # 縁取り
    for dx in range(-3, 4):
        for dy in range(-3, 4):
            draw.text((cx + dx, cy + 120 + dy), title_display,
                      font=font_title, fill=(0, 0, 0), anchor="mm")
    draw.text((cx, cy + 120), title_display,
              font=font_title, fill=(255, 255, 255), anchor="mm")

    # 左下にテーマ名
    font_sm = _get_font(22)
    theme_name = theme.get("theme", "")[:30] if theme else ""
    draw.text((30, size[1] - 40), theme_name,
              font=font_sm, fill=(150, 150, 150), anchor="lm")

    # 右下にチャンネル名
    draw.text((size[0] - 30, size[1] - 40), CHANNEL_NAME,
              font=font_sm, fill=BRAND_YELLOW, anchor="rm")

    return img


def edit_video(footage: list, voiceover_path: str, script: str,
               output_path: str, timestamp: str, theme: dict = None) -> str:
    """moviepy で テロップ+単色背景+図解スライド+セクション見出し の動画を生成"""
    try:
        from moviepy.editor import (
            VideoFileClip, ImageClip, AudioFileClip,
            ColorClip, concatenate_videoclips, CompositeVideoClip
        )
        from PIL import Image, ImageDraw
    except ImportError:
        raise ImportError("moviepy/PIL が未インストールです")

    SIZE = (1280, 720)
    BRAND_YELLOW = (255, 204, 0)   # #FFCC00
    BRAND_PURPLE = (100, 50, 180)

    # セクションごとの背景色バリエーション（視覚的に変化をつける）
    SECTION_BG_COLORS = [
        (25, 25, 35),   # 濃紺（導入）
        (20, 30, 45),   # ダークブルー（ポイント1）
        (25, 25, 40),   # ダークパープル（ポイント2）
        (30, 25, 35),   # ダークマゼンタ（ポイント3）
        (25, 30, 30),   # ダークティール（ポイント4）
        (30, 25, 25),   # ダークレッド（ポイント5）
        (25, 25, 35),   # 濃紺（まとめ）
    ]

    # 音声の尺を基準にする（なければデフォルト）
    if voiceover_path and Path(voiceover_path).exists():
        audio = AudioFileClip(voiceover_path)
        target_duration = audio.duration
        logger.info(f"   📊 音声尺基準: {target_duration:.0f}秒")
    else:
        audio = None
        target_duration = 60 * VIDEO_DURATION_MIN

    # 台本を行単位で解析（セクション見出しと本文を分離）
    raw_lines = script.split('\n')
    parsed_items = []  # [{"type": "section"|"text", "text": str, "point_num": int, "section_idx": int}]
    current_section_idx = 0
    current_point_num = 0

    for line in raw_lines:
        stripped = line.strip()
        if not stripped or len(stripped) <= 2:
            continue

        # セクション見出しを検出
        if stripped.startswith('## ---') or stripped.startswith('## ─'):
            current_section_idx += 1
            continue

        # ポイント番号を検出
        point_match = re.match(r'(?:ポイント|Point)\s*(\d+)', stripped)
        if point_match:
            current_point_num = int(point_match.group(1))
            # ポイント見出し行
            title = re.sub(r'^(?:ポイント|Point)\s*\d+\s*[:：]?\s*', '', stripped).strip()
            if title and not title.startswith('[') and not title.startswith('#'):
                parsed_items.append({
                    "type": "section",
                    "text": title[:30],
                    "point_num": current_point_num,
                    "section_idx": current_section_idx
                })
            continue

        # メタ行をスキップ
        if stripped.startswith('[') or stripped.startswith('#') or stripped.startswith('---'):
            continue
        if stripped.startswith('- ') or stripped.startswith('★') or stripped.startswith('【'):
            continue

        # 通常テロップ行
        parsed_items.append({
            "type": "text",
            "text": stripped,
            "point_num": current_point_num,
            "section_idx": current_section_idx
        })

    if not parsed_items:
        parsed_items = [{"type": "text", "text": "テロップ準備中...",
                         "point_num": 0, "section_idx": 0}]

    # テロップ+セクション見出し以外の尺を計算
    section_header_count = sum(1 for p in parsed_items if p["type"] == "section")
    infographic_total_sec = sum(s.get("duration", 7.0) for s in footage) if footage else 0
    section_header_total_sec = section_header_count * 4.0  # 見出し1枚4秒
    text_total_sec = target_duration - infographic_total_sec - section_header_total_sec
    text_count = sum(1 for p in parsed_items if p["type"] == "text")
    sentence_duration = max(text_total_sec / max(text_count, 1), 2.0)

    logger.info(f"   🎬 テロップ生成中... (テキスト{text_count}枚 + 見出し{section_header_count}枚 + 図解{len(footage) if footage else 0}枚)")
    clips = []

    # 図解スライドの挿入位置（テキスト枚数の等分位置）
    infographic_positions = set()
    footage_copy = list(footage) if footage else []
    if footage_copy:
        interval = max(text_count // (len(footage_copy) + 1), 1)
        for idx in range(len(footage_copy)):
            pos = interval * (idx + 1)
            infographic_positions.add(pos)

    text_idx = 0
    for item in parsed_items:
        if item["type"] == "section":
            # セクション見出しスライド（4秒表示）
            header_img = _create_section_header_image(
                item["text"], item["point_num"], theme, SIZE
            )
            header_path = TEMP_DIR / f"header_{timestamp}_{item['point_num']:02d}.png"
            header_img.save(str(header_path))
            clips.append(ImageClip(str(header_path), duration=4.0))
            continue

        # 図解スライドの挿入タイミング
        if text_idx in infographic_positions and footage_copy:
            slide_item = footage_copy.pop(0)
            try:
                slide_clip = ImageClip(
                    slide_item["path"],
                    duration=slide_item.get("duration", 7.0)
                ).resize(SIZE)
                clips.append(slide_clip)
            except Exception as e:
                logger.warning(f"⚠️ スライド読み込み失敗: {e}")

        text_idx += 1

        # テロップ画像をPILで生成
        bg_color = SECTION_BG_COLORS[item["section_idx"] % len(SECTION_BG_COLORS)]
        img = Image.new("RGB", SIZE, color=bg_color)
        draw = ImageDraw.Draw(img)

        # 上部にポイント番号バー（現在のセクションを常時表示）
        bar_height = 50
        draw.rectangle([0, 0, SIZE[0], bar_height], fill=(15, 10, 25))
        draw.rectangle([0, bar_height - 3, SIZE[0], bar_height], fill=BRAND_YELLOW)

        font_bar = _get_font(22)
        point_label = f"POINT {item['point_num']}" if item['point_num'] > 0 else "INTRODUCTION"
        draw.text((30, bar_height // 2), point_label,
                  font=font_bar, fill=BRAND_YELLOW, anchor="lm")

        # ポイントインジケーター（5つの丸で進捗表示）
        for p in range(1, 6):
            px = SIZE[0] - 200 + p * 30
            py = bar_height // 2
            r = 8
            color = BRAND_YELLOW if p <= item['point_num'] else (60, 60, 80)
            draw.ellipse([px - r, py - r, px + r, py + r], fill=color)

        # チャンネル名（バー右端）
        draw.text((SIZE[0] - 30, bar_height // 2), CHANNEL_NAME,
                  font=font_bar, fill=(180, 180, 180), anchor="rm")

        # テロップテキスト（画面中央〜下部に配置）
        font = _get_font(46)
        display_text = item["text"][:80]
        text_lines = _wrap_japanese_text(display_text, max_chars=22)

        # テロップエリア: 画面の中央から下部
        y_start = SIZE[1] // 2 - len(text_lines) * 35 + 20
        for tl in text_lines:
            # 黒縁取り（3px）
            for dx in range(-3, 4):
                for dy in range(-3, 4):
                    if abs(dx) + abs(dy) > 4:
                        continue
                    draw.text((SIZE[0] // 2 + dx, y_start + dy), tl,
                              font=font, fill=(0, 0, 0), anchor="mm")
            draw.text((SIZE[0] // 2, y_start), tl,
                      font=font, fill=(255, 255, 255), anchor="mm")
            y_start += 60

        # 下部にうすい紫バー
        draw.rectangle([0, SIZE[1] - 5, SIZE[0], SIZE[1]], fill=BRAND_PURPLE)

        # PIL → ImageClip
        telop_path = TEMP_DIR / f"telop_{timestamp}_{text_idx:04d}.png"
        img.save(str(telop_path))
        clip = ImageClip(str(telop_path), duration=sentence_duration)
        clips.append(clip)

    # 残りの図解スライドを末尾に追加
    for slide_item in footage_copy:
        try:
            slide_clip = ImageClip(
                slide_item["path"],
                duration=slide_item.get("duration", 7.0)
            ).resize(SIZE)
            clips.append(slide_clip)
        except Exception:
            pass

    if not clips:
        raise ValueError("有効なクリップがありません")

    # 結合
    video = concatenate_videoclips(clips, method="compose")

    # 音声合成
    if audio:
        if audio.duration > video.duration:
            audio = audio.subclip(0, video.duration)
        video = video.set_audio(audio)

    # SRT 字幕生成
    srt_path = TEMP_DIR / f"subtitles_{timestamp}.srt"
    _generate_srt(script, str(srt_path), video.duration)

    # 出力
    video.write_videofile(
        output_path,
        fps=30,
        codec='libx264',
        audio_codec='aac',
        logger=None,
        threads=2  # t4g.medium 2vCPU 対応
    )

    # テロップ・ヘッダー一時ファイル削除
    for f in TEMP_DIR.glob(f"telop_{timestamp}_*.png"):
        f.unlink(missing_ok=True)
    for f in TEMP_DIR.glob(f"header_{timestamp}_*.png"):
        f.unlink(missing_ok=True)

    logger.info(f"✅ 動画出力: {output_path} ({video.duration:.0f}秒)")
    return output_path


def _generate_srt(script: str, srt_path: str, total_duration: float):
    """台本から SRT 字幕ファイルを生成"""
    lines = [l.strip() for l in script.split('\n')
             if l.strip() and not l.startswith('[')]
    if not lines:
        return

    interval = total_duration / max(len(lines), 1)
    srt_content = ""

    for i, line in enumerate(lines):
        start = i * interval
        end = (i + 1) * interval
        srt_content += f"{i+1}\n"
        srt_content += f"{_fmt_time(start)} --> {_fmt_time(end)}\n"
        srt_content += f"{line}\n\n"

    Path(srt_path).write_text(srt_content, encoding='utf-8')


def _fmt_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


# ============================================================
# フォントヘルパー（サムネイル・テロップ共通）
# ============================================================

def _get_font(size: int):
    """日本語対応フォントを検索して返す（ARM/x86 両対応）"""
    from PIL import ImageFont
    font_paths = [
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/google-noto-cjk/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for fp in font_paths:
        try:
            return ImageFont.truetype(fp, size)
        except Exception:
            continue
    return ImageFont.load_default()


# ============================================================
# Step 6: サムネイル生成
# ============================================================

def generate_thumbnail(theme: dict, output_path: str) -> str:
    """PIL サムネイル生成 — ブランド統一版（黄帯+96pt大文字+キーワード帯）"""
    from PIL import Image, ImageDraw

    width, height = 1280, 720

    # ブランドカラー定数
    BRAND_YELLOW = (255, 204, 0)     # #FFCC00
    BRAND_PURPLE = (100, 50, 180)    # #6432B4
    BG_DARK      = (15, 10, 30)      # 濃紺ベース
    WHITE        = (255, 255, 255)
    BLACK        = (10, 10, 10)

    img = Image.new("RGB", (width, height), color=BG_DARK)
    draw = ImageDraw.Draw(img)

    # --- 上部: 黄色帯（フック文表示エリア）---
    draw.rectangle([0, 0, width, 120], fill=BRAND_YELLOW)

    # --- 下部: 紫帯（キーワード + チャンネル名）---
    draw.rectangle([0, height - 80, width, height], fill=BRAND_PURPLE)

    # フォント
    font_xl = _get_font(96)    # メインタイトル
    font_lg = _get_font(48)    # フック文
    font_md = _get_font(36)    # キーワード
    font_sm = _get_font(28)    # チャンネル名

    # --- フック文（黄色帯内・黒文字）---
    hook = theme.get("hook", "")
    if hook:
        hook_display = hook[:25] + ("..." if len(hook) > 25 else "")
        draw.text((width // 2, 60), hook_display,
                  font=font_lg, fill=BLACK, anchor="mm")

    # --- メインタイトル（中央・白文字+5px黒縁取り）---
    title = theme.get("theme", "今週の注目テーマ")
    # 8-10文字で改行（サムネ視認性のため短く）
    max_chars_per_line = 10
    if len(title) > max_chars_per_line * 2:
        chunk = max_chars_per_line
        title_lines = [title[:chunk], title[chunk:chunk*2], title[chunk*2:chunk*3]]
    elif len(title) > max_chars_per_line:
        mid = len(title) // 2
        title_lines = [title[:mid], title[mid:]]
    else:
        title_lines = [title]

    line_height = 110
    y_center = height // 2 + 10
    y_start = y_center - len(title_lines) * line_height // 2

    for line in title_lines:
        # 5px 縁取り（黒）
        for dx in range(-5, 6):
            for dy in range(-5, 6):
                if abs(dx) + abs(dy) > 7:
                    continue
                draw.text((width // 2 + dx, y_start + dy), line,
                          font=font_xl, fill=BLACK, anchor="mm")
        # 本文（白）
        draw.text((width // 2, y_start), line,
                  font=font_xl, fill=WHITE, anchor="mm")
        y_start += line_height

    # --- 下部紫帯: キーワード + チャンネル名 ---
    keywords = theme.get("keywords", [])[:3]
    kw_text = "  ".join([f"#{k}" for k in keywords])
    draw.text((40, height - 45), kw_text,
              font=font_md, fill=WHITE, anchor="lm")

    # チャンネル名（右寄せ）
    draw.text((width - 40, height - 45), CHANNEL_NAME,
              font=font_sm, fill=BRAND_YELLOW, anchor="rm")

    img.save(output_path, "PNG", quality=95)
    logger.info(f"✅ サムネイル生成完了: {output_path}")
    return output_path


# ============================================================
# Step 7: メタデータ最適化
# ============================================================

def _generate_chapters(script: str) -> str:
    """台本からYouTubeチャプター用タイムスタンプを生成"""
    chapters = ["0:00 はじめに"]

    # セクションヘッダーを検出してチャプター化
    section_patterns = [
        (r'\[フック', '0:00 オープニング'),
        (r'\[導入', '0:30 導入'),
        (r'ポイント1[:：]?\s*(.+)', '3:00 {}'),
        (r'ポイント2[:：]?\s*(.+)', '7:00 {}'),
        (r'ポイント3[:：]?\s*(.+)', '11:00 {}'),
        (r'ポイント4[:：]?\s*(.+)', '15:00 {}'),
        (r'ポイント5[:：]?\s*(.+)', '19:00 {}'),
        (r'\[まとめ', '22:00 まとめ'),
    ]

    chapters = []
    for pattern, template in section_patterns:
        match = re.search(pattern, script)
        if match:
            if '{}' in template and match.groups():
                title = match.group(1).strip().rstrip('...。、')[:20]
                chapters.append(template.format(title))
            else:
                chapters.append(template)

    if not chapters:
        # フォールバック: 基本チャプター（5セクション対応）
        chapters = [
            "0:00 はじめに",
            "0:30 導入",
            "3:00 ポイント1",
            "7:00 ポイント2",
            "11:00 ポイント3",
            "15:00 ポイント4",
            "19:00 ポイント5",
            "22:00 まとめ",
        ]

    return "\n".join(chapters)


def optimize_metadata(theme: dict, script: str) -> dict:
    """Groq で YouTube SEO メタデータを生成（CTR+SEO最適化版）"""
    client = Groq(api_key=GROQ_API_KEY)

    chapters = _generate_chapters(script)

    prompt = f"""あなたはYouTube SEOの専門家です。
以下の動画について、検索・クリック率を最大化するメタデータを生成してください。

テーマ: {theme['theme']}
キーワード: {', '.join(theme.get('keywords', []))}
対象: {theme.get('audience', '日本のサラリーマン')}
動画尺: {VIDEO_DURATION_MIN}〜{VIDEO_DURATION_MAX}分

【タイトルのルール — 最重要】
- メインキーワードを最初の40文字以内に配置すること
- 【】で囲んだパワーワードを冒頭に入れる（例: 【衝撃】【知らないと損】【完全版】）
- 数字を必ず含める（3つの方法、5つのステップ、87%の人が〜等）
- 疑問形 or 断定形で書く
- 50文字以内
- 良い例: 「【知らないと損】月5万円の不労所得を作る3つの方法」「【2026年版】なぜサラリーマンの9割が投資で失敗するのか」
- 悪い例: 「投資 お金儲け 資産運用」「節約 貯金 方法 おすすめ」

【説明文のルール — SEO重視】
- 最初の150文字が「もっと見る」の前に表示される → ここにキーワードと価値提案を凝縮
- 1行目: 動画の結論（何が学べるか）を1文で
- 2行目: 対象者（「〜な方は必見です」）
- 3行目以降: 動画の内容概要
- 末尾にチャプターを含める
- 合計300-500文字

以下のJSON形式のみで出力してください:
{{
  "title": "【パワーワード】メインキーワード入りタイトル（50文字以内）",
  "description_main": "150文字以内の要約（もっと見る前に表示される部分）",
  "description_detail": "残りの説明文（150-300文字）",
  "tags": ["メインKW", "関連KW1", ..., "タグ15（最大）"],
  "category": "Education"
}}"""

    resp = client.chat.completions.create(
        model=GROQ_MODEL,
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = resp.choices[0].message.content.strip()

    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if match:
        meta = json.loads(match.group())

        # タイトル制限
        title = meta.get("title", theme["theme"])[:50]

        # 説明文組み立て（SEOテンプレ）
        desc_main = meta.get("description_main", "")
        desc_detail = meta.get("description_detail", "")
        description = _build_description(desc_main, desc_detail, chapters, theme)

        # タグ（カテゴリ別ベース + AI生成タグ）
        base_tags = _get_category_tags(theme.get("category", "finance"))
        ai_tags = meta.get("tags", [])[:10]
        all_tags = list(dict.fromkeys(ai_tags + base_tags))[:15]  # 重複排除・15個上限

        return {
            "title": title,
            "description": description,
            "tags": all_tags,
            "category": meta.get("category", "Education")
        }

    # フォールバック
    fallback_desc = _build_description(
        f"{theme['theme']}について徹底解説します。",
        f"この動画では5つのポイントに分けて、{theme.get('audience', '日本のサラリーマン')}向けに詳しく解説しています。",
        chapters, theme
    )
    return {
        "title": theme["theme"][:50],
        "description": fallback_desc,
        "tags": theme.get("keywords", []) + _get_category_tags("finance"),
        "category": "Education"
    }


def _build_description(main: str, detail: str, chapters: str, theme: dict) -> str:
    """YouTube説明文のテンプレート組み立て"""
    keywords = theme.get("keywords", [])
    kw_text = " ".join([f"#{k}" for k in keywords[:5]])

    description = f"""{main}

{detail}

━━━━━━━━━━━━━━━━━━━━━━
📋 目次（チャプター）
━━━━━━━━━━━━━━━━━━━━━━
{chapters}

━━━━━━━━━━━━━━━━━━━━━━
{kw_text}

🔔 チャンネル登録はこちら → {CHANNEL_NAME}で検索！
👍 高評価・コメントで応援お願いします！

⚠️ この動画の一部はAI技術を活用して制作しています。
情報の正確性には注意を払っていますが、投資判断は自己責任でお願いします。
最新の正確な情報は公式ソースをご確認ください。"""

    return description.strip()


def _get_category_tags(category: str) -> list:
    """カテゴリ別ベースタグ"""
    tag_templates = {
        "finance": ["投資", "資産運用", "節約", "お金", "サラリーマン", "不労所得", "NISA", "副業"],
        "tech": ["AI", "テクノロジー", "最新技術", "ガジェット", "プログラミング", "IT", "ChatGPT"],
        "business": ["ビジネス", "自己啓発", "副業", "起業", "キャリア", "スキルアップ", "転職"],
    }
    return tag_templates.get(category, tag_templates["finance"])


# ============================================================
# Step 8: YouTube アップロード
# ============================================================

def upload_to_youtube(video_path: str, metadata: dict,
                      thumbnail_path: str,
                      publish_mode: str = "SCHEDULE") -> str:
    """YouTube Data API v3 で動画をアップロード（トークンファイル方式・EC2対応）"""
    try:
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        from google.oauth2.credentials import Credentials
        import google.auth.transport.requests
    except ImportError:
        raise ImportError("google-api-python-client が未インストールです")

    SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

    # トークンファイルパス（環境変数 or デフォルト）
    TOKEN_FILE = Path(os.getenv(
        "YOUTUBE_TOKEN_FILE",
        "/home/ec2-user/task/03_PROJECTS/youtube_automation/token.json"
    ))

    # トークン読み込み
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
        logger.info(f"   📄 トークン読み込み: {TOKEN_FILE}")
    else:
        raise FileNotFoundError(
            f"token.json が見つかりません: {TOKEN_FILE}\n"
            "ローカルPCで generate_token.py を実行してトークンを生成し、\n"
            "EC2 に SCP でコピーしてください:\n"
            "  [ローカル] python generate_token.py\n"
            "  [ローカル] scp token.json ec2-user@<EC2_IP>:{TOKEN_FILE}"
        )

    # トークンリフレッシュ
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            logger.info("   🔄 トークンをリフレッシュ中...")
            creds.refresh(google.auth.transport.requests.Request())
            TOKEN_FILE.write_text(creds.to_json())
            logger.info("   ✅ トークンリフレッシュ完了")
        else:
            raise RuntimeError(
                "トークンが無効で、リフレッシュトークンもありません。\n"
                "ローカルPCで generate_token.py を再実行してください。"
            )

    youtube = build("youtube", "v3", credentials=creds)

    # 公開設定
    jst = timezone(timedelta(hours=9))
    if publish_mode == "SCHEDULE":
        publish_at = (datetime.now(jst) + timedelta(days=1)).replace(
            hour=YOUTUBE_PUBLISH_HOUR, minute=0, second=0, microsecond=0
        )
        status = {
            "privacyStatus": "private",
            "publishAt": publish_at.isoformat()
        }
    elif publish_mode == "PUBLIC":
        status = {"privacyStatus": "public"}
    else:
        status = {"privacyStatus": "private"}

    # 動画アップロード
    body = {
        "snippet": {
            "title":       metadata.get("title", "動画タイトル"),
            "description": metadata.get("description", ""),
            "tags":        metadata.get("tags", []),
            "categoryId":  "22",  # Education
        },
        "status": status
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    response = None
    logger.info("   🔄 アップロード中...")
    while response is None:
        _, response = request.next_chunk()

    video_id = response["id"]
    logger.info(f"   ✅ アップロード完了: https://www.youtube.com/watch?v={video_id}")

    # サムネイル設定
    if thumbnail_path and Path(thumbnail_path).exists():
        try:
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path)
            ).execute()
            logger.info("   ✅ サムネイル設定完了")
        except Exception as e:
            logger.warning(f"⚠️ サムネイル設定失敗: {e}")

    return video_id


# ============================================================
# パイプライン本体
# ============================================================

class YouTubeAutomationPipeline:
    """YouTube自動化パイプラインの主処理"""

    def __init__(self, theme_mode: str = "auto"):
        self.theme_mode = theme_mode
        self.timestamp  = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.edit_log   = {
            "timestamp": datetime.now().isoformat(),
            "theme_mode": theme_mode,
            "steps": [],
            "output": {}
        }
        # ステップ間のデータ共有
        self.theme:          Optional[dict] = None
        self.script:         Optional[str]  = None
        self.voiceover_path: Optional[str]  = None
        self.footage:        Optional[list] = None
        self.video_path:     Optional[str]  = None
        self.thumbnail_path: Optional[str]  = None
        self.metadata:       Optional[dict] = None

    def run(self) -> bool:
        logger.info("=" * 60)
        logger.info("🎬 YouTube自動化パイプラインを開始します")
        logger.info("=" * 60)

        steps = [
            ("Step 1: Theme Generation",    self._step_generate_theme),
            ("Step 2: Script Generation",   self._step_generate_script),
            ("Step 3: Voiceover Generation",self._step_generate_voiceover),
            ("Step 4: Footage Collection",  self._step_collect_footage),
            ("Step 5: Video Editing",       self._step_edit_video),
            ("Step 6: Thumbnail Generation",self._step_generate_thumbnail),
            ("Step 7: Metadata Optimization",self._step_optimize_metadata),
            ("Step 8: YouTube Upload",      self._step_upload_to_youtube),
        ]

        start_time = datetime.now()

        for step_name, step_func in steps:
            try:
                logger.info(f"\n📋 {step_name}")
                step_func()
                self._log_step(step_name, "success")
            except Exception as e:
                logger.error(f"❌ {step_name} に失敗: {str(e)}")
                logger.debug(traceback.format_exc())
                self._log_step(step_name, "failed", error=str(e))
                if self._should_stop_on_error(step_name):
                    logger.error("🛑 重要ステップ失敗のため中止")
                    return False

        elapsed = (datetime.now() - start_time).total_seconds()
        self.edit_log["total_duration_sec"] = elapsed

        logger.info("\n" + "=" * 60)
        logger.info(f"✅ パイプライン完了！！ ({elapsed:.0f}秒)")
        logger.info("=" * 60)

        self._save_edit_log()
        return True

    # ----------------------------------------------------------
    # Step 1
    # ----------------------------------------------------------
    def _step_generate_theme(self):
        logger.info("   🔄 Groq でトレンド分析中...")
        self.theme = generate_theme(self.theme_mode)
        logger.info(f"   ✅ テーマ決定: {self.theme['theme']}")
        logger.info(f"   📌 キーワード: {', '.join(self.theme['keywords'])}")

    # ----------------------------------------------------------
    # Step 2
    # ----------------------------------------------------------
    def _step_generate_script(self):
        if not self.theme:
            raise ValueError("テーマが未生成です")
        logger.info("   🔄 Groq で台本生成中...")
        self.script = generate_script(self.theme, LANGUAGE)
        lines = len([l for l in self.script.split('\n') if l.strip()])
        logger.info(f"   ✅ 台本生成完了 ({lines}行)")

    # ----------------------------------------------------------
    # Step 3
    # ----------------------------------------------------------
    def _step_generate_voiceover(self):
        if not self.script:
            raise ValueError("台本が未生成です")
        logger.info("   🔄 VOICEVOX で音声生成中...")
        self.voiceover_path = generate_voiceover(self.script)
        if self.voiceover_path:
            logger.info(f"   ✅ 音声生成完了: {self.voiceover_path}")
        else:
            logger.warning("   ⚠️ 音声生成スキップ（VOICEVOX 未起動）")

    # ----------------------------------------------------------
    # Step 4
    # ----------------------------------------------------------
    def _step_collect_footage(self):
        if not self.theme:
            raise ValueError("テーマが未生成です")
        logger.info("   🔄 図解スライド生成中（v3: テロップ+単色背景方式）...")
        # v3: Pexels映像は不要。テロップ+単色背景+図解スライドで構成
        self.footage = generate_infographics(self.theme)
        logger.info(f"   ✅ 図解スライド生成完了: {len(self.footage)}枚")

    # ----------------------------------------------------------
    # Step 5
    # ----------------------------------------------------------
    def _step_edit_video(self):
        if not self.footage:
            raise ValueError("映像素材が未収集です")
        logger.info("   🔄 moviepy で動画編集中（テロップ+単色背景）...")
        output_path = str(OUTPUT_DIR / f"final_{self.timestamp}.mp4")
        self.video_path = edit_video(
            footage=self.footage,
            voiceover_path=self.voiceover_path or "",
            script=self.script or "",
            output_path=output_path,
            timestamp=self.timestamp,
            theme=self.theme
        )
        self.edit_log["output"]["video"] = self.video_path
        logger.info(f"   ✅ 動画編集完了: {self.video_path}")

    # ----------------------------------------------------------
    # Step 6
    # ----------------------------------------------------------
    def _step_generate_thumbnail(self):
        if not self.theme:
            raise ValueError("テーマが未生成です")
        logger.info("   🔄 PIL でサムネイル生成中...")
        thumbnail_path = str(OUTPUT_DIR / f"thumbnail_{self.timestamp}.png")
        self.thumbnail_path = generate_thumbnail(self.theme, thumbnail_path)
        self.edit_log["output"]["thumbnail"] = self.thumbnail_path

    # ----------------------------------------------------------
    # Step 7
    # ----------------------------------------------------------
    def _step_optimize_metadata(self):
        if not self.theme or not self.script:
            raise ValueError("テーマまたは台本が未生成です")
        logger.info("   🔄 Groq でメタデータ最適化中...")
        self.metadata = optimize_metadata(self.theme, self.script)
        metadata_path = OUTPUT_DIR / f"metadata_{self.timestamp}.json"
        metadata_path.write_text(
            json.dumps(self.metadata, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
        self.edit_log["output"]["metadata"] = str(metadata_path)
        logger.info(f"   ✅ タイトル: {self.metadata['title']}")
        logger.info(f"   ✅ タグ数: {len(self.metadata.get('tags', []))}個")

    # ----------------------------------------------------------
    # Step 8
    # ----------------------------------------------------------
    def _step_upload_to_youtube(self):
        if not self.video_path or not Path(self.video_path).exists():
            raise ValueError("動画ファイルが存在しません")
        if not self.metadata:
            raise ValueError("メタデータが未生成です")
        logger.info("   🔄 YouTube にアップロード中...")
        video_id = upload_to_youtube(
            video_path=self.video_path,
            metadata=self.metadata,
            thumbnail_path=self.thumbnail_path or "",
            publish_mode=YOUTUBE_PUBLISH_MODE
        )
        self.edit_log["output"]["video_id"] = video_id
        self.edit_log["output"]["youtube_url"] = f"https://www.youtube.com/watch?v={video_id}"

    # ----------------------------------------------------------
    # ユーティリティ
    # ----------------------------------------------------------
    def _log_step(self, step_name: str, status: str, error: Optional[str] = None):
        self.edit_log["steps"].append({
            "step": step_name,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            **({"error": error} if error else {})
        })

    def _should_stop_on_error(self, step_name: str) -> bool:
        critical = [
            "Step 1: Theme Generation",
            "Step 2: Script Generation",
            "Step 5: Video Editing",
        ]
        return step_name in critical

    def _save_edit_log(self):
        log_file = OUTPUT_DIR / f"edit_log_{self.timestamp}.json"
        log_file.write_text(
            json.dumps(self.edit_log, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
        logger.info(f"✅ ログ保存: {log_file}")
        self.edit_log["output"]["log"] = str(log_file)


# ============================================================
# メイン処理
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="YouTube自動化パイプライン",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
例:
  python3 youtube_pipeline.py --theme auto
  python3 youtube_pipeline.py --theme finance --output /home/ec2-user/task/out
  python3 youtube_pipeline.py --theme tech --log-file /home/ec2-user/task/pipeline.log
        """
    )
    parser.add_argument("--theme", type=str, default=TARGET_THEME,
                        choices=["auto", "finance", "tech", "business"])
    parser.add_argument("--output", type=str, default=str(OUTPUT_DIR))
    parser.add_argument("--log-file", type=str, default=None)
    parser.add_argument("--count", type=int, default=1,
                        help="生成する動画の本数（デフォルト: 1）")
    args = parser.parse_args()

    global logger
    logger = setup_logging(args.log_file)

    logger.info("🚀 YouTube自動化パイプライン v4.0 — マネー研究所（Kokoro TTS専用）")
    logger.info(f"   Python: {sys.version.split()[0]}")
    logger.info(f"   テーマモード: {args.theme}")
    logger.info(f"   生成本数: {args.count}")
    logger.info(f"   動画尺: {VIDEO_DURATION_MIN}〜{VIDEO_DURATION_MAX}分")

    if not validate_dependencies():
        return 1
    if not validate_env_vars():
        return 1

    success_count = 0
    fail_count = 0

    for i in range(args.count):
        logger.info(f"\n{'🎬' * 20}")
        logger.info(f"🎬 動画 [{i + 1}/{args.count}] 開始")
        logger.info(f"{'🎬' * 20}")

        try:
            pipeline = YouTubeAutomationPipeline(theme_mode=args.theme)
            success = pipeline.run()
            if success:
                success_count += 1
            else:
                fail_count += 1
        except Exception as e:
            logger.error(f"❌ 動画 [{i + 1}/{args.count}] 予期しないエラー: {str(e)}")
            logger.debug(traceback.format_exc())
            fail_count += 1

        # 次の動画との間にクールダウン（API レート制限対策）
        if i < args.count - 1:
            cooldown = 10
            logger.info(f"⏳ クールダウン {cooldown}秒...")
            time.sleep(cooldown)

    # バッチサマリー
    logger.info(f"\n{'=' * 60}")
    logger.info(f"📊 バッチ完了: {success_count}/{args.count} 成功, {fail_count} 失敗")
    logger.info(f"{'=' * 60}")

    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
