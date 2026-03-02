"""
VibeMatch 印象タグ推定エンジン

CLIP Zero-shot で顔画像から印象タグを推定する。
"""

import numpy as np
import open_clip
import torch
from PIL import Image

from app.tags import VIBE_TAGS, CATEGORIES, CATEGORY_IDS, TAGS_BY_CATEGORY


class ImpressionTagger:
    """CLIP Zero-shot ベースの印象タグ推定器"""

    def __init__(self):
        self.device = "cpu"  # MVP: CPU推論で十分
        self.model = None
        self.preprocess = None
        self.tokenizer = None
        self._tag_embeddings: dict[str, np.ndarray] = {}
        self._category_embeddings: dict[str, np.ndarray] = {}

    def load(self):
        """モデルをロード（起動時に1回だけ呼ぶ）"""
        print("Loading CLIP model (ViT-L-14)...")
        self.model, _, self.preprocess = open_clip.create_model_and_transforms(
            "ViT-L-14", pretrained="openai", device=self.device
        )
        self.tokenizer = open_clip.get_tokenizer("ViT-L-14")
        self.model.eval()

        # 全タグのテキストembeddingを事前計算
        self._precompute_tag_embeddings()
        print(f"Loaded. {len(self._tag_embeddings)} tag embeddings cached.")

    def _precompute_tag_embeddings(self):
        """全タグのCLIPテキストembeddingを事前計算してキャッシュ"""
        for tag in VIBE_TAGS:
            # 英語プロンプトの平均embedding
            prompts = tag.prompts_en
            embeddings = []
            for prompt in prompts:
                tokens = self.tokenizer([prompt]).to(self.device)
                with torch.no_grad():
                    emb = self.model.encode_text(tokens)
                    emb = emb / emb.norm(dim=-1, keepdim=True)
                    embeddings.append(emb.cpu().numpy()[0])
            self._tag_embeddings[tag.id] = np.mean(embeddings, axis=0)

        # カテゴリ単位のembedding（各カテゴリのタグ平均）
        for cat_id in CATEGORY_IDS:
            cat_tags = TAGS_BY_CATEGORY[cat_id]
            cat_embs = [self._tag_embeddings[t.id] for t in cat_tags]
            self._category_embeddings[cat_id] = np.mean(cat_embs, axis=0)

    def predict(self, face_image: Image.Image, top_k: int = 5) -> dict:
        """
        顔画像から印象タグを推定する。

        Args:
            face_image: クロップ済みの顔画像 (PIL Image)
            top_k: 返すタグの数

        Returns:
            {
                "tags": [{"id": str, "label": str, "prob": float}, ...],
                "overall_confidence": int (0-100),
                "tag_vector": [float, ...] (8次元, 各カテゴリの確率),
                "explanation": [{"type": "explain", "text": str}, ...],
            }
        """
        # 画像embedding取得
        image_tensor = self.preprocess(face_image).unsqueeze(0).to(self.device)
        with torch.no_grad():
            image_emb = self.model.encode_image(image_tensor)
            image_emb = image_emb / image_emb.norm(dim=-1, keepdim=True)
            image_emb = image_emb.cpu().numpy()[0]

        # 各タグとのcos類似度
        tag_scores = {}
        for tag in VIBE_TAGS:
            tag_emb = self._tag_embeddings[tag.id]
            cos_sim = float(np.dot(image_emb, tag_emb))
            tag_scores[tag.id] = cos_sim

        # カテゴリごとの集約スコア（8次元ベクトル）
        cat_scores = {}
        for cat_id in CATEGORY_IDS:
            cat_emb = self._category_embeddings[cat_id]
            cos_sim = float(np.dot(image_emb, cat_emb))
            cat_scores[cat_id] = cos_sim

        # softmaxで確率化
        cat_probs = _softmax_dict(cat_scores, temperature=0.05)
        tag_probs = _softmax_dict(tag_scores, temperature=0.03)

        # Top-K タグ
        sorted_tags = sorted(tag_probs.items(), key=lambda x: x[1], reverse=True)
        top_tags = []
        for tag_id, prob in sorted_tags[:top_k]:
            tag_def = next(t for t in VIBE_TAGS if t.id == tag_id)
            top_tags.append({
                "id": tag_id,
                "label": tag_def.label,
                "prob": round(prob, 3),
                "category": tag_def.category,
            })

        # 総合信頼度: Top1確率が高いほど信頼度が高い
        top1_prob = sorted_tags[0][1] if sorted_tags else 0
        top3_spread = sorted_tags[0][1] - sorted_tags[2][1] if len(sorted_tags) >= 3 else 0
        overall_confidence = min(100, int(top1_prob * 80 + top3_spread * 200))

        # タグベクトル（8次元）
        tag_vector = [round(cat_probs.get(c, 0.0), 4) for c in CATEGORY_IDS]

        # 説明文生成（テンプレートベース）
        explanations = _generate_explanations(top_tags, cat_probs)

        return {
            "tags": top_tags,
            "overall_confidence": overall_confidence,
            "tag_vector": tag_vector,
            "explanation": explanations,
        }


def _softmax_dict(scores: dict[str, float], temperature: float = 0.05) -> dict[str, float]:
    """辞書のvalueにsoftmaxを適用"""
    keys = list(scores.keys())
    values = np.array([scores[k] for k in keys])
    # temperature scaling
    values = values / temperature
    exp_values = np.exp(values - np.max(values))
    probs = exp_values / exp_values.sum()
    return {k: float(p) for k, p in zip(keys, probs)}


def _generate_explanations(
    top_tags: list[dict], cat_probs: dict[str, float]
) -> list[dict]:
    """推薦理由を自然文で生成（テンプレートベース）"""
    explanations = []

    # 1. メインタグの説明
    if top_tags:
        main = top_tags[0]
        cat_label = next(
            (c["label"] for c in CATEGORIES if c["id"] == main["category"]), ""
        )
        explanations.append({
            "type": "explain",
            "text": f"全体の印象が「{cat_label}」寄りで、{main['label']}な雰囲気が強く出ています",
        })

    # 2. サブタグの補足
    if len(top_tags) >= 2:
        sub = top_tags[1]
        explanations.append({
            "type": "explain",
            "text": f"「{sub['label']}」の要素も感じられ、多面的な魅力があります",
        })

    # 3. 全体バランスの言及
    sorted_cats = sorted(cat_probs.items(), key=lambda x: x[1], reverse=True)
    top_cat = sorted_cats[0][0] if sorted_cats else ""
    second_cat = sorted_cats[1][0] if len(sorted_cats) > 1 else ""
    if top_cat and second_cat:
        top_label = next(
            (c["label"] for c in CATEGORIES if c["id"] == top_cat), ""
        )
        sec_label = next(
            (c["label"] for c in CATEGORIES if c["id"] == second_cat), ""
        )
        explanations.append({
            "type": "explain",
            "text": f"「{top_label}」と「{sec_label}」のバランスが特徴的です",
        })

    return explanations[:3]
