# storyboard-gen

日本語台本 → カット分解 → 縦長(9:16)画像一括生成 → ZIPダウンロード

## 機能

- 日本語台本を入力 → GPT-4o が自動カット分解（最大30カット）
- カットごとに画像生成プロンプト作成（テキスト余白位置も指定）
- DALL-E 3 で 9:16 縦画像を一括生成
- 生成状況をリアルタイムでポーリング表示
- 完了後 ZIP ダウンロード

## EC2 デプロイ（最短手順）

詳細は [DEPLOY.md](./DEPLOY.md) を参照。

```bash
unzip storyboard-gen.zip && cd storyboard-gen
cp .env.example .env
nano .env   # OPENAI_API_KEY を設定
docker compose up -d --build
# → http://<EC2_IP>:3000 でアクセス
```

## ローカル開発

### 必要なもの

- Node.js 20+
- npm
- OpenAI API Key

### セットアップ

```bash
git clone <this-repo>
cd storyboard-gen

npm install

cp .env.example .env.local
# .env.local を編集して OPENAI_API_KEY を設定
# DATA_DIR をローカルパスに変更（例: DATA_DIR=./data）

npm run dev
# → http://localhost:3000
```

### 環境変数（.env.local）

```
OPENAI_API_KEY=sk-...
DATA_DIR=./data          # ローカルは相対パスでOK
JOB_TTL_DAYS=7
MAX_SCRIPT_LENGTH=5000
DEFAULT_MAX_CUTS=15
MAX_CUTS_LIMIT=30
```

### ビルド確認

```bash
npm run build
NODE_ENV=production DATA_DIR=./data node .next/standalone/server.js
```

## API

| Method | Path | 説明 |
|--------|------|------|
| `POST` | `/api/jobs` | ジョブ作成・処理開始 |
| `GET`  | `/api/jobs/:id` | ジョブ状態取得（ポーリング用） |
| `GET`  | `/api/jobs/:id/zip` | 完了ジョブのZIPダウンロード |
| `GET`  | `/api/jobs/:id/images/:filename` | 生成画像の取得 |
| `GET`  | `/api/health` | ヘルスチェック |

### POST /api/jobs

```json
{
  "script": "台本テキスト（20〜5000文字）",
  "maxCuts": 15
}
```

レスポンス:
```json
{ "jobId": "uuid-v4" }
```

### GET /api/jobs/:id

```json
{
  "id": "uuid",
  "status": "pending|processing|completed|failed",
  "totalCuts": 10,
  "completedCuts": 7,
  "failedCuts": 0,
  "cuts": [ { "cutNumber": 1, "description": "...", "textPosition": "bottom" } ],
  "results": [ { "cutNumber": 1, "status": "done", "imageUrl": "/api/jobs/.../images/cut-001.png" } ]
}
```

## ディレクトリ構成

```
storyboard-gen/
├── src/
│   ├── app/
│   │   ├── page.tsx                    # メインページ（台本入力フォーム）
│   │   ├── jobs/[jobId]/page.tsx       # 生成結果ページ（ポーリング）
│   │   ├── api/
│   │   │   ├── jobs/route.ts           # POST /api/jobs
│   │   │   └── jobs/[jobId]/
│   │   │       ├── route.ts            # GET /api/jobs/:id
│   │   │       ├── zip/route.ts        # GET /api/jobs/:id/zip
│   │   │       └── images/[filename]/  # GET /api/jobs/:id/images/:f
│   │   └── api/health/route.ts
│   ├── components/
│   │   └── ScriptForm.tsx              # 台本入力フォーム（Client Component）
│   └── lib/
│       ├── types.ts                    # 型定義
│       ├── jobStore.ts                 # ファイルI/O（/data）
│       ├── scriptParser.ts             # GPT-4o で台本分解
│       ├── imageGenerator.ts           # DALL-E 3 で画像生成（リトライ付き）
│       ├── jobProcessor.ts             # ジョブオーケストレーター
│       └── cleanup.ts                  # 古いジョブの自動削除
├── Dockerfile                          # マルチステージビルド
├── docker-compose.yml
├── .env.example
└── DEPLOY.md
```

## 設計上の注意点

- **APIキーはサーバー側のみ**。ブラウザには一切露出しません。
- **DB不要**。ジョブ情報は `/data/{jobId}/job.json` で管理します。
- **画像内テキスト禁止**。プロンプトに `No text, no letters, no logos, no watermarks` を必ず付与します。
- **リトライ**。画像生成失敗時、プロンプトを簡略化して最大2回リトライします。
- **古いジョブ自動削除**。`JOB_TTL_DAYS`（デフォルト7日）を超えたジョブは起動時に削除されます。
