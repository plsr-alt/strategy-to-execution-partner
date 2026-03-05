# VibeMatch MVP 実装ガイド（ステップバイステップ）

> 作成日: 2026-03-01（検証ファースト版に改訂）
> 対象: 1人開発、iOS（TestFlight）、初期費最小
> **方針: まず需要を検証（¥0）→ Go判定後に開発（¥17,300）**

---

## 全体フロー

```
Phase 0: 需要検証（2週間 / ¥0）
  ↓ Go判定
Phase 1: 環境構築（1週間 / ¥17,300）
  ↓
Phase 2-6: 開発（11週間 / 月¥150-4,500）
  ↓
TestFlight配布 → クローズドβ
```

---

## ★ PHASE 0: 需要検証（あなたのアクション）⏱️ 2週間 / ¥0

> 詳細: `09_validation_first.md`

### あなたがやること一覧

| # | タスク | 所要時間 | 参照ファイル |
|---|--------|---------|-------------|
| 0-1 | Googleフォームで先行登録LP作成 | 10分 | `12_lp_google_form.md` |
| 0-2 | X投稿 #1（問題提起）を投稿 | 5分 | `10_x_posts_validation.md` |
| 0-3 | X投稿 #4（タグ紹介）を投稿 | 5分 | 同上 |
| 0-4 | X投稿 #3（投票）を投稿 | 5分 | 同上 |
| 0-5 | X投稿 #5（無料診断オファー）★最重要 | 5分 | 同上 |
| 0-6 | DMで診断希望者の写真を受け取り → 手動診断 | 1件5分 | `11_manual_diagnosis_guide.md` |
| 0-7 | フィードバック質問を送信 | 1件2分 | 同上 |
| 0-8 | 2週間後にKPIを集計 → Go/No-Go判定 | 30分 | `09_validation_first.md` |

### Go基準（1つでも満たせばGo）
- 先行登録 **50人以上**
- X投票「使いたい」 **60%以上**
- DM診断希望 **20人以上**

### 並行: AI PoC テスト（任意）
```bash
# WSLで実行。手動診断の裏付けに使える
cd /mnt/c/Users/tshibasaki/Desktop/etc/work/task/03_PROJECTS/vibe_match/src/services/ai
python3 -m venv .venv && source .venv/bin/activate
pip install open-clip-torch torch Pillow numpy insightface onnxruntime
python poc_test.py --photo test_photo.jpg
```

---

## ★ Go判定後: PHASE 1 に進む

---

## PHASE 1: 事前準備（あなたのアクション）⏱️ 30分

### 1-1. アカウント作成（すべて無料）

| # | サービス | URL | やること |
|---|---------|-----|---------|
| 1 | **GitHub** | https://github.com | アカウント作成（あれば不要） |
| 2 | **Supabase** | https://supabase.com | GitHub連携でサインアップ → New Project作成 |
| 3 | **Expo** | https://expo.dev | GitHub連携でサインアップ |
| 4 | **Cloudflare** | https://dash.cloudflare.com | メールでサインアップ |
| 5 | **Google Cloud** | https://console.cloud.google.com | Cloud Run用。無料枠$300あり |

### 0-2. Apple Developer Program 登録 ⏱️ 1-2日（審査待ち）

1. https://developer.apple.com/programs/ にアクセス
2. 「Enroll」→ 個人で登録（¥15,800/年）
3. Apple IDでサインイン → 支払い → **審査完了まで24-48時間**
4. 完了後、App Store Connect にアクセス可能になる

> ⚠️ **これが一番時間がかかる。最初にやること！**

### 0-3. ドメイン取得 ⏱️ 5分

1. https://www.onamae.com/ or https://domains.google/ にアクセス
2. `vibematch.jp` or `vibematch.app` を検索・購入（¥1,500前後）
3. ネームサーバーをCloudflareに変更（後で設定）

### 0-4. ローカル開発環境 ⏱️ 15分

```bash
# Node.js（v20推奨）
# 公式サイトからインストール: https://nodejs.org/

# Expo CLI
npm install -g expo-cli eas-cli

# Python（WSL内で実行）
# WSLターミナルで:
sudo apt update && sudo apt install python3.11 python3.11-venv python3-pip

# Git（Windowsに入ってるはず）
git --version
```

---

