# AI画像生成GPU環境 — 仕様書 (SPEC.md)

**作成日**: 2026-03-06
**関連**: `03_PROJECTS/youtube_automation/` (既存パイプライン)

---

## 1. 概要

g6.xlarge スポットインスタンスで FLUX.2 [klein] 4B を実行し、YouTube動画用のAI画像を大量生成。
生成画像は S3 経由で既存 t4g.medium パイプラインに受け渡す。

---

## 2. アーキテクチャ

```
[手動起動] g6.xlarge (スポット / NVIDIA L4 24GB)
    │
    ├── FLUX.2 [klein] 4B で画像バッチ生成
    ├── Wan 2.2 (1.3B) で image-to-video 変換（オプション）
    ├── Ken Burns 効果で動画クリップ生成（オプション）
    ├── LoRA 学習（将来対応）
    │
    ├── → S3 バケット (ai-image-gen-{account-id}) にアップロード
    │
    ├── CloudWatch Alarm: 起動後1.5hで自動停止
    └── SNS通知: 起動時 / 停止時 / CW Alarm発火時

[自動] t4g.medium (既存パイプライン)
    │
    ├── S3 から画像取得 (collect_footage の代替)
    └── 通常通り動画編集→YouTube アップロード
```

---

## 3. ネットワーク構成

**既存 t4g.medium と同じ VPC / サブネットに配置**

| 項目 | 設定 |
|------|------|
| VPC | 既存と同一 |
| サブネット | 既存 t4g.medium と同じパブリックサブネット |
| パブリックIP | 不要（SSM Session Manager 経由でアクセス） |
| セキュリティグループ | SSH不要。S3 は VPC エンドポイント or NAT経由 |

**注**: パブリックサブネットに配置するが、パブリックIPは不要。
SSMでの接続 + S3アクセスのみ。
ただし、PyPI等からパッケージインストールする初期セットアップ時のみ
パブリックIPを一時的に付与する（or NAT Gateway経由）。

**簡易版**: 既存と同じ構成（パブリックIP付き）でOK。
月1.5hしか稼働しないので、SGで十分にガード。

---

## 4. インスタンス仕様

| 項目 | 値 |
|------|-----|
| インスタンスタイプ | `g6.xlarge` |
| GPU | NVIDIA L4 (24GB VRAM) |
| vCPU | 4 |
| RAM | 16GB |
| ストレージ | 100GB gp3 (FLUX.2 klein ~8GB + Wan 2.2 ~3GB + 生成画像) |
| AMI | Amazon Linux 2023 (x86_64) |
| 購入オプション | スポットインスタンス |
| スポット価格 | ~$0.09-0.15/h (リージョン依存、東京 ~$0.12/h) |
| 課金単位 | **秒単位** (最小1分) |

### g4ad.xlarge を選ばない理由
- AMD Radeon Pro V520 (8GB VRAM)
- **CUDA非対応** → PyTorch/FLUX.2/Stable Diffusion が動作しない
- AI画像生成はNVIDIA CUDA必須

### g6.xlarge を選ぶ理由 (vs g4dn.xlarge)
- g6.xlarge: NVIDIA L4 (24GB VRAM) — FLUX.2 klein (~8GB) + Wan 2.2 (~3GB) を余裕で搭載
- g4dn.xlarge: NVIDIA T4 (16GB VRAM) — 旧世代、スポット価格も g6 と大差なし
- L4 は T4 の約2-3倍の推論性能（Ada Lovelace世代）

---

## 5. ソフトウェア構成 (AMI セットアップ)

```bash
# 1. NVIDIA ドライバ + CUDA
nvidia-driver-550+ (L4対応) + CUDA 12.x

# 2. Python 環境
python3.11 + pip

# 3. AI画像生成 (共通)
torch==2.3+ (CUDA 12.x)
diffusers  (HuggingFace)
transformers
accelerate
safetensors

# 4. FLUX.2 [klein] 4B (Apache 2.0)
black-forest-labs/FLUX.2-klein (HuggingFace からダウンロード)
→ 約 8GB (fp16)
→ L4 で ~2-6秒/枚 の高速生成

# 5. Wan 2.2 (1.3B) — image-to-video (Apache 2.0)
Wan-AI/Wan2.2-T2V-1.3B (HuggingFace)
→ 約 3GB、~8GB VRAM で動作
→ AI生成画像 → 短尺動画クリップへの変換

# 6. Z-Image-Turbo (オプション — 日本語テキスト入りサムネイル)
→ 日本語テキストレンダリング対応モデル
→ サムネイル生成に特化して利用

# 7. 動画化 (Ken Burns等)
opencv-python
moviepy

# 8. AWS連携
boto3
awscli
```

---

## 6. 画像生成バッチスクリプト

### 入力
```json
// S3: s3://ai-image-gen-bucket/prompts/pending.json
{
  "batch_id": "20260306_001",
  "prompts": [
    {
      "id": "vid001_bg1",
      "prompt": "A futuristic Tokyo skyline at sunset, cyberpunk style, 16:9 aspect ratio",
      "negative_prompt": "blurry, low quality",
      "width": 1280,
      "height": 720,
      "num_images": 1
    },
    {
      "id": "vid001_bg2",
      "prompt": "Japanese businessman analyzing financial charts on holographic display",
      "negative_prompt": "blurry, low quality",
      "width": 1280,
      "height": 720,
      "num_images": 1
    }
  ]
}
```

### 出力
```
S3: s3://ai-image-gen-bucket/output/{batch_id}/
├── vid001_bg1_0.png
├── vid001_bg2_0.png
└── manifest.json  ← 生成結果メタデータ
```

