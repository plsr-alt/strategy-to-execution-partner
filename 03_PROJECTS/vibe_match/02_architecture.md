# VibeMatch MVP アーキテクチャ設計書

> 作成日: 2026-03-01 | ステータス: ドラフト

---

## 1. 全体構成図

```
┌─────────────────────────────────────────────────────┐
│                    Client Layer                      │
│  ┌──────────────────────────────────────────────┐   │
│  │   React Native (Expo) / iOS + Android        │   │
│  │   - TypeScript                               │   │
│  │   - React Navigation                         │   │
│  │   - TanStack Query (API state)               │   │
│  └──────────────┬───────────────────────────────┘   │
└─────────────────┼───────────────────────────────────┘
                  │ HTTPS (TLS 1.3)
                  ▼
┌─────────────────────────────────────────────────────┐
│                   Edge / Gateway                     │
│  ┌──────────────────────────────────────────────┐   │
│  │   Cloudflare (CDN + WAF + DDoS)              │   │
│  │   → API Gateway (rate limit, auth)           │   │
│  └──────────────┬───────────────────────────────┘   │
└─────────────────┼───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│                  Backend Services                    │
│                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  │
│  │  App Server   │  │  AI Service  │  │  Chat    │  │
│  │  (Go/Node)    │  │  (FastAPI)   │  │  (WS)   │  │
│  │              │  │              │  │          │  │
│  │ - Auth       │  │ - 顔検出     │  │ - Pub/Sub│  │
│  │ - Profile    │  │ - 品質判定   │  │ - 通報   │  │
│  │ - Match      │  │ - 印象推定   │  │          │  │
│  │ - Recommend  │  │ - フィルタ   │  │          │  │
│  │ - Payment    │  │              │  │          │  │
│  └──────┬───────┘  └──────┬───────┘  └────┬─────┘  │
│         │                 │                │        │
│  ┌──────┴─────────────────┴────────────────┴─────┐  │
│  │              Data Layer                        │  │
│  │  ┌─────────┐ ┌─────────┐ ┌──────────────────┐│  │
│  │  │PostgreSQL│ │ Redis   │ │ S3 (画像)        ││  │
│  │  │         │ │         │ │ + CloudFront CDN  ││  │
│  │  │- users  │ │- session│ │                   ││  │
│  │  │- matches│ │- cache  │ │ 暗号化(AES-256)   ││  │
│  │  │- chats  │ │- rate   │ │ 30日自動削除      ││  │
│  │  │- logs   │ │- queue  │ │                   ││  │
│  │  └─────────┘ └─────────┘ └──────────────────┘│  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

---

## 2. 技術スタック選定

### 2.1 クライアント

| 項目 | 選定 | 理由 |
|------|------|------|
| フレームワーク | **React Native (Expo)** | iOS/Android同時、Web Preview可、OTAアップデート |
| 言語 | TypeScript | 型安全 |
| 状態管理 | Zustand + TanStack Query | 軽量、サーバー状態分離 |
| ナビゲーション | React Navigation v7 | 標準的 |
| UI | Tamagui or NativeWind | クロスプラットフォームスタイリング |
| カメラ/画像 | expo-image-picker + expo-image-manipulator | トリミング・リサイズ |

### 2.2 バックエンド

| 項目 | 選定 | 理由 |
|------|------|------|
| App Server | **Go (Fiber/Echo)** | 高パフォーマンス、並行処理、型安全 |
| AI Service | **Python (FastAPI)** | ML/DLエコシステム、推論特化 |
| Chat | **Go + WebSocket** (gorilla/websocket) | 低レイテンシ |
| 認証 | Firebase Auth or Supabase Auth | SMS/SNSログイン即時構築 |
| DB | **PostgreSQL 16** (Supabase or RDS) | JSONB対応、実績 |
| キャッシュ | **Redis 7** (Upstash or ElastiCache) | 推薦キャッシュ、セッション、レート制限 |
| ストレージ | **S3** + CloudFront | 画像、プリサインURL |
| キュー | Redis Streams or SQS | 診断ジョブ、削除キュー |

### 2.3 AI推論

| 項目 | 選定 | 理由 |
|------|------|------|
| 顔検出 | **MediaPipe Face Detection** or MTCNN | 軽量、高速 |
| 品質判定 | ルールベース（明るさ/ブレ/顔サイズ/人数） | シンプル＆確実 |
| 印象推定 | **CLIP (ViT-L/14)** + カスタムプロンプト | → 05_tech_research.md で詳細確定 |
| フィルタ | ルールベース禁止語辞書 + LLMガードレール | 禁止推定の防止 |
| 実行環境 | **AWS Lambda (GPU)** or **Modal** | サーバーレスGPU、コスト効率 |

### 2.4 インフラ

| 項目 | 選定 | 理由 |
|------|------|------|
| ホスティング | **AWS** (ECS Fargate or Lambda) | スケーラビリティ |
| CDN/WAF | **Cloudflare** | 無料プランあり、DDoS防御 |
| CI/CD | GitHub Actions | 標準的 |
| 監視 | Datadog or Grafana Cloud (Free) | APM + ログ |
| IaC | Terraform or SST (Serverless Stack) | 再現性 |

---

## 3. データベース設計（主要テーブル）

```sql
-- ユーザー
users (
  id UUID PK,
  phone_hash TEXT,          -- SMS認証ハッシュ
  nickname TEXT,
  gender TEXT,
  seeking_gender TEXT,
  age INT,
  prefecture TEXT,
  purpose TEXT,             -- dating/marriage
  bio TEXT,
  created_at TIMESTAMPTZ,
  deleted_at TIMESTAMPTZ    -- 論理削除
)

