#!/usr/bin/env python3
# ============================================================
# プロンプト生成スクリプト — YouTube動画用AI画像プロンプト
# ============================================================
# Usage:
#   python create_prompts.py --theme "AI投資分析" --keywords "AI,投資,資産運用"
#   python create_prompts.py --theme "節約術" --count 5 --videos 8 --output prompts.json
#   python create_prompts.py --theme "テック" --upload-s3
#
# 環境変数:
#   GROQ_API_KEY         Groq API キー（必須）
#   AI_IMAGE_S3_BUCKET   S3バケット名（--upload-s3 時に必要）
#   AWS_DEFAULT_REGION   AWSリージョン（デフォルト: ap-northeast-1）

import argparse
import json
import logging
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# ============================================================
# 設定・定数
# ============================================================

GROQ_API_KEY   = os.getenv("GROQ_API_KEY", "")
S3_BUCKET      = os.getenv("AI_IMAGE_S3_BUCKET", "")
AWS_REGION     = os.getenv("AWS_DEFAULT_REGION", "ap-northeast-1")
LOG_LEVEL      = os.getenv("LOG_LEVEL", "INFO")
GROQ_MODEL     = "llama-3.3-70b-versatile"
S3_PROMPTS_KEY = "prompts/pending.json"

# 1動画あたりのデフォルト画像構成
DEFAULT_IMAGE_ROLES = [
    "background_main",       # メインテーマビジュアル
    "background_support",    # サブビジュアル
    "background_data",       # データ/チャート系ビジュアル
    "thumbnail_background",  # サムネイル用（目を引く・鮮やか）
    "transition",            # トランジション用（抽象・パターン）
]

# 画像ロール別のスタイルガイド（Groqへの指示に含める）
ROLE_STYLE_GUIDES: Dict[str, str] = {
    "background_main": (
        "Main background visual for YouTube video. "
        "Wide shot, cinematic composition, 16:9 ratio. "
        "Professional and high-quality. Atmospheric and thematic."
    ),
    "background_support": (
        "Supporting background visual for YouTube video. "
        "Complementary to the main theme. "
        "Different angle or perspective from the main visual."
    ),
    "background_data": (
        "Data visualization themed background. "
        "Abstract representation of charts, graphs, financial data, or analytics. "
        "Clean, modern, tech aesthetic. "
        "Holographic displays, glowing numbers, futuristic UI elements."
    ),
    "thumbnail_background": (
        "YouTube thumbnail background. Eye-catching and vibrant. "
        "High contrast, bold colors. "
        "Must look great at small sizes (mobile thumbnail). "
        "Dramatic lighting, strong visual impact."
    ),
    "transition": (
        "Abstract transition image. Geometric patterns or flowing shapes. "
        "Smooth gradients, particle effects, or minimalist design. "
        "Suitable for video transitions and overlays."
    ),
}

# 共通ネガティブプロンプト
NEGATIVE_PROMPT_BASE = (
    "blurry, low quality, pixelated, text, watermark, logo, "
    "signature, distorted, deformed, ugly, bad anatomy, "
    "cropped, out of frame"
)

# デフォルト解像度（YouTube 16:9）
DEFAULT_WIDTH  = 1280
DEFAULT_HEIGHT = 720

# サムネイル: 正方形寄りにして汎用性を高める
THUMBNAIL_WIDTH  = 1280
THUMBNAIL_HEIGHT = 720

logger = logging.getLogger("create_prompts")


# ============================================================
# ロギング設定
# ============================================================

def setup_logging() -> logging.Logger:
    level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(formatter)
    _logger = logging.getLogger("create_prompts")
    _logger.setLevel(level)
    _logger.handlers.clear()
    _logger.addHandler(handler)
    return _logger


# ============================================================
# Groq ユーティリティ
# ============================================================