## STEP 1: リポジトリ作成 & プロジェクト初期化 ⏱️ 15分

### 1-1. GitHubリポジトリ作成

1. https://github.com/new にアクセス
2. Repository name: `vibematch`
3. Private にチェック
4. 「Create repository」

### 1-2. ローカルにクローン & 構造作成

```bash
cd ~/Desktop/etc/work
git clone https://github.com/<YOUR_USERNAME>/vibematch.git
cd vibematch
```

> 以降の構造作成・コード生成は Claude Code が実行済み（STEP 1-3参照）

### 1-3. 生成済みファイル一覧

```
vibematch/
├── apps/
│   └── mobile/          ← Expo (React Native) アプリ
│       ├── app/         ← 画面ファイル（Expo Router）
│       ├── components/  ← UIコンポーネント
│       ├── lib/         ← Supabase client, API呼び出し
│       ├── app.json
│       └── package.json
├── services/
│   └── ai/              ← FastAPI AI推論サービス
│       ├── app/
│       │   ├── main.py
│       │   ├── face_detector.py
│       │   ├── impression_tagger.py
│       │   ├── tags.py          ← タグ定義 & CLIPプロンプト
│       │   └── guardrails.py    ← 禁止出力フィルタ
│       ├── requirements.txt
│       └── Dockerfile
├── supabase/
│   └── migrations/      ← DBマイグレーション
│       └── 001_initial_schema.sql
├── .github/
│   └── workflows/       ← CI/CD
├── .gitignore
└── README.md
```

---

## STEP 2: Supabase セットアップ ⏱️ 20分

### 2-1. プロジェクト作成

1. https://supabase.com/dashboard にログイン
2. 「New Project」クリック
3. 設定:
   - Name: `vibematch`
   - Database Password: 強いパスワードを設定（**メモしておく**）
   - Region: `Northeast Asia (Tokyo)` ★
   - Plan: Free
4. 「Create new project」→ 2分ほど待つ

### 2-2. API Key取得

1. 左メニュー「Project Settings」→「API」
2. 以下をメモ:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **anon public key**: `eyJhbGc...`（フロントエンドで使う）
   - **service_role key**: `eyJhbGc...`（バックエンドのみ。公開厳禁）

### 2-3. DBマイグレーション実行

1. 左メニュー「SQL Editor」を開く
2. 生成済みの `supabase/migrations/001_initial_schema.sql` の内容をコピペ
3. 「Run」をクリック

### 2-4. Auth設定

1. 左メニュー「Authentication」→「Providers」
2. 以下を有効化:
   - **Apple**: Apple Developer PortalでService ID作成 → Client ID/Secretを入力
   - **Google**: Google Cloud ConsoleでOAuth設定 → Client ID/Secretを入力
3. （βから）Phone: Twilio SIDとAuthTokenを入力

### 2-5. Storage設定

1. 左メニュー「Storage」→「New Bucket」
2. Bucket名: `photos`
3. Public: OFF（プリサインURL経由でアクセス）
4. File size limit: `5MB`
5. Allowed MIME types: `image/jpeg, image/png, image/webp`

---

## STEP 3: モバイルアプリ起動確認 ⏱️ 10分

### 3-1. 依存インストール & 起動

```bash
cd vibematch/apps/mobile
npm install
npx expo start
```

### 3-2. iPhone実機で確認

1. iPhoneに「Expo Go」アプリをApp Storeからインストール
2. ターミナルに表示されるQRコードをiPhoneカメラで読み取る
3. アプリが起動すればOK！

### 3-3. 環境変数設定

`apps/mobile/.env` ファイルを作成:

```
EXPO_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
EXPO_PUBLIC_SUPABASE_ANON_KEY=eyJhbGc...
EXPO_PUBLIC_AI_API_URL=https://ai.vibematch.app  # 後で設定
```

---

## STEP 4: AI推論サービスのデプロイ ⏱️ 30分

### 4-1. ローカルテスト（WSL）

```bash
cd vibematch/services/ai
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# CLIPモデルの初回ダウンロード（約2GB、初回のみ）
python -c "import open_clip; open_clip.create_model_and_transforms('ViT-L-14', pretrained='openai')"

# サーバー起動
uvicorn app.main:app --reload --port 8000

# テスト（別ターミナルで）
curl -X POST http://localhost:8000/v1/face/diagnose \
  -F "photo=@test_photo.jpg"
```

