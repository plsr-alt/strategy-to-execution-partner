#!/usr/bin/env python3
# ============================================================
# AI画像バッチ生成スクリプト — FLUX.2-klein 4B (GPU / NVIDIA L4 24GB VRAM)
# ============================================================
# Usage:
#   python generate_images.py --from-s3
#   python generate_images.py --prompts prompts.json --output /home/ec2-user/output
#   python generate_images.py --test
#
# 環境変数:
#   AI_IMAGE_S3_BUCKET   S3バケット名（必須、--from-s3 時）
#   AWS_DEFAULT_REGION   AWSリージョン（デフォルト: ap-northeast-1）
#   LOG_LEVEL            ログレベル（デフォルト: INFO）

import argparse
import json
import logging
import os
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import torch
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# 設定・定数
# ============================================================

MODEL_PATH    = os.getenv("FLUX_MODEL_PATH", "/home/ec2-user/models/flux2-klein")
OUTPUT_DIR    = Path(os.getenv("OUTPUT_DIR", "/home/ec2-user/output"))
S3_BUCKET     = os.getenv("AI_IMAGE_S3_BUCKET", "")
S3_PROMPTS_KEY = "prompts/pending.json"
AWS_REGION    = os.getenv("AWS_DEFAULT_REGION", "ap-northeast-1")
LOG_LEVEL     = os.getenv("LOG_LEVEL", "INFO")

# デフォルト生成パラメータ
DEFAULT_WIDTH            = 1280
DEFAULT_HEIGHT           = 720
DEFAULT_GUIDANCE_SCALE   = 0     # FLUX.2-klein は蒸留モデル: CFG不要 (guidance_scale=0)
DEFAULT_INFERENCE_STEPS  = 4    # FLUX.2-klein 4B: sub-second on L4, 4ステップで十分
DEFAULT_NUM_IMAGES       = 1

# OOM 発生時の縮小解像度（縦横ともに 75%）
OOM_FALLBACK_SCALE = 0.75

# テスト用プロンプト
TEST_PROMPT = {
    "id": "test_001",
    "prompt": "A futuristic Tokyo skyline at sunset, cyberpunk style, 16:9 aspect ratio, high quality",
    "negative_prompt": "blurry, low quality, text, watermark",
    "width": 1280,
    "height": 720,
    "num_images": 1,
    "guidance_scale": 0,
    "num_inference_steps": 4,
}

logger = logging.getLogger("generate_images")


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
    _logger = logging.getLogger("generate_images")
    _logger.setLevel(level)
    _logger.handlers.clear()
    _logger.addHandler(handler)
    return _logger


# ============================================================
# モデルのロード
# ============================================================