def _groq_call(client: Groq, prompt: str, max_tokens: int = 2048) -> str:
    """Groq API を呼び出してテキストを生成（youtube_pipeline.py と同じパターン）"""
    resp = client.chat.completions.create(
        model=GROQ_MODEL,
        max_tokens=max_tokens,
        temperature=0.8,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.choices[0].message.content.strip()


def _extract_json(text: str) -> Optional[dict]:
    """テキストから最初の JSON オブジェクトまたは配列を抽出する"""
    # オブジェクト { ... }
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    # 配列 [ ... ]
    match = re.search(r'\[.*\]', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return None


# ============================================================
# 1動画分のプロンプト生成
# ============================================================

def generate_video_prompts(
    client: Groq,
    theme: str,
    keywords: List[str],
    video_index: int,
    image_roles: List[str],
) -> List[dict]:
    """
    Groq を使って1本の動画分の画像プロンプトを生成する。

    Returns:
        List[dict] — generate_images.py が受け取れる形式のプロンプトリスト
    """
    keywords_str = ", ".join(keywords)
    roles_desc = "\n".join([
        f'  - "{role}": {ROLE_STYLE_GUIDES.get(role, "")}'
        for role in image_roles
    ])

    system_context = (
        "You are an expert AI image prompt engineer specializing in "
        "FLUX.1 (Black Forest Labs) model. Your prompts produce photorealistic, "
        "cinematic, high-quality images optimized for YouTube video production "
        "targeting Japanese salaryman audience."
    )

    prompt = f"""{system_context}

Generate FLUX.1-optimized image prompts for a YouTube video about:
Theme: {theme}
Keywords: {keywords_str}
Video index: {video_index + 1} (for batch variation)

Generate one prompt for each of these image roles:
{roles_desc}

Requirements for each prompt:
- Start with the primary subject (e.g., "A Japanese businessman...", "Futuristic cityscape...")
- Include style keywords (e.g., "cinematic lighting", "8k uhd", "photorealistic", "professional photography")
- Include atmosphere/mood (e.g., "dramatic sunset", "neon lights", "clean corporate aesthetic")
- Keep prompts between 40-80 words
- Make each prompt distinct and visually varied from the others
- Japanese/Asian setting preferred when contextually appropriate
- The "thumbnail_background" prompt must be especially vibrant and eye-catching

Output ONLY a JSON object in this exact format (no explanation):
{{
  "background_main": "detailed prompt here...",
  "background_support": "detailed prompt here...",
  "background_data": "detailed prompt here...",
  "thumbnail_background": "detailed prompt here...",
  "transition": "detailed prompt here..."
}}"""

    raw = _groq_call(client, prompt, max_tokens=1024)
    parsed = _extract_json(raw)

    if not parsed or not isinstance(parsed, dict):
        logger.warning(f"  JSON parse failed for video {video_index + 1}. Using fallback prompts.")
        parsed = _fallback_prompts(theme, keywords)

    # generate_images.py のフォーマットに変換
    result = []
    for role in image_roles:
        prompt_text = parsed.get(role, _fallback_single_prompt(theme, role))
        vid_id = f"vid{video_index + 1:03d}"
        role_short = role.split("_")[-1][:3]

        # サムネイルは少し大きめにしてもよいが、デフォルト解像度を維持
        width  = THUMBNAIL_WIDTH  if "thumbnail" in role else DEFAULT_WIDTH
        height = THUMBNAIL_HEIGHT if "thumbnail" in role else DEFAULT_HEIGHT

        result.append({
            "id":                  f"{vid_id}_{role}",
            "role":                role,
            "prompt":              prompt_text,
            "negative_prompt":     NEGATIVE_PROMPT_BASE,
            "width":               width,
            "height":              height,
            "num_images":          1,
            "guidance_scale":      3.5,
            "num_inference_steps": 4,
            "theme":               theme,
            "keywords":            keywords,
        })

    return result


def _fallback_prompts(theme: str, keywords: List[str]) -> dict:
    """Groq パース失敗時のフォールバックプロンプト"""
    kw = keywords[0] if keywords else theme
    return {
        "background_main": (
            f"A professional Japanese business setting related to {theme}, "
            "cinematic lighting, 8k uhd, photorealistic, wide shot"
        ),
        "background_support": (
            f"Abstract visualization of {kw} concept, modern office environment, "
            "corporate aesthetic, clean design, professional photography"
        ),
        "background_data": (
            f"Futuristic data analytics dashboard showing {kw} statistics, "
            "holographic displays, glowing charts, dark background, neon blue accent"
        ),
        "thumbnail_background": (
            f"Eye-catching vibrant scene representing {theme}, "
            "dramatic lighting, bold colors, high contrast, "
            "professional quality, YouTube thumbnail style"
        ),
        "transition": (
            "Abstract geometric pattern, smooth gradient flow, "
            "minimal design, particle effects, dark background with blue accents"
        ),
    }


def _fallback_single_prompt(theme: str, role: str) -> str:
    """単一ロールのフォールバックプロンプト"""
    return _fallback_prompts(theme, [theme]).get(role, f"Professional image about {theme}")


# ============================================================
# バッチ全体のプロンプト生成
# ============================================================

def generate_all_prompts(
    theme: str,
    keywords: List[str],
    num_videos: int,
    images_per_video: int,
    batch_id: Optional[str] = None,
) -> dict:
    """
    複数本の動画分のプロンプトを一括生成して、generate_images.py 用の JSON を返す。
    """
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not set")

    client = Groq(api_key=GROQ_API_KEY)

    if batch_id is None:
        batch_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    # images_per_video に合わせてロール数を調整
    roles = DEFAULT_IMAGE_ROLES[:images_per_video]
    if images_per_video > len(DEFAULT_IMAGE_ROLES):
        # ロール数が足りない場合は background を追加
        extra = images_per_video - len(DEFAULT_IMAGE_ROLES)
        for i in range(extra):
            roles.append(f"background_extra_{i + 1}")

    all_prompts = []
    total_expected = num_videos * len(roles)

    logger.info(f"Generating prompts for {num_videos} videos x {len(roles)} images = {total_expected} total")
    logger.info(f"Theme: {theme} | Keywords: {', '.join(keywords)}")
    logger.info(f"Batch ID: {batch_id}")

    for video_idx in range(num_videos):
        logger.info(f"  Video {video_idx + 1}/{num_videos}...")
        try:
            video_prompts = generate_video_prompts(
                client=client,
                theme=theme,
                keywords=keywords,
                video_index=video_idx,
                image_roles=roles,
            )
            all_prompts.extend(video_prompts)
            logger.info(f"  -> {len(video_prompts)} prompts generated")

            # Groq レート制限対策（動画間に短いウェイト）
            if video_idx < num_videos - 1:
                time.sleep(0.5)

        except Exception as e:
            logger.error(f"  Failed to generate prompts for video {video_idx + 1}: {e}")
            # フォールバックプロンプトで補完
            for role in roles:
                vid_id = f"vid{video_idx + 1:03d}"
                all_prompts.append({
                    "id":                  f"{vid_id}_{role}",
                    "role":                role,
                    "prompt":              _fallback_single_prompt(theme, role),
                    "negative_prompt":     NEGATIVE_PROMPT_BASE,
                    "width":               DEFAULT_WIDTH,
                    "height":             DEFAULT_HEIGHT,
                    "num_images":          1,
                    "guidance_scale":      3.5,
                    "num_inference_steps": 4,
                    "theme":               theme,
                    "keywords":            keywords,
                })

    result = {
        "batch_id":        batch_id,
        "created_at":      datetime.now().isoformat(timespec="seconds"),
        "theme":           theme,
        "keywords":        keywords,
        "num_videos":      num_videos,
        "images_per_video": len(roles),
        "total_prompts":   len(all_prompts),
        "prompts":         all_prompts,
    }

    logger.info(f"Total prompts generated: {len(all_prompts)}")
    return result


# ============================================================
# S3 アップロード
# ============================================================

def upload_to_s3(prompts_data: dict, bucket: str) -> None:
    """prompts JSON を S3 の prompts/pending.json にアップロードする"""
    import boto3

    s3 = boto3.client("s3", region_name=AWS_REGION)
    body = json.dumps(prompts_data, ensure_ascii=False, indent=2).encode("utf-8")
    s3.put_object(
        Bucket=bucket,
        Key=S3_PROMPTS_KEY,
        Body=body,
        ContentType="application/json",
    )
    logger.info(f"Uploaded to s3://{bucket}/{S3_PROMPTS_KEY}")
    logger.info(f"  Total prompts: {prompts_data['total_prompts']}")


# ============================================================
# メイン処理
# ============================================================

def main() -> int:
    global logger
    logger = setup_logging()

    parser = argparse.ArgumentParser(
        description="YouTube動画用AI画像プロンプト生成スクリプト",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使い方:
  # 基本（8本分のプロンプトを生成）
  python create_prompts.py --theme "AI投資分析" --keywords "AI,投資,資産運用"

  # 本数・枚数を指定
  python create_prompts.py --theme "節約術" --count 3 --videos 4 --output prompts.json

  # S3に直接アップロード
  python create_prompts.py --theme "テックトレンド" --upload-s3

  # フル指定
  python create_prompts.py \\
    --theme "2026年の投資戦略" \\
    --keywords "NISA,積立投資,高配当株,副業" \\
    --count 5 \\
    --videos 8 \\
    --output /tmp/prompts_monthly.json \\
    --upload-s3
        """,
    )
    parser.add_argument("--theme",      type=str, required=True, help="動画テーマ（例: 'AI投資分析'）")
    parser.add_argument("--keywords",   type=str, default="",    help="カンマ区切りキーワード（例: 'AI,投資,資産運用'）")
    parser.add_argument("--count",      type=int, default=5,     help="1動画あたりの画像枚数 (default: 5)")
    parser.add_argument("--videos",     type=int, default=8,     help="動画本数 (default: 8, 月次バッチ想定)")
    parser.add_argument("--output",     type=str, default=None,  help="出力JSONファイルパス (default: stdout)")
    parser.add_argument("--upload-s3",  action="store_true",     help="生成したプロンプトをS3にアップロード")
    parser.add_argument("--batch-id",   type=str, default=None,  help="バッチID（省略時は日時で自動生成）")
    args = parser.parse_args()

    if not GROQ_API_KEY:
        logger.error("GROQ_API_KEY is not set")
        return 1

    if args.upload_s3 and not S3_BUCKET:
        logger.error("AI_IMAGE_S3_BUCKET is not set (required for --upload-s3)")
        return 1

    # キーワードをリストに変換
    keywords = [k.strip() for k in args.keywords.split(",") if k.strip()] if args.keywords else [args.theme]

    logger.info("=" * 60)
    logger.info("Prompt Generator — YouTube AI Image Batch")
    logger.info("=" * 60)
    logger.info(f"Theme    : {args.theme}")
    logger.info(f"Keywords : {', '.join(keywords)}")
    logger.info(f"Videos   : {args.videos}")
    logger.info(f"Images/v : {args.count}")
    logger.info(f"Total    : {args.videos * args.count}")

    # プロンプト生成
    try:
        prompts_data = generate_all_prompts(
            theme=args.theme,
            keywords=keywords,
            num_videos=args.videos,
            images_per_video=args.count,
            batch_id=args.batch_id,
        )
    except Exception as e:
        logger.error(f"Failed to generate prompts: {e}")
        return 1

    output_json = json.dumps(prompts_data, ensure_ascii=False, indent=2)

    # ファイル出力
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output_json, encoding="utf-8")
        logger.info(f"Saved to: {output_path}")
        logger.info(f"  Batch ID : {prompts_data['batch_id']}")
        logger.info(f"  Prompts  : {prompts_data['total_prompts']}")
    else:
        # stdout に出力（パイプ処理用）
        print(output_json)

    # S3 アップロード
    if args.upload_s3:
        try:
            upload_to_s3(prompts_data, S3_BUCKET)
            logger.info("S3 upload complete. Ready for generate_images.py --from-s3")
        except Exception as e:
            logger.error(f"S3 upload failed: {e}")
            return 1

    logger.info("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