### 4-2. Google Cloud Runにデプロイ

```bash
# Google Cloud CLIインストール（初回のみ）
# https://cloud.google.com/sdk/docs/install

# ログイン
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Cloud Runにデプロイ（Dockerfileから自動ビルド）
cd vibematch/services/ai
gcloud run deploy vibematch-ai \
  --source . \
  --region asia-northeast1 \
  --memory 2Gi \
  --cpu 2 \
  --min-instances 0 \
  --max-instances 3 \
  --allow-unauthenticated
```

> デプロイ完了後、URLが表示される（例: `https://vibematch-ai-xxxxx-an.a.run.app`）
> → `.env` の `EXPO_PUBLIC_AI_API_URL` に設定

---

## STEP 5: TestFlight配布 ⏱️ 20分

### 5-1. EAS Build設定

```bash
cd vibematch/apps/mobile

# EASにログイン
eas login

# ビルド設定初期化
eas build:configure

# iOSビルド（クラウドで実行、ローカルMac不要！）
eas build --platform ios --profile preview
```

> ビルドは10-20分かかる。完了するとダウンロードリンクが届く。

### 5-2. TestFlightに配布

```bash
# App Store Connectに送信
eas submit --platform ios --profile preview
```

### 5-3. テスターを招待

1. https://appstoreconnect.apple.com にログイン
2. 「My Apps」→「VibeMatch」→「TestFlight」
3. 「Internal Testing」→「+」→ メールアドレスでテスター招待
4. テスターがiPhoneでTestFlightアプリを開き、インストール

---

## STEP 6: Cloudflare設定 ⏱️ 10分

### 6-1. ドメイン追加

1. Cloudflareダッシュボード → 「Add a site」
2. ドメイン入力（例: vibematch.app）
3. Free planを選択
4. 表示されるネームサーバーを、ドメイン管理画面（お名前.com等）で設定

### 6-2. DNS設定

| Type | Name | Content | Proxy |
|------|------|---------|-------|
| CNAME | api | Cloud RunのURL | OFF |
| CNAME | ai | Cloud RunのURL | OFF |

---

## STEP 7: 動作確認チェックリスト ⏱️ 15分

| # | 確認項目 | 方法 | OK |
|---|---------|------|---|
| 1 | アプリがExpo Goで起動する | QRコード読み取り | [ ] |
| 2 | Apple/Googleログインできる | 実機で操作 | [ ] |
| 3 | プロフィールが保存される | 入力→再起動→表示確認 | [ ] |
| 4 | 写真をアップロードできる | カメラ/ギャラリーから | [ ] |
| 5 | AI診断が返ってくる | 写真アップ後にタグ表示 | [ ] |
| 6 | 推薦カードが表示される | 探索画面を開く | [ ] |
| 7 | いいね/スキップが動く | カード操作 | [ ] |
| 8 | マッチが成立する | テストユーザー2人で相互いいね | [ ] |
| 9 | チャットが送受信できる | マッチ後にメッセージ | [ ] |
| 10 | TestFlightで配布できる | EAS build & submit | [ ] |

---

## 開発→リリースのタイムライン（目安）

```
Week 1-2:  STEP 0-3（環境構築 + アプリ骨格 + Supabase接続）
Week 3-4:  認証 + プロフィール + 写真アップロード
Week 5-6:  AI診断エンジン + 診断画面 ★最重要
Week 7-8:  レコメンド + マッチング + 探索画面
Week 9-10: チャット + 通報/ブロック
Week 11:   課金導線 + 設定画面
Week 12:   テスト + TestFlight配布 + クローズドβ開始
```

---

## 困ったときのトラブルシューティング

| 症状 | 対処 |
|------|------|
| Expo Goで繋がらない | 同じWiFiか確認。`npx expo start --tunnel` を試す |
| Supabase接続エラー | `.env` のURL/Keyが正しいか確認。Row Level Security有効時はポリシー確認 |
| CLIPモデルのダウンロードが遅い | WSLのネットワーク設定確認。`pip install huggingface_hub` で事前DL |
| EAS Buildが失敗する | `eas build` のログを確認。よくある原因: app.jsonの設定ミス |
| Cloud Runがタイムアウト | メモリ不足の可能性。`--memory 4Gi` に増やす |