-- 写真
photos (
  id UUID PK,
  user_id UUID FK → users,
  s3_key TEXT,              -- 暗号化パス
  status TEXT,              -- uploaded/processed/deleted
  quality_score INT,
  expires_at TIMESTAMPTZ,   -- 30日後自動削除
  created_at TIMESTAMPTZ
)

-- AI診断結果
diagnoses (
  id UUID PK,
  user_id UUID FK → users,
  photo_ids UUID[],
  model_version TEXT,
  overall_confidence INT,
  tags JSONB,               -- [{id, label, prob}]
  explanation JSONB,        -- [{type, text}]
  created_at TIMESTAMPTZ
)

-- いいね
likes (
  id UUID PK,
  from_user_id UUID FK → users,
  to_user_id UUID FK → users,
  mode TEXT,                -- unified/complement
  reason_pick TEXT,
  created_at TIMESTAMPTZ,
  UNIQUE(from_user_id, to_user_id)
)

-- マッチ
matches (
  id UUID PK,
  user_a UUID FK → users,
  user_b UUID FK → users,
  matched_at TIMESTAMPTZ,
  status TEXT               -- active/unmatched/blocked
)

-- チャット
messages (
  id UUID PK,
  match_id UUID FK → matches,
  sender_id UUID FK → users,
  text TEXT,
  created_at TIMESTAMPTZ
)

-- 通報
reports (
  id UUID PK,
  reporter_id UUID FK → users,
  target_user_id UUID FK → users,
  category TEXT,
  detail TEXT,
  status TEXT,              -- pending/reviewed/actioned
  created_at TIMESTAMPTZ
)

-- 推薦キャッシュ（Redis）
-- key: reco:{user_id}:{mode}
-- value: [{user_id, score, reasons, tags_preview}]
-- TTL: 1h（いいね/スキップで即時更新）

-- 監査ログ
audit_logs (
  id BIGSERIAL PK,
  actor_id UUID,
  action TEXT,
  target_type TEXT,
  target_id UUID,
  detail JSONB,
  ip TEXT,
  created_at TIMESTAMPTZ
)
```

---

## 4. 認証フロー

```
1. ユーザー → POST /v1/auth/sms/request {phone}
2. サーバー → Twilio/Firebase で SMS送信
3. ユーザー → POST /v1/auth/sms/verify {code}
4. サーバー → JWT発行 (access: 15min, refresh: 30day)
5. 以降: Authorization: Bearer {access_token}
6. リフレッシュ: POST /v1/auth/refresh {refresh_token}
```

Apple/Google SSO:
```
1. クライアント → Apple/Google SDKでIDトークン取得
2. POST /v1/auth/social {provider, id_token}
3. サーバー → トークン検証 → JWT発行
```

---

## 5. AI診断パイプライン

```
写真アップロード
    ↓
