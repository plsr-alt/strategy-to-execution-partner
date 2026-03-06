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
VIDEO_DURATION_MIN = int(os.getenv("VIDEO_DURATION_MIN", "30"))
VIDEO_DURATION_MAX = int(os.getenv("VIDEO_DURATION_MAX", "35"))
LANGUAGE          = os.getenv("LANGUAGE", "ja")

GROQ_API_KEY    = os.getenv("GROQ_API_KEY", "")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
PEXELS_API_KEY  = os.getenv("PEXELS_API_KEY", "")
VOICEVOX_URL    = os.getenv("VOICEVOX_URL", "http://localhost:50021")

GROQ_MODEL = "llama-3.3-70b-versatile"

REQUIRED_ENV_VARS = ["GROQ_API_KEY", "YOUTUBE_API_KEY", "PEXELS_API_KEY", "VOICEVOX_URL"]

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

    prompt = f"""あなたはYouTubeチャンネルのプロデューサーです。
日本のサラリーマン向けに「{genre}」ジャンルの動画ネタを1つ提案してください。

【重要な条件】
- 15〜20分の長尺動画を前提とすること
- 深掘り解説・実践的ノウハウを含む構成にすること
- フックは視聴者が最初の5秒で「見なきゃ」と思う衝撃的な一文にすること
- 具体的な数字（金額・%・期間）を必ず含めること

以下のJSON形式のみで出力してください（説明不要）:
{{
  "theme": "具体的な動画タイトル案（数字・意外性を含む）",
  "keywords": ["キーワード1", "キーワード2", "キーワード3", "キーワード4", "キーワード5"],
  "hook": "視聴者を引きつける衝撃的な最初の一言（数字入り）",
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
    """Groq Llama で YouTube 動画台本をセクション別に生成（15-20分長尺対応）"""
    client = Groq(api_key=GROQ_API_KEY)

    theme_text = theme['theme']
    keywords = ', '.join(theme['keywords'])
    hook = theme['hook']
    audience = theme.get('audience', '日本のサラリーマン')
    duration = f"{VIDEO_DURATION_MIN}〜{VIDEO_DURATION_MAX}分"

    base_context = f"テーマ: {theme_text}\nキーワード: {keywords}\n対象: {audience}\n動画尺: {duration}"

    # --- セクション1: フック + 導入（0:00〜3:00） ---
    logger.info("      📝 セクション1/4: フック+導入 生成中...")
    sec1 = _groq_generate(client, f"""あなたは視聴維持率の高いYouTubeクリエイターです。{duration}の長尺動画の台本の「フック」と「導入」パートを書いてください。

{base_context}
フック: {hook}

【最重要】冒頭15秒で視聴者を完全に掴むこと。離脱されたら終わり。

以下の形式で出力してください:

[フック — 0:00〜0:30]
冒頭の掴み。視聴者が「え？マジ？」と思う衝撃的な事実や数字から始める。
- 最初の1文は必ず具体的な数字を含めること（例: 「日本人の87%が知らない〜」）
- 2文目で「この動画を見れば〜」と視聴の価値を明示
- 3-5文で「でも実は〜」と意外な展開をチラ見せ
- 計5〜8文

[導入 — 0:30〜3:00]
テーマの背景・なぜ今このテーマが重要かを詳しく説明。
- 最新の2025-2026年のデータや社会的背景を含める
- 「この動画では5つのポイントに分けて徹底解説します」と全体像を予告
- 各ポイントの見出しを予告して「全部見てほしい」と促す
- 15文以上

各文の末尾には「...」を付けて間を示してください。""")

    # --- セクション2: ポイント1〜3（3:00〜12:00） ---
    logger.info("      📝 セクション2/4: ポイント1〜3 生成中...")
    sec2 = _groq_generate(client, f"""あなたは視聴維持率の高いYouTubeクリエイターです。{duration}の長尺動画の台本の本題（前半）を書いてください。

{base_context}

