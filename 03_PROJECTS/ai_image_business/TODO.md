# AI画像生成ビジネス — TODO

**最終更新**: 2026-03-06

---

## Phase 1: GPU環境構築（今週）

### インフラ
- [ ] CloudFormation テンプレート完成 (`gpu_image_gen_stack.yaml`)
- [ ] S3 バケット作成
- [ ] SNS トピック作成 + メール登録
- [ ] IAM ロール/ポリシー作成
- [ ] Launch Template 作成
- [ ] CloudWatch Alarm + Lambda (1.5h自動停止) 構築
- [ ] EventBridge ルール (起動/停止検知→SNS) 構築

### GPU インスタンスセットアップ
- [ ] g4dn.xlarge スポット初回起動
- [ ] `setup_gpu_env.sh` 実行 (NVIDIA + CUDA + Python)
- [ ] FLUX.1-schnell モデルダウンロード (~12GB)
- [ ] テスト画像生成 (`generate_images.py --test`)
- [ ] AMI 作成 (セットアップ済み環境を保存)

### スクリプト
- [ ] `generate_images.py` — 画像バッチ生成
- [ ] `create_prompts.py` — プロンプトJSON生成 (Groq)
- [ ] `setup_gpu_env.sh` — GPU環境セットアップ
- [ ] `startup.sh` — EC2起動時自動実行

---

## Phase 2: 既存パイプライン統合

### youtube_pipeline.py 改修
- [ ] Step 4 改修: S3からAI画像取得 (Pexelsフォールバック)
- [ ] Step 6 改修: サムネイルにAI背景画像使用 (オプション)
- [ ] S3画像取得ユーティリティ関数追加
- [ ] .env に `AI_IMAGE_S3_BUCKET` 追加

### 運用フロー確立
- [ ] 月初バッチ: create_prompts.py → S3 → g4dn起動 → 画像生成 → S3
- [ ] 日次: t4g.medium が S3から画像取得 → 動画パイプライン実行

---

## Phase 3: 品質向上・拡張（Month 2〜）

- [ ] LoRA 学習環境構築 (固定キャラクター)
- [ ] Ken Burns 動画化パイプライン
- [ ] サムネイル A/B テスト自動生成
- [ ] マルチチャネル展開 (Instagram/X/Pinterest)

---

## 完了済み

- [x] マネタイズ調査 (`04_RESEARCH/2026-03-06_AI_image_monetization_research.md`)
- [x] 技術パイプライン調査 (`04_RESEARCH/2026-03-06_AI_image_generation_SNS_pipeline.md`)
- [x] 統合PLAN.md作成 (`03_PROJECTS/ai_image_business/PLAN.md`)
- [x] SPEC.md作成 (`03_PROJECTS/ai_image_business/SPEC.md`)