### 処理フロー
```
1. S3 から prompts/pending.json を取得
2. FLUX.2 [klein] 4B でバッチ生成
3. (オプション) Wan 2.2 で image-to-video 変換
4. 生成画像/動画を S3 にアップロード
5. manifest.json を S3 にアップロード
6. pending.json を processed/ に移動
```

---

## 7. CloudWatch Alarm (1.5h 自動停止)

| 項目 | 設定 |
|------|------|
| メトリクス | `StatusCheckFailed` (カスタムではなく起動時間ベース) |
| 方式 | **EventBridge + Lambda** (起動イベント検知 → 1.5h後にStop) |
| トリガー | EC2 State Change → `running` |
| アクション | 1.5h (5400秒) 後に `ec2:StopInstances` |
| フォールバック | CloudWatch Alarm (CPUUtilization < 5% for 30min → Stop) |

### 実装方式
```
EC2 State Change (running)
  → EventBridge Rule
    → Step Functions (Wait 5400秒 → Lambda Stop)
```

※ Step Functions より簡易な方法:
```
EC2 State Change (running)
  → Lambda:
    1. SNS通知「GPU起動」
    2. CloudWatch Alarm 作成 (1.5h後にStop)
```

---

## 8. SNS通知

| イベント | 通知内容 |
|---------|---------|
| **起動時** | 「GPU インスタンス起動しました。1.5h後に自動停止します」 |
| **停止時** | 「GPU インスタンス停止しました。コスト: 約$X.XX」 |
| **CW Alarm 発火時** | 「⚠️ 1.5h経過のため自動停止しました」 |

通知先: メール (Amazon SNS → Email)

---

## 9. 既存パイプラインとの統合

### 変更箇所: `youtube_pipeline.py` Step 4

**Before**: Pexels API で映像素材を取得
**After**: S3 から AI生成画像を取得 (Pexels をフォールバック)

```python
def collect_footage(keywords, num_clips=5):
    # 1. まず S3 から AI 生成画像を取得
    ai_images = fetch_ai_images_from_s3(batch_id)
    if ai_images:
        return ai_images

    # 2. なければ Pexels API にフォールバック
    return collect_footage_pexels(keywords, num_clips)
```

---

## 10. S3 バケット構成

```
s3://ai-image-gen-{account-id}/
├── prompts/
│   ├── pending.json      ← t4g.medium が配置
│   └── processed/        ← 処理済み
├── output/
│   └── {batch_id}/       ← g6.xlarge が配置
│       ├── *.png
│       ├── *.mp4          ← Wan 2.2 動画出力
│       └── manifest.json
└── models/               ← LoRA モデル保存 (将来)
```

---

## 11. コスト試算

### 月次 (月2-3回、各1.5h稼働)
| 項目 | コスト |
|------|-------|
| g6.xlarge スポット (1.5h × 2-3回) | $0.27-0.54 (≒50-80円) |
| S3 (1GB保存 + 転送) | $0.03 |
| CloudWatch + SNS | $0.00 (無料枠内) |
| **合計** | **約50-80円/月** |

### 生成能力
| 稼働時間 | 生成枚数 | 備考 |
|---------|---------|------|
| 1.5h | 1000-2000枚 | FLUX.2 klein on L4: ~2-6秒/枚 (旧T4では10-15秒/枚) |
| — | YouTube 8本分 × 3枚 = 24枚で十分 | 余剰分はストック可 |

---

## 12. セキュリティ

| 項目 | 対策 |
|------|------|
| SSH | 不要（SSM Session Manager） |
| SG | アウトバウンドのみ（S3, PyPI, HuggingFace, Wan-AI） |
| IAM | 最小権限（S3 put/get + EC2 stop のみ） |
| HuggingFace Token | SSM Parameter Store に保存 |
| スポット中断 | データは S3 に即アップロード → 中断されても画像は保持 |

---

## 13. デプロイ手順

### Phase 1: 初回セットアップ
```bash
# 1. CloudFormation でインフラ構築
aws cloudformation deploy --template-file gpu_image_gen_stack.yaml ...

# 2. g6.xlarge を手動起動
aws ec2 run-instances --launch-template ...

# 3. SSH/SSM で接続 → セットアップスクリプト実行
./setup_gpu_env.sh

# 4. モデルダウンロード (初回のみ)
#    - FLUX.2 [klein] 4B: ~8GB
#    - Wan 2.2 (1.3B): ~3GB
#    - Z-Image-Turbo: (オプション)
python download_model.py

# 5. テスト生成
python generate_images.py --test

# 6. AMI 作成 (次回以降は AMI から起動)
aws ec2 create-image --instance-id ... --name "ai-image-gen-v1"
```

### Phase 2: 通常運用
```bash
# 1. 手動起動 (AMI から)
aws ec2 run-instances --launch-template ...

# 2. 自動で画像生成 → S3 アップロード (User Data)
# 3. 1.5h後に自動停止 (CloudWatch)
# 4. t4g.medium が S3 から取得 → 動画パイプライン
```

---

## 14. ファイル一覧

| ファイル | 用途 |
|---------|------|
| `gpu_image_gen_stack.yaml` | CloudFormation テンプレート |
| `setup_gpu_env.sh` | GPU環境セットアップスクリプト |
| `generate_images.py` | AI画像生成バッチスクリプト |
| `s3_sync.py` | S3 アップロード/ダウンロードユーティリティ |
| `SPEC.md` | 本仕様書 |
| `TODO.md` | タスク管理 |