以下の3つのポイントを、それぞれ詳しく解説してください。
各ポイントは3〜4分の尺になるよう、20文以上で具体的に書いてください。

【ポイント1: 基本・前提知識 — 3:00〜6:00】
- 初心者にもわかるように基礎から説明
- 具体的な数字やデータを3つ以上含める
- 「例えば〜」で始まる具体例を2つ以上入れる
- 20文以上
- ★最後に「ここまでが基本ですが、次のポイント2ではさらに実践的な内容に踏み込みます」と次への橋渡し

【ポイント2: 実践的なノウハウ — 6:00〜9:00】
- ステップバイステップで説明
- 成功事例と失敗事例を対比
- 「ここが重要なんですが〜」のような強調表現を使う
- 20文以上
- ★最後に「多くの人はここまでで満足しますが、次のポイント3を知らないと大損します」と煽り

【ポイント3: 意外な落とし穴・注意点 — 9:00〜12:00】
- 多くの人が見落としがちなポイント
- データや統計で裏付け
- 「実は〜」「意外にも〜」で始まる意外性のある情報
- 20文以上
- ★最後に「ここからが本番です。ポイント4では上級者向けの裏技をお伝えします」

各文の末尾には「...」を付けて間を示してください。
セクションタイトルは「ポイント1: 〇〇」の形式で出力してください。""", max_tokens=6000)

    # --- セクション3: ポイント4〜5（12:00〜18:00） ---
    logger.info("      📝 セクション3/4: ポイント4〜5 生成中...")
    sec3 = _groq_generate(client, f"""あなたは視聴維持率の高いYouTubeクリエイターです。{duration}の長尺動画の台本の本題（後半）を書いてください。

{base_context}

以下の2つのポイントを、それぞれ詳しく解説してください。

【ポイント4: 上級テクニック・差がつく方法 — 12:00〜15:00】
- 知っている人だけが得をする情報
- 具体的な比較（AとBではこれだけ差が出る）
- 実際の事例やケーススタディ
- 20文以上、3〜4分の尺
- ★最後に「最後のポイント5では、今日から即実践できるアクションプランをお伝えします」

【ポイント5: すぐに始められる実践アドバイス — 15:00〜18:00】
- 今日から始められる具体的なアクション3〜5つ
- 各アクションの期待される効果（具体的な数字付き）
- 優先順位をつけて説明
- 15文以上、2〜3分の尺

各文の末尾には「...」を付けて間を示してください。
セクションタイトルは「ポイント4: 〇〇」「ポイント5: 〇〇」の形式で出力してください。""", max_tokens=5000)

    # --- セクション4: まとめ + CTA（18:00〜20:00） ---
    logger.info("      📝 セクション4/4: まとめ+CTA 生成中...")
    sec4 = _groq_generate(client, f"""あなたは視聴維持率の高いYouTubeクリエイターです。{duration}の長尺動画の台本の「まとめ」と「CTA」を書いてください。

{base_context}

[まとめ — 18:00〜19:30]
- 「では、今日お伝えした5つのポイントを振り返りましょう」で始める
- 5つのポイントを各1-2文で簡潔に整理
- 「この中で1つでも実践すれば、確実に結果が変わります」と励まし
- 10文以上

[CTA — 19:30〜20:00]
- 「この動画が参考になったら高評価とチャンネル登録をお願いします」
- 「コメント欄で『一番参考になったポイント番号』を教えてください」
- 次回の動画テーマの予告（関連テーマ）
- 5文以上

