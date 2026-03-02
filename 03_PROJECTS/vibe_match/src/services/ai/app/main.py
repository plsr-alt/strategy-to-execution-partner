"""
VibeMatch AI推論サービス (FastAPI)

エンドポイント:
  POST /v1/face/diagnose   - 写真から印象タグを診断
  GET  /health             - ヘルスチェック
"""

import io
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from pydantic import BaseModel

from app.face_detector import FaceDetector
from app.guardrails import validate_output
from app.impression_tagger import ImpressionTagger


# ============================================
# グローバルモデルインスタンス
# ============================================
face_detector = FaceDetector()
tagger = ImpressionTagger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """起動時にモデルをロード"""
    face_detector.load()
    tagger.load()
    yield


app = FastAPI(
    title="VibeMatch AI Service",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番ではドメイン制限する
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# レスポンスモデル
# ============================================
class DiagnosisResponse(BaseModel):
    diagnosis_id: str
    overall_confidence: int
    tags: list[dict]
    explanation: list[dict]
    tag_vector: list[float]
    quality_score: int
    quality_issues: list[str]
    quality_suggestions: list[str]
    guardrails: dict
    processing_time_ms: int


# ============================================
# エンドポイント
# ============================================
@app.get("/health")
async def health():
    return {"status": "ok", "model": "clip-vit-l-14-v1"}


@app.post("/v1/face/diagnose", response_model=DiagnosisResponse)
async def diagnose(photo: UploadFile = File(...)):
    """
    写真から印象タグを診断する。

    1. 画像バリデーション
    2. 顔検出 + 品質チェック
    3. CLIP印象タグ推定
    4. ガードレール通過
    5. 結果返却
    """
    start_time = time.time()

    # 1. 画像バリデーション
    if photo.content_type not in ("image/jpeg", "image/png", "image/webp"):
        raise HTTPException(400, "Unsupported image format. Use JPEG, PNG, or WebP.")

    contents = await photo.read()
    if len(contents) > 5 * 1024 * 1024:  # 5MB
        raise HTTPException(400, "Image too large. Max 5MB.")

    try:
        image = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception:
        raise HTTPException(400, "Invalid image file.")

    # 2. 顔検出 + 品質チェック
    detection = face_detector.detect_and_crop(image)

    if not detection["success"]:
        # 顔検出失敗でも部分的な結果は返す
        processing_time = int((time.time() - start_time) * 1000)
        return DiagnosisResponse(
            diagnosis_id=f"dg_{int(time.time())}",
            overall_confidence=0,
            tags=[],
            explanation=[],
            tag_vector=[0.0] * 8,
            quality_score=detection["quality_score"],
            quality_issues=detection["issues"],
            quality_suggestions=detection["suggestions"],
            guardrails={
                "celebrity_similarity": "blocked",
                "identity_match": "blocked",
                "sensitive_inference": "blocked",
            },
            processing_time_ms=processing_time,
        )

    face_image = detection["face_image"]

    # 3. CLIP印象タグ推定
    result = tagger.predict(face_image, top_k=5)

    # 4. ガードレール
    validation = validate_output(result["tags"], result["explanation"])

    processing_time = int((time.time() - start_time) * 1000)

    return DiagnosisResponse(
        diagnosis_id=f"dg_{int(time.time())}",
        overall_confidence=result["overall_confidence"],
        tags=validation["filtered_tags"],
        explanation=validation["filtered_explanations"],
        tag_vector=result["tag_vector"],
        quality_score=detection["quality_score"],
        quality_issues=detection["issues"],
        quality_suggestions=detection["suggestions"],
        guardrails=validation["guardrails"],
        processing_time_ms=processing_time,
    )
