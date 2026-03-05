"""
VibeMatch 顔検出 & 品質判定

InsightFace RetinaFace で顔を検出し、
品質チェック（明るさ/ブレ/サイズ/人数）を行う。
"""

import numpy as np
from PIL import Image, ImageFilter


class FaceDetector:
    """顔検出 + 品質チェック"""

    # 品質しきい値
    MIN_FACE_RATIO = 0.15       # 顔が画像の15%以上
    MIN_BRIGHTNESS = 50          # 平均輝度の下限
    MAX_BRIGHTNESS = 240         # 平均輝度の上限
    MIN_SHARPNESS = 50.0         # Laplacian variance の下限
    MAX_FACES = 1                # 最大検出顔数（1人のみ）

    def __init__(self):
        self._model = None

    def load(self):
        """InsightFace モデルのロード"""
        try:
            from insightface.app import FaceAnalysis
            self._model = FaceAnalysis(
                name="buffalo_sc",  # 軽量版
                providers=["CPUExecutionProvider"],
            )
            self._model.prepare(ctx_id=-1, det_size=(640, 640))
            print("FaceDetector loaded (InsightFace buffalo_sc)")
        except Exception as e:
            print(f"InsightFace load failed, using fallback: {e}")
            self._model = None

    def detect_and_crop(self, image: Image.Image) -> dict:
        """
        顔検出 + 品質チェック + クロップ

        Returns:
            {
                "success": bool,
                "face_image": Image (cropped) or None,
                "quality_score": int (0-100),
                "issues": [str],  # 問題点のリスト
                "suggestions": [str],  # 改善提案
            }
        """
        img_array = np.array(image.convert("RGB"))
        issues = []
        suggestions = []

        # 1. 明るさチェック
        brightness = np.mean(img_array)
        if brightness < self.MIN_BRIGHTNESS:
            issues.append("dark")
            suggestions.append("明るい場所で撮影してください")
        elif brightness > self.MAX_BRIGHTNESS:
            issues.append("overexposed")
            suggestions.append("明るすぎます。直射日光を避けてください")

        # 2. ブレチェック (Laplacian variance)
        gray = image.convert("L")
        laplacian = gray.filter(ImageFilter.Kernel(
            size=(3, 3),
            kernel=[-1, -1, -1, -1, 8, -1, -1, -1, -1],
            scale=1, offset=128,
        ))
        sharpness = np.var(np.array(laplacian).astype(float))
        if sharpness < self.MIN_SHARPNESS:
            issues.append("blurry")
            suggestions.append("ブレています。カメラを固定して撮影してください")

        # 3. 顔検出
        if self._model is not None:
            faces = self._model.get(img_array)
        else:
            # フォールバック: 顔検出なしで画像中央をクロップ
            faces = self._fallback_detect(img_array)

        if len(faces) == 0:
            return {
                "success": False,
                "face_image": None,
                "quality_score": 0,
                "issues": ["no_face"],
                "suggestions": ["顔が検出できませんでした。正面を向いて撮影してください"],
            }

        if len(faces) > self.MAX_FACES:
            issues.append("multiple_faces")
            suggestions.append("1人で撮影してください")
            return {
                "success": False,
                "face_image": None,
                "quality_score": 0,
                "issues": issues,
                "suggestions": suggestions,
            }

        # 4. 顔サイズチェック
        face = faces[0]
        if hasattr(face, 'bbox'):
            bbox = face.bbox.astype(int)
        else:
            bbox = face["bbox"]

        x1, y1, x2, y2 = bbox
        face_area = (x2 - x1) * (y2 - y1)
        image_area = img_array.shape[0] * img_array.shape[1]
        face_ratio = face_area / image_area

        if face_ratio < self.MIN_FACE_RATIO:
            issues.append("face_too_small")
            suggestions.append("顔がもっと大きく映るように近づいてください")

        # 5. 顔をクロップ（マージン付き）
        margin = 0.3
        h, w = img_array.shape[:2]
        fw, fh = x2 - x1, y2 - y1
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        crop_size = int(max(fw, fh) * (1 + margin))
        half = crop_size // 2

        crop_x1 = max(0, cx - half)
        crop_y1 = max(0, cy - half)
        crop_x2 = min(w, cx + half)
        crop_y2 = min(h, cy + half)

        face_crop = image.crop((crop_x1, crop_y1, crop_x2, crop_y2))
        face_crop = face_crop.resize((224, 224), Image.LANCZOS)

        # 品質スコア計算
        quality_score = self._compute_quality_score(
            brightness, sharpness, face_ratio, issues
        )

        return {
            "success": len(issues) == 0 or (len(issues) == 1 and "face_too_small" in issues),
            "face_image": face_crop,
            "quality_score": quality_score,
            "issues": issues,
            "suggestions": suggestions,
        }

    def _compute_quality_score(
        self,
        brightness: float,
        sharpness: float,
        face_ratio: float,
        issues: list[str],
    ) -> int:
        """品質スコアを0-100で計算"""
        score = 100

        # 明るさ減点
        if brightness < self.MIN_BRIGHTNESS:
            score -= 20
        elif brightness > self.MAX_BRIGHTNESS:
            score -= 15

        # ブレ減点
        if sharpness < self.MIN_SHARPNESS:
            score -= 25
        elif sharpness < self.MIN_SHARPNESS * 2:
            score -= 10

        # 顔サイズ減点
        if face_ratio < self.MIN_FACE_RATIO:
            score -= 20
        elif face_ratio < 0.2:
            score -= 10

        # 問題数で減点
        score -= len(issues) * 5

        return max(0, min(100, score))

    def _fallback_detect(self, img_array: np.ndarray) -> list:
        """InsightFace使えない場合のフォールバック（中央クロップ）"""
        h, w = img_array.shape[:2]
        # 画像中央を顔と仮定
        cx, cy = w // 2, h // 2
        size = min(w, h) // 2
        return [{"bbox": [cx - size, cy - size, cx + size, cy + size]}]