[1. 顔検出] MediaPipe → 顔領域切り出し
    ↓ (顔なし → エラー返却)
[2. 品質判定] ルールベース
    - 明るさ閾値
    - ブレ検出（Laplacian variance）
    - 顔サイズ（画像の20%以上）
    - 人数チェック（1人のみ）
    - サングラス/マスク検出
    ↓ (NG → 具体的理由を返却)
[3. 特徴抽出] CLIP ViT-L/14
    - 顔領域を224x224にリサイズ
    - image embedding取得 (768dim)
    ↓
[4. 印象タグ推定]
    - 各タグのテキストembeddingとcos類似度
    - Top5を確率正規化
    - confidence = Top1確率 × 品質スコア
    ↓
[5. ガードレール]
    - 禁止タグフィルタ（人種、年齢等）
    - 有名人名検出（辞書マッチ → ブロック）
    - 出力サニタイズ
    ↓
[6. 結果保存] → diagnoses テーブル
    ↓
[7. レスポンス返却]
```

---

## 6. レコメンドエンジン

### 統一感スコア
```python
unified_score = 1 - cosine_distance(user_a.tag_vector, user_b.tag_vector)
# tag_vector = [tag1_prob, tag2_prob, ..., tagN_prob]
```

### 補完スコア
```python
complement_score = sum(
    complement_matrix[tag_a][tag_b] * prob_a * prob_b
    for tag_a, prob_a in user_a.tags
    for tag_b, prob_b in user_b.tags
)
# complement_matrix: 事前定義の相性行列 (06_tag_taxonomy.md)
```

### 最終スコア
```python
final_score = (
    0.40 * type_compat      # 統一感 or 補完
  + 0.25 * preference_fit    # 好み学習（SHOULD: βから）
  + 0.15 * activity_fit      # アクティブ度
  + 0.10 * diversity_bonus   # 同タイプ出し過ぎ抑制
  + 0.10 * recency_bonus     # 最終ログイン
) * constraint_filter         # 距離/年齢/目的/ブロック (0 or 1)
```

### バッチ vs リアルタイム
- **MVP**: バッチ（1h毎にRedisキャッシュ更新） + いいね/スキップで即時除外
- **β以降**: オンライン特徴量ストア + リアルタイム再スコアリング

---

## 7. セキュリティ設計

| 脅威 | 対策 |
|------|------|
| 画像流出 | S3暗号化(SSE-KMS) + プリサインURL(15min有効) + CDN署名 |
| なりすまし | JWT + リフレッシュトークンローテーション |
| スクレイピング | WAF + レート制限 + User-Agentチェック |
| SQLインジェクション | ORM/パラメタライズドクエリ |
| IDOR | user_idをJWTから取得、パスパラメータのuser_id検証 |
| レート制限 | Redis: いいね50/day, 画像アップ10/day, SMS5/h |
| 個人情報 | phone_hashのみ保存、ログにPIIマスキング |

---

## 8. コスト見積もり（MVP月額）

| 項目 | サービス | 月額見積 |
|------|---------|---------|
| App Server | ECS Fargate (0.5vCPU x 2) | $30-50 |
| AI推論 | Modal / Lambda GPU | $50-100 (1000診断/月) |
| DB | Supabase Pro or RDS t3.small | $25-50 |
| Redis | Upstash Serverless | $10-20 |
| S3 + CDN | S3 + CloudFront | $5-10 |
| SMS認証 | Twilio | $10-20 (500認証/月) |
| ドメイン + SSL | Cloudflare | $0 |
| 監視 | Grafana Cloud Free | $0 |
| **合計** | | **$130-250/月** |

※ ユーザー数1000人以下のMVP想定。スケール時はAutoScalingで段階増。

---

## 9. デプロイ戦略

### MVP
```
GitHub → GitHub Actions → Docker Build → ECR → ECS Fargate
                                              → Lambda (AI Service)
```

### 環境
| 環境 | 用途 |
|------|------|
| dev | 開発・テスト |
| staging | QA・受入テスト |
| prod | 本番 |

### リリースフロー
1. feature branch → PR → レビュー → merge to main
2. main merge → staging自動デプロイ
3. staging検証OK → prod手動デプロイ（GitHub Release tag）