def load_model():
    """
    FLUX.2-klein 4B をローカルパスから fp16 でロード。
    NVIDIA L4 (24GB VRAM) での推論を前提とした設定。
    4Bパラメータの蒸留モデルのため、L4上でsub-second推論が可能。
    """
    from diffusers import FluxPipeline

    logger.info(f"Loading FLUX.2-klein 4B from: {MODEL_PATH}")
    logger.info(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        logger.info(f"GPU: {torch.cuda.get_device_name(0)}, "
                    f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB")

    pipe = FluxPipeline.from_pretrained(
        MODEL_PATH,
        torch_dtype=torch.float16,
        # ローカルモデルのみ使用（HuggingFace Hub へのアクセス禁止）
        local_files_only=True,
    )

    if torch.cuda.is_available():
        pipe = pipe.to("cuda")
        # L4 24GB VRAM: 4Bモデルなので余裕あり。attention slicing で追加マージン確保
        pipe.enable_attention_slicing()
        # xformers が使えれば利用（高速化・省メモリ）
        try:
            pipe.enable_xformers_memory_efficient_attention()
            logger.info("xformers memory efficient attention enabled")
        except Exception:
            logger.info("xformers not available, using default attention")
    else:
        logger.warning("CUDA not available. Running on CPU (very slow).")
        pipe = pipe.to("cpu")

    logger.info("Model loaded successfully")
    return pipe


# ============================================================
# 画像生成（単一プロンプト）
# ============================================================

def generate_single(
    pipe,
    prompt_cfg: dict,
    output_dir: Path,
) -> Tuple[List[str], float]:
    """
    単一プロンプト設定から画像を生成し、PNG として保存する。

    Returns:
        (saved_paths, elapsed_sec)
    """
    prompt_id    = prompt_cfg["id"]
    prompt       = prompt_cfg["prompt"]
    neg_prompt   = prompt_cfg.get("negative_prompt", "blurry, low quality")
    width        = prompt_cfg.get("width",  DEFAULT_WIDTH)
    height       = prompt_cfg.get("height", DEFAULT_HEIGHT)
    num_images   = prompt_cfg.get("num_images", DEFAULT_NUM_IMAGES)
    guidance     = prompt_cfg.get("guidance_scale", DEFAULT_GUIDANCE_SCALE)
    steps        = prompt_cfg.get("num_inference_steps", DEFAULT_INFERENCE_STEPS)

    output_dir.mkdir(parents=True, exist_ok=True)
    saved_paths: List[str] = []
    start = time.time()

    # --- 生成試行（OOM 発生時は解像度を下げてリトライ） ---
    for attempt in range(2):
        try:
            if attempt > 0:
                # 1回目が OOM → 解像度を縮小してリトライ
                width  = int(width  * OOM_FALLBACK_SCALE)
                height = int(height * OOM_FALLBACK_SCALE)
                # FLUX は 8 の倍数が必須
                width  = (width  // 8) * 8
                height = (height // 8) * 8
                logger.warning(f"  OOM fallback: retrying at {width}x{height}")
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()

            # FLUX.2-klein: guidance_scale=0 が推奨設定
            # （蒸留モデルのため classifier-free guidance を使わない）
            result = pipe(
                prompt=prompt,
                negative_prompt=neg_prompt,
                width=width,
                height=height,
                num_images_per_prompt=num_images,
                guidance_scale=guidance,
                num_inference_steps=steps,
                generator=torch.Generator("cuda" if torch.cuda.is_available() else "cpu"),
            )

            for idx, image in enumerate(result.images):
                filename = f"{prompt_id}_{idx}.png"
                save_path = output_dir / filename
                image.save(str(save_path), format="PNG")
                saved_paths.append(str(save_path))

            break  # 成功

        except torch.cuda.OutOfMemoryError:
            if attempt == 0:
                logger.warning(f"  CUDA OOM on {prompt_id} ({width}x{height}). Retrying with lower resolution...")
                continue
            else:
                raise RuntimeError(
                    f"OOM even at reduced resolution ({width}x{height}). "
                    "L4 has 24GB VRAM — check for other GPU processes or "
                    "consider reducing num_images or inference steps."
                )

    elapsed = time.time() - start
    return saved_paths, elapsed


# ============================================================
# バッチ生成（メインループ）
# ============================================================

def run_batch(
    pipe,
    prompts_data: dict,
    output_dir: Path,
) -> dict:
    """
    prompts_data の全プロンプトを順次生成し、manifest を返す。
    """
    batch_id  = prompts_data.get("batch_id", datetime.now().strftime("%Y%m%d_%H%M%S"))
    prompts   = prompts_data.get("prompts", [])
    total     = len(prompts)

    batch_output_dir = output_dir / batch_id
    batch_output_dir.mkdir(parents=True, exist_ok=True)

    manifest_images: List[dict] = []
    batch_start = time.time()

    logger.info(f"Starting batch: {batch_id} ({total} prompts)")

    for i, prompt_cfg in enumerate(prompts, start=1):
        prompt_id = prompt_cfg.get("id", f"img_{i:04d}")
        logger.info(f"Generating image {i}/{total}: {prompt_id}...")

        try:
            saved_paths, elapsed = generate_single(pipe, prompt_cfg, batch_output_dir)

            for path in saved_paths:
                manifest_images.append({
                    "id":                  prompt_id,
                    "filename":            Path(path).name,
                    "prompt":              prompt_cfg.get("prompt", ""),
                    "negative_prompt":     prompt_cfg.get("negative_prompt", ""),
                    "width":               prompt_cfg.get("width",  DEFAULT_WIDTH),
                    "height":              prompt_cfg.get("height", DEFAULT_HEIGHT),
                    "guidance_scale":      prompt_cfg.get("guidance_scale", DEFAULT_GUIDANCE_SCALE),
                    "num_inference_steps": prompt_cfg.get("num_inference_steps", DEFAULT_INFERENCE_STEPS),
                    "generation_time_sec": round(elapsed, 2),
                    "status":              "success",
                })

            logger.info(f"  Done in {elapsed:.1f}s -> {[Path(p).name for p in saved_paths]}")

        except Exception as e:
            logger.error(f"  FAILED {prompt_id}: {e}")
            logger.debug(traceback.format_exc())
            manifest_images.append({
                "id":     prompt_id,
                "status": "failed",
                "error":  str(e),
            })

    total_elapsed = time.time() - batch_start
    success_count = sum(1 for m in manifest_images if m.get("status") == "success")

    manifest = {
        "batch_id":        batch_id,
        "generated_at":    datetime.now().isoformat(timespec="seconds"),
        "images":          manifest_images,
        "total_images":    success_count,
        "total_time_sec":  round(total_elapsed, 2),
        "failed_count":    total - success_count,
    }

    # manifest.json を出力ディレクトリに保存
    manifest_path = batch_output_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info(f"Manifest saved: {manifest_path}")
    logger.info(f"Batch complete: {success_count}/{total} succeeded in {total_elapsed:.1f}s")

    return manifest


# ============================================================
# S3 連携
# ============================================================

def s3_download_prompts(bucket: str) -> dict:
    """S3 から prompts/pending.json を取得して dict を返す"""
    import boto3

    s3 = boto3.client("s3", region_name=AWS_REGION)
    logger.info(f"Downloading prompts from s3://{bucket}/{S3_PROMPTS_KEY}")
    obj = s3.get_object(Bucket=bucket, Key=S3_PROMPTS_KEY)
    return json.loads(obj["Body"].read().decode("utf-8"))


def s3_upload_results(bucket: str, batch_id: str, batch_output_dir: Path) -> None:
    """
    生成結果（PNG + manifest.json）を S3 output/{batch_id}/ にアップロードし、
    pending.json を prompts/processed/{batch_id}.json に移動する。
    """
    import boto3

    s3 = boto3.client("s3", region_name=AWS_REGION)
    prefix = f"output/{batch_id}/"

    files = list(batch_output_dir.iterdir())
    logger.info(f"Uploading {len(files)} files to s3://{bucket}/{prefix}")

    for file_path in files:
        s3_key = f"{prefix}{file_path.name}"
        content_type = "application/json" if file_path.suffix == ".json" else "image/png"
        s3.upload_file(
            str(file_path),
            bucket,
            s3_key,
            ExtraArgs={"ContentType": content_type},
        )
        logger.info(f"  Uploaded: {s3_key}")

    # pending.json -> processed/{batch_id}.json に移動（コピー後削除）
    processed_key = f"prompts/processed/{batch_id}.json"
    s3.copy_object(
        Bucket=bucket,
        CopySource={"Bucket": bucket, "Key": S3_PROMPTS_KEY},
        Key=processed_key,
    )
    s3.delete_object(Bucket=bucket, Key=S3_PROMPTS_KEY)
    logger.info(f"Moved pending.json -> {processed_key}")


# ============================================================
# テストモード
# ============================================================

def run_test(pipe, output_dir: Path) -> bool:
    """
    1枚だけ生成してセットアップが正常かを確認する。
    """
    logger.info("Running test generation (1 image)...")
    test_data = {
        "batch_id": "test_" + datetime.now().strftime("%Y%m%d_%H%M%S"),
        "prompts":  [TEST_PROMPT],
    }
    try:
        manifest = run_batch(pipe, test_data, output_dir)
        if manifest["total_images"] == 1:
            img_info = manifest["images"][0]
            logger.info(f"Test PASSED: {img_info['filename']} generated in {img_info['generation_time_sec']}s")
            return True
        else:
            logger.error("Test FAILED: image not generated")
            return False
    except Exception as e:
        logger.error(f"Test FAILED: {e}")
        logger.debug(traceback.format_exc())
        return False


# ============================================================
# メイン処理
# ============================================================

def main() -> int:
    global logger
    logger = setup_logging()

    parser = argparse.ArgumentParser(
        description="FLUX.2-klein 4B AI画像バッチ生成スクリプト (NVIDIA L4 24GB)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使い方:
  # テスト（1枚生成）
  python generate_images.py --test

  # ローカルファイルから生成
  python generate_images.py --prompts /path/to/prompts.json

  # S3から取得して生成・アップロード
  python generate_images.py --from-s3

  # 出力先指定
  python generate_images.py --prompts prompts.json --output /home/ec2-user/output
        """,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--from-s3",  action="store_true", help="S3からプロンプトを取得し、結果をS3にアップロード")
    group.add_argument("--prompts",  type=str,             help="ローカルプロンプトJSONファイルのパス")
    group.add_argument("--test",     action="store_true",  help="テスト用に1枚生成してセットアップを確認")
    parser.add_argument("--output",  type=str, default=str(OUTPUT_DIR), help=f"出力ディレクトリ (default: {OUTPUT_DIR})")
    parser.add_argument("--model",   type=str, default=MODEL_PATH,      help=f"モデルパス (default: {MODEL_PATH})")
    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("=" * 60)
    logger.info("AI Image Generator — FLUX.2-klein 4B (L4 24GB)")
    logger.info("=" * 60)
    logger.info(f"Output dir : {output_dir}")
    logger.info(f"Model path : {args.model}")
    logger.info(f"CUDA       : {torch.cuda.is_available()}")

    # モデルロード（全モードで共通）
    try:
        pipe = load_model()
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        logger.debug(traceback.format_exc())
        return 1

    # --- テストモード ---
    if args.test:
        success = run_test(pipe, output_dir)
        return 0 if success else 1

    # --- ローカルファイルモード ---
    if args.prompts:
        prompts_path = Path(args.prompts)
        if not prompts_path.exists():
            logger.error(f"Prompts file not found: {prompts_path}")
            return 1
        prompts_data = json.loads(prompts_path.read_text(encoding="utf-8"))
        manifest = run_batch(pipe, prompts_data, output_dir)
        return 0 if manifest["failed_count"] == 0 else 1

    # --- S3 モード ---
    if args.from_s3:
        if not S3_BUCKET:
            logger.error("AI_IMAGE_S3_BUCKET environment variable is not set")
            return 1

        try:
            prompts_data = s3_download_prompts(S3_BUCKET)
        except Exception as e:
            logger.error(f"Failed to download prompts from S3: {e}")
            return 1

        batch_id = prompts_data.get("batch_id", datetime.now().strftime("%Y%m%d_%H%M%S"))
        manifest = run_batch(pipe, prompts_data, output_dir)

        batch_output_dir = output_dir / batch_id
        try:
            s3_upload_results(S3_BUCKET, batch_id, batch_output_dir)
        except Exception as e:
            logger.error(f"Failed to upload results to S3: {e}")
            logger.info(f"Results are saved locally at: {batch_output_dir}")
            return 1

        return 0 if manifest["failed_count"] == 0 else 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
