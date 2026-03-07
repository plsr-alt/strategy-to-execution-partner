# AI画像生成ビジネス — TODO

**最終更新**: 2026-03-07

---

## Phase 1: GPU環境構築（今週）

### インフラ（CloudFormation: `gpu_image_gen_stack.yaml`）
- [x] CloudFormation テンプレート完成 → **g6.xlarge (NVIDIA L4, 24GB VRAM)** に更新済み
- [ ] `aws cloudformation deploy` でスタック作成
- [ ] SNS メール購読確認（確認メールをクリック）
- [ ] スポットインスタンス起動テスト

### GPU インスタンスセットアップ
- [ ] g6.xlarge スポット初回起動
- [x] `setup_gpu_env.sh` 完成 → FLUX.2 klein 4B + Wan 2.2 対応済み
- [ ] `setup_gpu_env.sh` 実行 (NVIDIA L4 + CUDA 12.4 + Python)
- [ ] FLUX.2 [klein] 4B ダウンロード (~8GB)
- [ ] Wan 2.2 (1.3B) ダウンロード (~5GB)
- [ ] テスト画像生成 (`generate_images.py --test`)
- [ ] AMI 作成 (セットアップ済み環境を保存)

### スクリプト
- [x] `generate_images.py` — FLUX.2 klein 4B バッチ生成
- [x] `create_prompts.py` — プロンプトJSON生成 (Groq)
- [x] `setup_gpu_env.sh` — GPU環境セットアップ (L4対応)
- [x] `startup.sh` — EC2起動時自動実行 (shutdown -h +90)

---

## Phase 2: 既存パイプライン統合

### youtube_pipeline.py 改修
- [ ] Step 4 改修: S3からAI画像取得 (Pexelsフォールバック)
- [ ] Step 6 改修: サムネイルにAI背景画像使用 (オプション)
- [ ] S3画像取得ユーティリティ関数追加
- [ ] .env に `AI_IMAGE_S3_BUCKET` 追加

### 運用フロー確立
- [ ] 月初バッチ: create_prompts.py → S3 → g6起動 → 画像生成 → S3
- [ ] 日次: t4g.medium が S3から画像取得 → 動画パイプライン実行

---

## Phase 3: 品質向上・拡張（Month 2〜）

- [ ] LoRA 学習 (Ostris AI Toolkit, L4 24GBで十分)
- [ ] Wan 2.2 動画化パイプライン (Ken Burns代替)
- [ ] Z-Image-Turbo 日本語サムネイル
- [ ] サムネイル A/B テスト自動生成
- [ ] マルチチャネル展開 (XActions + Mixpost)

---

## 完了済み

- [x] マネタイズ調査 (`04_RESEARCH/2026-03-06_AI_image_monetization_research.md`)
- [x] 技術パイプライン調査 (`04_RESEARCH/2026-03-06_AI_image_generation_SNS_pipeline.md`)
- [x] 統合PLAN.md作成 (`03_PROJECTS/ai_image_business/PLAN.md`)
- [x] SPEC.md作成・更新 → g6.xlarge + FLUX.2 klein + Wan 2.2
- [x] CloudFormation テンプレート (`gpu_image_gen_stack.yaml`) → g6.xlarge対応
- [x] 画像生成スクリプト (`generate_images.py`) → FLUX.2 klein 4B対応
- [x] プロンプト生成スクリプト (`create_prompts.py`)
- [x] GPUセットアップスクリプト (`setup_gpu_env.sh`) → L4 + CUDA 12.4対応