各文の末尾には「...」を付けて間を示してください。""")

    # 全セクションを結合
    full_script = f"{sec1}\n\n{sec2}\n\n{sec3}\n\n{sec4}"
    lines = [l for l in full_script.split('\n') if l.strip()]
    logger.info(f"      📊 台本合計: {len(lines)}行")

    return full_script


# ============================================================
# Step 3: 音声生成（VOICEVOX）
# ============================================================

def generate_voiceover(script: str, speaker_id: int = 3) -> str:
    """gTTS（Google Text-to-Speech）で日本語音声を生成（無料・APIキー不要）"""
    try:
        from gtts import gTTS
    except ImportError:
        logger.warning("⚠️ gTTS が未インストール。音声生成をスキップします")
        return ""

    try:
        # 台本を文単位に分割し、間に「...」を挟んで自然なポーズを作る
        lines = [l.strip() for l in script.split('\n') if l.strip()
                 and not l.startswith('[') and len(l.strip()) > 2]

        if not lines:
            logger.warning("⚠️ 台本に有効な行がありません")
            return ""

        # 全行を結合（行間にポーズ用の句点を挿入）
        full_text = "。\n".join(lines)
        logger.info(f"   📝 音声化対象: {len(lines)}行")

        # gTTS で1つの MP3 ファイルに直接保存（pydub/ffmpeg 不要！！）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = TEMP_DIR / f"voiceover_{timestamp}.mp3"
        tts = gTTS(text=full_text, lang='ja', slow=False)
        tts.save(str(output_path))

        logger.info(f"✅ 音声生成完了: {output_path}")
        return str(output_path)

    except Exception as e:
        logger.warning(f"⚠️ gTTS 処理エラー: {e}")
        return ""


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
    """matplotlib で図解スライドを自動生成"""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches

    try:
        import matplotlib.font_manager as fm
        # 日本語フォント試行
        for font in ['Noto Sans CJK JP', 'IPAGothic', 'TakaoPGothic', 'DejaVu Sans']:
            if any(font.lower() in f.name.lower() for f in fm.fontManager.ttflist):
                plt.rcParams['font.family'] = font
                break
    except Exception:
        pass

    slides = []
    keywords = theme.get("keywords", ["AI", "節約", "自動化"])

    # スライド1: タイトル + キーワード一覧
    fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=100)
    fig.patch.set_facecolor('#1a1a2e')
    ax.set_facecolor('#1a1a2e')
    ax.axis('off')

    ax.text(0.5, 0.7, theme.get("theme", "今週のトレンド"),
            color='white', fontsize=28, ha='center', va='center',
            fontweight='bold', wrap=True, transform=ax.transAxes)

    for i, kw in enumerate(keywords[:3]):
        ax.text(0.5, 0.45 - i * 0.12, f"▶ {kw}",
                color='#00d4ff', fontsize=18, ha='center',
                transform=ax.transAxes)

    path = TEMP_DIR / "slide_title.png"
    plt.savefig(str(path), bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()
    slides.append({"path": str(path), "duration": 5.0, "type": "image"})

    # スライド2: 3ポイント比較
    fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=100)
    fig.patch.set_facecolor('#16213e')
    ax.set_facecolor('#16213e')
    ax.axis('off')

    ax.text(0.5, 0.88, "3つのポイント", color='white', fontsize=24,
            ha='center', fontweight='bold', transform=ax.transAxes)

    colors = ['#ff6b6b', '#feca57', '#48dbfb']
    for i, kw in enumerate(keywords[:3]):
        y = 0.65 - i * 0.2
        rect = mpatches.FancyBboxPatch((0.1, y - 0.07), 0.8, 0.14,
                                        boxstyle="round,pad=0.02",
                                        facecolor=colors[i], alpha=0.3,
                                        transform=ax.transAxes)
        ax.add_patch(rect)
        ax.text(0.2, y, f"{i+1}.", color=colors[i], fontsize=20,
                ha='left', va='center', fontweight='bold', transform=ax.transAxes)
        ax.text(0.3, y, kw, color='white', fontsize=18,
                ha='left', va='center', transform=ax.transAxes)

    path = TEMP_DIR / "slide_points.png"
    plt.savefig(str(path), bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()
    slides.append({"path": str(path), "duration": 4.0, "type": "image"})

    logger.info(f"   ✅ インフォグラフィック生成完了: {len(slides)}枚")
    return slides


# ============================================================
# Step 5: 動画編集
# ============================================================

def edit_video(footage: list, voiceover_path: str, script: str,
               output_path: str, timestamp: str) -> str:
    """moviepy で素材を結合して動画を生成"""
    try:
        from moviepy.editor import (
            VideoFileClip, ImageClip, AudioFileClip,
            concatenate_videoclips, CompositeVideoClip
        )
    except ImportError:
        raise ImportError("moviepy が未インストールです: pip install moviepy")

    clips = []
    target_duration = 60 * VIDEO_DURATION_MIN  # 秒

    for item in footage:
        path = item["path"]
        dur = item.get("duration", 5.0)

        try:
            if item.get("type") == "image" or path.endswith(".png"):
                clip = ImageClip(path, duration=dur).resize((1280, 720))
            else:
                clip = VideoFileClip(path).resize((1280, 720))
                clip = clip.subclip(0, min(dur, clip.duration))
            clips.append(clip)
        except Exception as e:
            logger.warning(f"⚠️ クリップ読み込み失敗 {path}: {e}")

    if not clips:
        raise ValueError("有効な映像クリップがありません")

    # ループして尺を合わせる
    while sum(c.duration for c in clips) < target_duration:
        clips.extend(clips[:])

    video = concatenate_videoclips(clips, method="compose")
    video = video.subclip(0, min(target_duration, video.duration))

    # 音声合成（音声が短くても動画の尺は維持する）
    if voiceover_path and Path(voiceover_path).exists():
        audio = AudioFileClip(voiceover_path)
        logger.info(f"   📊 音声尺: {audio.duration:.1f}秒 / 動画尺: {video.duration:.1f}秒")
        if audio.duration > video.duration:
            audio = audio.subclip(0, video.duration)
        video = video.set_audio(audio)

    # SRT 字幕生成
    srt_path = TEMP_DIR / f"subtitles_{timestamp}.srt"
    _generate_srt(script, str(srt_path), video.duration)

    # 一時ファイル出力
    temp_output = str(TEMP_DIR / f"temp_{timestamp}.mp4")
    video.write_videofile(
        temp_output,
        fps=30,
        codec='libx264',
        audio_codec='aac',
        logger=None
    )

    # video_auto_edit が存在する場合は呼び出し
    if VIDEO_AUTO_EDIT_PATH.exists():
        try:
            cmd = [
                "python3", str(VIDEO_AUTO_EDIT_PATH),
                "--input", temp_output,
                "--output", output_path,
            ]
            subprocess.run(cmd, check=True, timeout=600)
            logger.info(f"✅ video_auto_edit 完了: {output_path}")
        except Exception as e:
            logger.warning(f"⚠️ video_auto_edit 失敗（直接出力に切替）: {e}")
            import shutil
            shutil.copy(temp_output, output_path)
    else:
        import shutil
        shutil.copy(temp_output, output_path)
        logger.info(f"✅ 動画出力: {output_path}")

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
# Step 6: サムネイル生成
# ============================================================

def generate_thumbnail(theme: dict, output_path: str) -> str:
    """PIL でYouTubeサムネイル生成（1280x720px）— 黒背景+白文字+黄アクセント"""
    from PIL import Image, ImageDraw, ImageFont

    width, height = 1280, 720
    # 黒背景（完全な黒）
    img = Image.new("RGB", (width, height), color=(10, 10, 10))
    draw = ImageDraw.Draw(img)

    # 黄色アクセントライン（上下）
    YELLOW = (255, 215, 0)
    draw.rectangle([0, 0, width, 6], fill=YELLOW)
    draw.rectangle([0, height - 6, width, height], fill=YELLOW)

    # 左サイド黄色アクセントバー
    draw.rectangle([0, 80, 8, height - 80], fill=YELLOW)

    # タイトルテキスト — 太め・大きめ・白
    title = theme.get("theme", "今週の注目テーマ")

    # 日本語フォント試行（太字系優先）
    font_large = None
    font_medium = None
    font_small = None
    font_paths_bold = [
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    font_paths_regular = [
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for fp in font_paths_bold:
        try:
            font_large = ImageFont.truetype(fp, 72)
            font_medium = ImageFont.truetype(fp, 48)
            break
        except Exception:
            continue
    for fp in font_paths_regular:
        try:
            font_small = ImageFont.truetype(fp, 32)
            break
        except Exception:
            continue
    if not font_large:
        font_large = ImageFont.load_default()
    if not font_medium:
        font_medium = font_large
    if not font_small:
        font_small = ImageFont.load_default()

    # タイトルを折り返し（最大3行）
    if len(title) > 24:
        # 3行に分割
        chunk = len(title) // 3
        title_lines = [title[:chunk], title[chunk:chunk*2], title[chunk*2:]]
    elif len(title) > 14:
        mid = len(title) // 2
        title_lines = [title[:mid], title[mid:]]
    else:
        title_lines = [title]

    # メインタイトル描画（白文字 + 黒縁取り）
    line_height = 90
    y_start = height // 2 - len(title_lines) * line_height // 2
    for line in title_lines:
        # 太い縁取り（黒）
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                draw.text((width//2 + dx, y_start + dy), line,
                          font=font_large, fill=(0, 0, 0), anchor="mm")
        # 本文（白）
        draw.text((width//2, y_start), line,
                  font=font_large, fill=(255, 255, 255), anchor="mm")
        y_start += line_height

    # フック文（黄色・中サイズ — サムネで目を引くサブテキスト）
    hook = theme.get("hook", "")
    if hook and len(hook) > 5:
        hook_display = hook[:30] + ("..." if len(hook) > 30 else "")
        # 黄色背景バー
        hook_y = 100
        draw.rectangle([40, hook_y - 25, width - 40, hook_y + 30], fill=(255, 215, 0))
        draw.text((width//2, hook_y), hook_display,
                  font=font_medium, fill=(10, 10, 10), anchor="mm")

    # 下部：キーワードタグ（白文字）
    keywords = theme.get("keywords", [])[:4]
    kw_text = "  |  ".join([f"#{k}" for k in keywords])
    draw.text((width//2, height - 45), kw_text,
              font=font_small, fill=(200, 200, 200), anchor="mm")

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
        (r'ポイント2[:：]?\s*(.+)', '6:00 {}'),
        (r'ポイント3[:：]?\s*(.+)', '9:00 {}'),
        (r'ポイント4[:：]?\s*(.+)', '12:00 {}'),
        (r'ポイント5[:：]?\s*(.+)', '15:00 {}'),
        (r'\[まとめ', '18:00 まとめ'),
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
        # フォールバック: 基本チャプター
        chapters = [
            "0:00 はじめに",
            "0:30 導入",
            "3:00 ポイント1",
            "6:00 ポイント2",
            "9:00 ポイント3",
            "12:00 ポイント4",
            "15:00 ポイント5",
            "18:00 まとめ",
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

🔔 チャンネル登録はこちら → チャンネルページから登録お願いします
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
        logger.info("   🔄 Pexels API で映像素材収集中...")
        self.footage = collect_footage(self.theme.get("keywords", []))
        logger.info(f"   ✅ 素材収集完了: {len(self.footage)}クリップ")

    # ----------------------------------------------------------
    # Step 5
    # ----------------------------------------------------------
    def _step_edit_video(self):
        if not self.footage:
            raise ValueError("映像素材が未収集です")
        logger.info("   🔄 moviepy で動画編集中...")
        output_path = str(OUTPUT_DIR / f"final_{self.timestamp}.mp4")
        self.video_path = edit_video(
            footage=self.footage,
            voiceover_path=self.voiceover_path or "",
            script=self.script or "",
            output_path=output_path,
            timestamp=self.timestamp
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

    logger.info("🚀 YouTube自動化パイプライン v2.0")
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
