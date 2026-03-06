# AI Shorts Factory — タスク管理

**プロジェクト**: AIショート動画量産パイプライン
**開始日**: 2026-03-07
**目標完了日**: 2026-04-30 (Phase 3完了)
**最終更新**: 2026-03-07

---

## Phase Overview

```
Phase 0: 準備 (2026-03-07～2026-03-10) — 4日
├─ APIキー取得・アカウント開設
├─ 環境セットアップ
└─ 基本スクリプト検証

Phase 1: パイプライン構築 (2026-03-11～2026-03-24) — 2週間
├─ Week 1: コア機能 (画像生成～投稿)
├─ Week 2: 自動化＆最適化
└─ テスト環境で動作確認

Phase 2: テスト投稿＆最適化 (2026-03-25～2026-04-07) — 2週間
├─ Week 1: 少量テスト投稿 (5-10本/日)
├─ Week 2: メトリクス分析＆調整
└─ Go/No-Go判定

Phase 3: スケール (2026-04-08～2026-04-30) — 4週間
├─ 本運用開始 (2-3本/日)
├─ 自動スケジューリング
├─ 分析ダッシュボード構築
└─ 月次KPI確認
```

---

## Phase 0: 準備 (3/7～3/10)

### タスク一覧

#### P0-1: fal.ai アカウント準備 [優先度: 🔴]
- [ ] **登録**: https://fal.ai → Sign Up (GitHub OR Email)
- [ ] **支払い方法**: Stripe クレジットカード登録
- [ ] **API Key取得**: Dashboard → API Key をコピー
- [ ] **テスト実行**: Python + `falai` ライブラリで画像1枚生成テスト
  ```bash
  pip install fal-ai
  python -c "
  import fal
  fal.api_key = 'YOUR_KEY'
  result = fal.run('fal-ai/flux.2', {'prompt': 'Test: Cat'})
  print(result['images'][0]['url'])
  "
  ```
- [ ] **確認**: 画像 URL が返却されることを確認
- **期限**: 2026-03-07 (今日)
- **見積時間**: 15分
- **担当**: Claude Code
- **ブロッカー**: なし

#### P0-2: Pika API アカウント準備 [優先度: 🔴]
- [ ] **登録**: https://pika.art → Sign Up
- [ ] **プラン選択**: "Creator" ($8/月)
- [ ] **支払い**: Stripe カード登録
- [ ] **API Key取得**: Dashboard → API section
- [ ] **テスト実行**: サンプル画像でテスト動画1本生成
  ```bash
  curl -X POST https://api.pika.art/v1/generations \
    -H "Authorization: Bearer YOUR_API_KEY" \
    -F "image=@sample.png" \
    -F "prompt=smooth motion"
  ```
- [ ] **ダウンロード確認**: MP4 が正常に再生できるか確認
- **期限**: 2026-03-07
- **見積時間**: 15分
- **担当**: Claude Code
- **ブロッカー**: なし

#### P0-3: Ayrshare アカウント＆認証準備 [優先度: 🔴]
- [ ] **登録**: https://app.ayrshare.com → Sign Up
- [ ] **プラン**: Basic ($29/月)
- [ ] **YouTube 連携**:
  - [ ] Google Account で OAuth 認可
  - [ ] YouTube チャンネル選択
  - [ ] スコープ確認: `youtube.upload`, `youtube.channel:read`
- [ ] **Instagram 連携**:
  - [ ] Meta Business Account (既存利用)
  - [ ] Instagram ビジネスアカウント確認
  - [ ] Graph API Token 発行
- [ ] **TikTok 連携**:
  - [ ] TikTok Business Account 作成 (または既存)
  - [ ] TikTok API Access 申請
  - [ ] OAuth Token 設定
- [ ] **テスト投稿**: テスト動画1本を3PF同時投稿
- [ ] **確認**: Dashboard で各PF の post status を確認
- **期限**: 2026-03-08
- **見積時間**: 30分
- **担当**: Claude Code
- **ブロッカー**: YouTubeビジネスアカウント確認必須

#### P0-4: TikTok ビジネスアカウント育成 [優先度: 🟠]
- [ ] **新規作成** (未所有の場合):
  - [ ] TikTok 新規アカウント作成 (別メール)
  - [ ] 個人認証: 身分証アップロード
  - [ ] Business Mode 有効化
  - [ ] 3ヶ月育成（最低10-20フォロワー確保）予定
- [ ] **既存アカウント利用の場合**:
  - [ ] Business Mode 確認
  - [ ] Creator Fund 申請済み確認 (10,000フォロワー等の条件確認)
- **期限**: 2026-03-09
- **見積時間**: 20分 (新規の場合後日プロセス)
- **担当**: Claude Code
- **ブロッカー**: なし

#### P0-5: Epidemic Sounds ライセンス登録 [優先度: 🟠]
- [ ] **登録**: https://www.epidemicsound.com → Sign Up
- [ ] **プラン**: Business/Content Creator ($99.99/年)
- [ ] **支払い**: Stripe カード登録
- [ ] **BGM ダウンロード**: サンプル5-10曲をダウンロード
  - [ ] テンポ: 120-130 BPM (upbeat)
  - [ ] テンポ: 80-100 BPM (calm)
  - [ ] ジャンル: Lo-Fi, EDM, Ambient
- [ ] **ライセンス確認**: ダウンロード時に "Commercial Use" 確認
- [ ] **ストレージ**: `03_PROJECTS/ai_shorts_factory/assets/bgm/` に保存
- **期限**: 2026-03-08
- **見積時間**: 25分
- **担当**: Claude Code
- **ブロッカー**: なし

#### P0-6: 既存リソース確認＆再利用 [優先度: 🔴]
- [ ] **既存パイプライン確認**:
  - [ ] `03_PROJECTS/youtube_automation/youtube_pipeline.py` 確認
  - [ ] moviepy 設定再利用可能箇所リスト化
  - [ ] Groq API 連携部分をコピー
- [ ] **EC2 環境確認**:
  - [ ] ssh で EC2 接続
  - [ ] python3 / pip パッケージ確認
  - [ ] moviepy, Pillow バージョン確認
- [ ] **Groq LLM 再利用**:
  - [ ] 既存 groq API Key 確認
  - [ ] テスト: Groq でショート動画台本生成
- [ ] **既存ストレージ**:
  - [ ] GCS / S3 接続確認
  - [ ] ディレクトリ構造作成: `ai_shorts_factory/{images,videos,bgm,output}`
- **期限**: 2026-03-07
- **見積時間**: 30分
- **担当**: Claude Code
- **ブロッカー**: 既存プロジェクト確認必須

#### P0-7: プロジェクトディレクトリ＆スケルトン構築 [優先度: 🔴]
- [ ] **ローカルディレクトリ**:
  ```
  ai_shorts_factory/
  ├── README.md
  ├── SPEC.md ✅
  ├── TODO.md ✅
  ├── KNOWLEDGE.md
  ├── PLAN.md (ユーザーから)
  ├── scripts/
  │   ├── 01_generate_script.py      (Groq)
  │   ├── 02_generate_images.py      (fal.ai)
  │   ├── 03_video_generation.py     (Pika)
  │   ├── 04_edit_and_bgm.py         (moviepy)
  │   ├── 05_upload_and_post.py      (Ayrshare)
  │   ├── 06_monitor_and_analyze.py  (Analytics)
  │   └── main_pipeline.py           (統括)
  ├── assets/
  │   ├── bgm/
  │   ├── templates/
  │   └── prompts/
  ├── config/
  │   ├── .env.example
  │   └── config.yaml
  ├── utils/
  │   ├── logger.py
  │   ├── retry.py
  │   └── validators.py
  └── output/
      ├── scripts/
      ├── images/
      ├── videos/
      └── analytics/
  ```
- [ ] **Git設定** (既存repoに追加):
  - [ ] `.gitignore` に追加: `.env`, `*.pptx`, `output/`, `assets/bgm/` (容量)
  - [ ] 初期 commit
- [ ] **README.md 作成**: Quick start 版
- **期限**: 2026-03-07
- **見積時間**: 20分
- **担当**: Claude Code
- **ブロッカー**: なし

#### P0-8: 環境変数＆設定ファイル作成 [優先度: 🔴]
- [ ] **`.env` テンプレート作成**:
  ```
  # fal.ai
  FAL_API_KEY=xxx

  # Pika
  PIKA_API_KEY=xxx

  # Ayrshare
  AYRSHARE_API_KEY=xxx

  # Groq
  GROQ_API_KEY=xxx (既存)

  # GCS/S3
  GCS_BUCKET=ai-shorts-factory
  GCS_KEYFILE=path/to/keyfile.json

  # Epidemic Sounds (License info)
  EPIDEMIC_LICENSE_YEAR=2026

  # Platforms
  YOUTUBE_CHANNEL_ID=xxx
  INSTAGRAM_ACCOUNT_ID=xxx
  TIKTOK_ACCOUNT_ID=xxx
  ```
- [ ] **config.yaml 作成**:
  ```yaml
  pipeline:
    max_parallel_jobs: 3
    retry_attempts: 3
    timeout_sec: 3600

  content:
    shorts_duration_sec: [15, 30, 45, 60]
    target_fps: 30
    target_resolution: "1080x1920"
    bgm_volume: -8  # dB
    text_font_size: 50

  platforms:
    youtube:
      enabled: true
      min_interval_sec: 7200  # 2時間
    instagram:
      enabled: true
      min_interval_sec: 14400  # 4時間
    tiktok:
      enabled: true
      min_interval_sec: 43200  # 12時間

  schedule:
    daily_target: 3  # 本/日
    publishing_hours: [10, 16, 20]  # JST
  ```
- [ ] **認証キー管理**:
  - [ ] `.env` をローカルのみ保存（.gitignore）
  - [ ] `.env.example` を作成（キー抜き）
  - [ ] Secrets Manager への登録を後日計画
- **期限**: 2026-03-07
- **見積時間**: 15分
- **担当**: Claude Code
- **ブロッカー**: なし

#### P0-9: ドキュメント作成＆デザイン確認 [優先度: 🟡]
- [ ] **コンテンツテンプレート設計**:
  - [ ] 4つのテンプレート別に Prompt/Caption 例を作成
  - [ ] テンプレート1 (AIが描く○○): プロンプト3つ作成 + キャプション案
  - [ ] テンプレート2 (Before/After): サンプルプロンプト作成
  - [ ] テンプレート3 (制作過程): 複数枚の進行図案
  - [ ] テンプレート4 (金融ワンポイント): 既存CHとのシナジー案
- [ ] **KNOWLEDGE.md 初期化**:
  - [ ] "ハマりポイント予測" セクション (Pika, moviepy既知問題等)
  - [ ] "解決策テンプレート" 雛形
- **期限**: 2026-03-08
- **見積時間**: 30分
- **担当**: Claude Code
- **ブロッカー**: なし

---

### Phase 0 チェックリスト

- [ ] P0-1 ✅ (完了予定: 3/7 18:00)
- [ ] P0-2 ✅ (完了予定: 3/7 18:30)
- [ ] P0-3 ⏳ (完了予定: 3/8 17:00)
- [ ] P0-4 ⏳ (完了予定: 3/9 19:00)
- [ ] P0-5 ✅ (完了予定: 3/8 18:00)
- [ ] P0-6 ⏳ (完了予定: 3/7 20:00)
- [ ] P0-7 ✅ (完了予定: 3/7 19:30)
- [ ] P0-8 ✅ (完了予定: 3/7 19:00)
- [ ] P0-9 ⏳ (完了予定: 3/8 21:00)

---

## Phase 1: パイプライン構築 (3/11～3/24)

### Week 1: コア機能実装 (3/11～3/17)

#### P1W1-1: `01_generate_script.py` — Groq台本生成 [優先度: 🔴]
- [ ] **関数設計**:
  ```python
  def generate_shorts_script(theme, template_name, language="ja"):
    """
    Input:
      - theme: "aiart" | "finance" | "beforeafter"
      - template_name: "flux_animation" | "before_after" | ...

    Output:
      {
        "title": "AIが描く猫",
        "prompts": ["prompt1", "prompt2"],
        "captions": ["字幕1", "字幕2"],
        "duration_sec": 45,
        "bgm_tempo": "upbeat"
      }
    """
  ```
- [ ] **実装**:
  - [ ] Groq client 初期化
  - [ ] テーマ別プロンプトテンプレート (4種)
  - [ ] 乱数種でバリエーション生成
  - [ ] JSON 出力
  - [ ] エラーハンドリング (API制限)
- [ ] **テスト**: 各テーマ×各テンプレートで計10本テスト
- **期限**: 2026-03-12
- **見積時間**: 2時間
- **担当**: Claude Code
- **ブロッカー**: P0-6

#### P1W1-2: `02_generate_images.py` — fal.ai画像生成 [優先度: 🔴]
- [ ] **関数設計**:
  ```python
  def generate_images_from_prompts(prompts_list, num_images=3):
    """
    Input: ["prompt1", "prompt2", "prompt3"]
    Output: ["image_1.png", "image_2.png", "image_3.png"]
    """
  ```
- [ ] **実装**:
  - [ ] fal.ai API クライアント初期化
  - [ ] バッチ処理 (並列 3-5 同時)
  - [ ] 画像ダウンロード＆ローカル保存
  - [ ] メタデータ記録 (生成時間, seed等)
  - [ ] キャッシング (同じプロンプトの重複生成回避)
  - [ ] リトライロジック (3回, Exponential Backoff)
- [ ] **テスト**: プロンプト5つで画像生成テスト → メモリ確認
- **期限**: 2026-03-12
- **見積時間**: 2.5時間
- **担当**: Claude Code
- **ブロッカー**: P0-1

#### P1W1-3: `03_video_generation.py` — Pika 動画化 [優先度: 🔴]
- [ ] **関数設計**:
  ```python
  def generate_video_from_image(image_path, motion_type="smooth", duration_sec=15):
    """
    Input: image_path (PNG 1024x1024)
    Output: video.mp4 (1080x1920, 30fps, H.264)
    """
  ```
- [ ] **実装**:
  - [ ] Pika API クライアント
  - [ ] 画像→MP4 変換
  - [ ] フォーマット自動選択 (Shorts/Reels/TikTok)
  - [ ] 解像度变換 1024 → 1080x1920 (アスペクト比維持)
  - [ ] エラーハンドリング (Pika API レート制限)
  - [ ] Timeout 管理 (120秒以上の場合アラート)
- [ ] **テスト**: テスト画像3枚で動画生成 → MP4 再生確認
- [ ] **フォールバック**: Runway Gen-3 (オプション, 後日実装)
- **期限**: 2026-03-13
- **見積時間**: 2.5時間
- **担当**: Claude Code
- **ブロッカー**: P0-2

#### P1W1-4: `04_edit_and_bgm.py` — moviepy 編集 [優先度: 🔴]
- [ ] **関数設計**:
  ```python
  def edit_and_add_bgm(video_paths, captions_srt, bgm_path, target_duration=30):
    """
    Input:
      - video_paths: [video1.mp4, video2.mp4, ...]
      - captions_srt: srt形式のテキスト
      - bgm_path: BGM MP3

    Output: final_video.mp4 (1080x1920, H.264, 30fps)
    """
  ```
- [ ] **実装**:
  - [ ] VideoFileClip: 各動画読み込み
  - [ ] concatenate_videoclips: 結合 (フェード処理)
  - [ ] TextClip: 字幕オーバーレイ (SRT parse)
    - フォント: Roboto Bold
    - サイズ: 50px
    - 色: white (#FFFFFF)
    - 背景: 半透明黒 (rgba(0,0,0,0.5))
  - [ ] CompositeAudioClip: BGM + ボイス合成
    - BGM: -8dB
    - ボイス (TTS): 0dB
  - [ ] Resize: 1080x1920 に正規化
  - [ ] write_videofile:
    - codec: libx264
    - fps: 30
    - bitrate: "15M"
- [ ] **既知問題対応**:
  - [ ] Pillow 10+ ANTIALIAS パッチ (既存実装から流用)
  - [ ] ffmpeg タイムアウト管理
- [ ] **テスト**: 動画3本を結合 + 字幕 + BGM で最終MP4 確認
- **期限**: 2026-03-14
- **見積時間**: 3時間
- **担当**: Claude Code
- **ブロッカー**: P1W1-3 (Pika動画生成)

#### P1W1-5: `05_upload_and_post.py` — Ayrshare投稿 [優先度: 🔴]
- [ ] **関数設計**:
  ```python
  def post_to_platforms(video_path, caption, platforms=["youtube", "instagram", "tiktok"]):
    """
    Input:
      - video_path: final_video.mp4
      - caption: "🎨AIが描く猫 #AIアート #FLUX"
      - platforms: ["youtube", "instagram", "tiktok"]

    Output:
      {
        "youtube": {"post_id": "xxx", "status": "published"},
        "instagram": {...},
        "tiktok": {...}
      }
    """
  ```
- [ ] **実装**:
  - [ ] Ayrshare API クライアント初期化
  - [ ] マルチプラットフォーム投稿 (並列)
  - [ ] キャプション最適化 (PF別のハッシュタグ数調整)
    - YouTube: 5個
    - Instagram: 30個 (スパム回避)
    - TikTok: 3-5個 (キャプション内禁止)
  - [ ] サムネイル処理:
    - YouTube: 自動生成 OR カスタム (1280x720)
    - Instagram: 自動 (Reels)
    - TikTok: 自動
  - [ ] エラーハンドリング:
    - API レート制限: キューイング
    - 認証エラー: リトライ＆アラート
    - ネットワークエラー: 指数バックオフ
  - [ ] スケジューリング (後日):
    - デフォルト: 即座投稿
    - オプション: 時間指定投稿
- [ ] **テスト**: テスト動画を3PF に投稿 → Dashboard で status 確認
- **期限**: 2026-03-14
- **見積時間**: 2.5時間
- **担当**: Claude Code
- **ブロッカー**: P0-3

#### P1W1-6: `06_monitor_and_analyze.py` — 分析＆モニタリング [優先度: 🟠]
- [ ] **関数設計**:
  ```python
  def fetch_analytics(post_ids_dict, time_range_hours=24):
    """
    Input: {"youtube": ["id1", "id2"], "instagram": [...], "tiktok": [...]}
    Output:
      {
        "summary": {...},
        "by_platform": {...},
        "metrics": {...}
      }
    """
  ```
- [ ] **実装**:
  - [ ] YouTube Data API: views, engagement, CTR
  - [ ] Instagram Graph API: views, likes, comments, saves, shares
  - [ ] TikTok API: views, engagement_rate, completion_rate
  - [ ] Google Sheets: 日次統計を自動追記
  - [ ] メトリクス定義:
    - views_rate (views/hour)
    - engagement_rate (interactions / views)
    - ctr_estimate (description clicks / views)
  - [ ] Logging: 日次ログファイル生成
- [ ] **テスト**: 投稿後 1時間で analytics fetch テスト
- **期限**: 2026-03-15
- **見積時間**: 2時間
- **担当**: Claude Code
- **ブロッカー**: P1W1-5

### Week 2: 自動化＆統括 (3/18～3/24)

#### P1W2-1: `main_pipeline.py` — 統括スクリプト [優先度: 🔴]
- [ ] **設計**:
  ```python
  def run_daily_pipeline(num_videos=3, dry_run=False):
    """
    1. テーマ＆台本生成 (Groq)
    2. 画像生成 (fal.ai) × num_prompts
    3. 動画化 (Pika) × num_images
    4. 編集＆BGM (moviepy)
    5. 投稿 (Ayrshare)
    6. 分析記録 (Google Sheets)
    """
  ```
- [ ] **実装**:
  - [ ] 6つのステップを順序実行
  - [ ] エラー時の自動リトライ (3回)
  - [ ] 部分失敗時の通知 (Slack / Email)
  - [ ] ドライラン機能 (実際の投稿なしで検証)
  - [ ] ログ出力 (各ステップのタイムスタンプ＆ステータス)
  - [ ] 出力ディレクトリ管理:
    - 日付別フォルダ: `output/YYYYMMDD/`
    - ジョブID: `video_{seq_num}_${timestamp}`
  - [ ] 並列処理考慮:
    - MAX_PARALLEL_JOBS = 3 (API rate limit 対応)
    - Queue ベースのジョブ管理
- [ ] **テスト**: 全ステップを通して3本テスト実行
- **期限**: 2026-03-18
- **見積時間**: 3時間
- **担当**: Claude Code
- **ブロッカー**: P1W1-1〜P1W1-6

#### P1W2-2: Cron/Task スケジューラー設定 [優先度: 🟡]
- [ ] **Linux Cron 設定** (EC2で運用の場合):
  ```bash
  # 毎日 10:00, 16:00, 20:00 JST に実行
  0 10,16,20 * * * /home/ubuntu/ai_shorts_factory/run_daily.sh
  ```
- [ ] **run_daily.sh 作成**:
  ```bash
  #!/bin/bash
  cd /home/ubuntu/ai_shorts_factory
  python main_pipeline.py --num_videos 3 >> logs/$(date +\%Y\%m\%d).log 2>&1
  ```
- [ ] **ローカル実行の場合**:
  - [ ] APScheduler (Python) 導入
  - [ ] スケジューラーデーモン化
- [ ] **テスト**: 手動実行 1回確認後、スケジューラー on
- **期限**: 2026-03-19
- **見積時間**: 1.5時間
- **担当**: Claude Code
- **ブロッカー**: P1W2-1

#### P1W2-3: エラーハンドリング＆通知機能 [優先度: 🟠]
- [ ] **エラー分類**:
  - Critical (投稿失敗): Slack 即通知
  - Warning (部分失敗): Email 日1回
  - Info (成功): Google Sheets 記録のみ
- [ ] **実装**:
  - [ ] logging モジュール設定 (レベル別)
  - [ ] Slack Webhook 統合
  - [ ] Email 通知 (AWS SES or SendGrid)
  - [ ] 再試行ロジック (Exponential Backoff)
  - [ ] 詳細ログ保存 (error_logs/ ディレクトリ)
- [ ] **テスト**: 意図的にエラー発生 → 通知確認
- **期限**: 2026-03-20
- **見積時間**: 2時間
- **担当**: Claude Code
- **ブロッカー**: P1W2-1

#### P1W2-4: ローカル＆EC2デプロイ [優先度: 🔴]
- [ ] **ローカル環境確認**:
  - [ ] Python 3.9+ インストール確認
  - [ ] 依存ライブラリ一覧作成: `requirements.txt`
    - fal, pika, ayrshare, groq, google-cloud-storage, moviepy 等
  - [ ] venv 環境セットアップ
  - [ ] テスト実行 1-2本確認
- [ ] **EC2 デプロイ**:
  - [ ] SSH 接続確認
  - [ ] リポジトリクローン / 最新版pull
  - [ ] 依存ライブラリ install
  - [ ] `.env` ファイル配置
  - [ ] テスト実行 1本確認
  - [ ] Cron 登録
- [ ] **ストレージ管理**:
  - [ ] GCS バケット作成 (ai-shorts-factory-prod)
  - [ ] 自動削除ポリシー: 30日後に削除
  - [ ] ローカルバックアップ: 最新7日分保持
- **期限**: 2026-03-21
- **見積時間**: 2.5時間
- **担当**: Claude Code
- **ブロッカー**: P1W2-3

#### P1W2-5: ドキュメント＆KNOWLEDGE更新 [優先度: 🟡]
- [ ] **README.md 完成**:
  - [ ] Quick Start (コマンド5個)
  - [ ] トラブルシューティング
  - [ ] API Key 設定方法
- [ ] **KNOWLEDGE.md 記入**:
  - [ ] 実装過程での ハマりポイント
  - [ ] 解決策＆ワークアラウンド
  - [ ] パフォーマンス Tips
  - [ ] よくあるエラー＆対応
- [ ] **PLAN.md 更新**: ユーザーからもらった要件との齟齬確認
- **期限**: 2026-03-22
- **見積時間**: 1.5時間
- **担当**: Claude Code
- **ブロッカー**: P1W2-4

#### P1W2-6: 負荷テスト＆最適化 [優先度: 🟠]
- [ ] **単一ジョブ性能**:
  - [ ] 台本生成: < 10秒
  - [ ] 画像生成 (3枚): 90-120秒
  - [ ] 動画化 (3枚): 45-90秒
  - [ ] 編集＆BGM: 30-60秒
  - [ ] 投稿: 10-30秒
  - **合計**: 3-5分/本
- [ ] **並列処理テスト** (3本同時):
  - [ ] API レート制限の影響測定
  - [ ] メモリ使用量: < 2GB/プロセス
  - [ ] CPU 使用率: < 80% (共有EC2前提)
- [ ] **最適化実施**:
  - [ ] キャッシング強化 (同プロンプト画像再利用)
  - [ ] 画像リサイズの早期化 (1024→1080)
  - [ ] BGM プリロード (毎回ディスク読み込み回避)
  - [ ] Batch API 利用の検討 (fal.ai)
- **期限**: 2026-03-23
- **見積時間**: 2時間
- **担当**: Claude Code
- **ブロッカー**: P1W2-4

### Phase 1 チェックリスト

**Week 1**
- [ ] P1W1-1 ✅ (完了予定: 3/12 20:00)
- [ ] P1W1-2 ✅ (完了予定: 3/12 22:00)
- [ ] P1W1-3 ✅ (完了予定: 3/13 22:00)
- [ ] P1W1-4 ✅ (完了予定: 3/14 23:00)
- [ ] P1W1-5 ✅ (完了予定: 3/14 22:00)
- [ ] P1W1-6 ⏳ (完了予定: 3/15 20:00)

**Week 2**
- [ ] P1W2-1 ✅ (完了予定: 3/18 22:00)
- [ ] P1W2-2 ⏳ (完了予定: 3/19 20:00)
- [ ] P1W2-3 ⏳ (完了予定: 3/20 21:00)
- [ ] P1W2-4 ✅ (完了予定: 3/21 20:00)
- [ ] P1W2-5 ⏳ (完了予定: 3/22 19:00)
- [ ] P1W2-6 ⏳ (完了予定: 3/23 20:00)

---

## Phase 2: テスト投稿＆最適化 (3/25～4/7)

### Week 1: 少量テスト＆メトリクス (3/25～3/31)

#### P2W1-1: ライブテスト投稿 (5-10本/日) [優先度: 🔴]
- [ ] **テーマローテーション**:
  - Day 1-2: "AIが描く〇〇" シリーズ (×4)
  - Day 3-4: Before/After系 (×3)
  - Day 5-6: 制作過程 (×2)
  - Day 7: 金融ワンポイント (×2)
- [ ] **投稿パターン**:
  - 時間帯テスト: 10:00 / 16:00 / 20:00
  - プラットフォーム別反応測定
  - キャプション長テスト (短/中/長)
- [ ] **データ記録**:
  - Post ID, 投稿時刻, テーマ, キャプション, 画像プロンプト
  - Google Sheets に毎投稿後記入
- **期限**: 2026-03-31
- **見積時間**: 毎日 1時間（監視＆記録）
- **担当**: Claude Code
- **ブロッカー**: P1 完了

#### P2W1-2: メトリクス定義＆分析基盤構築 [優先度: 🔴]
- [ ] **KPI 定義**:
  ```
  [7日間移動平均]
  - AVG_VIEWS (動画あたりの平均再生数)
  - AVG_ENGAGEMENT (いいね＋コメント＋シェア)
  - CTR_ESTIMATE (description クリック率推定)
  - FOLLOWER_GAIN (フォロワー増加数)

  [PF別]
  - YouTube: views, engagement
  - Instagram: views, saves (保存数重視)
  - TikTok: completion_rate (完全視聴率)
  ```
- [ ] **分析ダッシュボード** (Google Sheets):
  - [ ] 日次: post ID, views, engagement, timestamp
  - [ ] 週次: AVG_VIEWS, AVG_ENG, テーマ別breakdown
  - [ ] テーマ別 top 5
  - [ ] PF別 推移グラフ
- [ ] **A/Bテスト設計**:
  - [ ] 長さ: 15秒 vs 30秒 vs 45秒 (各3本)
  - [ ] BGMテンポ: upbeat vs calm (各3本)
  - [ ] キャプション長: 短(< 50文字) vs 長(> 150文字) (各3本)
  - [ ] 結果分析: 有意差検定 (t-test)
- **期限**: 2026-03-29
- **見積時間**: 3時間
- **担当**: Claude Code
- **ブロッカー**: P2W1-1 開始前

#### P2W1-3: コンテンツ品質レビュー＆調整 [優先度: 🟠]
- [ ] **視覚品質チェック** (毎投稿後):
  - [ ] 字幕の読みやすさ (フォント/背景)
  - [ ] BGM と本編の音量バランス
  - [ ] 色合い (暗くないか / 明るすぎないか)
  - [ ] フレーム落ち / 乱れなし確認
- [ ] **コンテンツ改善案**:
  - [ ] 字幕サイズ: 50px → 60px 試行
  - [ ] 字幕表示時間: 拡大 (短かったテンプレ)
  - [ ] BGM フェード処理の追加
  - [ ] エフェクト最小化 (プラットフォーム側と競合回避)
- [ ] **テンプレート別改善**:
  - [ ] "制作過程": 音声なし版 vs 解説あり版 テスト
  - [ ] "金融ワンポイント": グラフの見やすさ向上
- [ ] **KNOWLEDGE.md に記録**
- **期限**: 2026-03-31 (随時更新)
- **見積時間**: 毎日 30分
- **担当**: Claude Code
- **ブロッカー**: なし (並行)

### Week 2: 最適化＆Go/No-Go判定 (4/1～4/7)

#### P2W2-1: パフォーマンス分析＆ボトルネック特定 [優先度: 🔴]
- [ ] **7日間データ分析**:
  - [ ] 全投稿 (35-70本) の集計
  - [ ] テーマ別 平均 views/engagement
  - [ ] PF別 パフォーマンス
  - [ ] 時間帯別 反応パターン
- [ ] **ボトルネック特定**:
  - [ ] 低パフォーマンステーマを特定
  - [ ] 改善施策立案:
    - テーマ変更?
    - キャプション改善?
    - 時間帯調整?
    - BGM 変更?
  - [ ] 次週試行リスト作成
- [ ] **データダッシュボード更新**:
  - [ ] 仮説検定結果記入
  - [ ] グラフ化 (views推移, engagement率等)
- **期限**: 2026-04-03
- **見積時間**: 2.5時間
- **担当**: Claude Code
- **ブロッカー**: P2W1-1 (7日分投稿)

#### P2W2-2: スケーリング前最終チェック [優先度: 🔴]
- [ ] **技術確認**:
  - [ ] API コスト実績: 予算内か
  - [ ] エラー発生率: < 5% か
  - [ ] パイプライン完了時間: < 5分/本 か
  - [ ] ストレージ使用量: 月30GB 以下か
- [ ] **運用体制確認**:
  - [ ] スケジューラー: 毎日正確に実行されるか
  - [ ] ログ: 問題追跡可能か
  - [ ] 通知: アラート機能正常か
- [ ] **規約準拠確認**:
  - [ ] 著作権チェック: 違反ないか
  - [ ] AI生成明記: すべてのキャプションに #AIアート 入っているか
  - [ ] 金融免責事項: 金融テーマに免責表記あるか
  - [ ] CGU違反: 各PF の最新ポリシー確認
- [ ] **セキュリティ確認**:
  - [ ] API Key が `.env` に隔離されているか
  - [ ] Git に credentials push されていないか
  - [ ] ログファイルに機密情報が露出していないか
- **期限**: 2026-04-04
- **見積時間**: 1.5時間
- **担当**: Claude Code
- **ブロッカー**: P2W2-1

#### P2W2-3: Go/No-Go 判定＆報告書作成 [優先度: 🔴]
- [ ] **判定基準**:
  ```
  GO 条件:
  - AVG_VIEWS >= 500 (7日平均)
  - AVG_ENG_RATE >= 2%
  - エラー率 < 5%
  - 規約違反 0件
  - API コスト実績 <= 予算内

  CONDITIONAL GO:
  - 上記いずれか未達だが、改善案あり

  NO-GO:
  - 複数項目未達で改善困難
  ```
- [ ] **報告書作成** (`03_PROJECTS/ai_shorts_factory/P2_report.md`):
  - 7日間の集計データ
  - テーマ別分析
  - PF別反応比較
  - 改善施策案
  - Phase 3 スケール計画
  - ユーザーへの報告
- [ ] **次フェーズ計画決定**:
  - GO: 4/8 より 3本/日 開始
  - CONDITIONAL: 調整期間追加 (1-2週)
  - NO-GO: 抜本改善 or プロジェクト見直し
- **期限**: 2026-04-07
- **見積時間**: 2時間
- **担当**: Claude Code
- **ブロッカー**: P2W2-2

### Phase 2 チェックリスト

**Week 1**
- [ ] P2W1-1 ⏳ (完了予定: 3/31 24:00)
- [ ] P2W1-2 ✅ (完了予定: 3/29 20:00)
- [ ] P2W1-3 ⏳ (完了予定: 3/31 24:00, 随時更新)

**Week 2**
- [ ] P2W2-1 ⏳ (完了予定: 4/3 20:00)
- [ ] P2W2-2 ⏳ (完了予定: 4/4 19:00)
- [ ] P2W2-3 ⏳ (完了予定: 4/7 21:00)

---

## Phase 3: スケール＆安定化 (4/8～4/30)

### Week 1-2: 本運用開始 (4/8～4/21)

#### P3-1: 投稿本数スケール (2本/日 → 3本/日) [優先度: 🔴]
- [ ] **実施内容**:
  - [ ] `main_pipeline.py` に `--num_videos 3` フラグを設定
  - [ ] Cron ジョブを 3本/日 に変更:
    ```bash
    0 10 * * * /home/ubuntu/ai_shorts_factory/run_daily.sh --num 1
    0 16 * * * /home/ubuntu/ai_shorts_factory/run_daily.sh --num 1
    0 20 * * * /home/ubuntu/ai_shorts_factory/run_daily.sh --num 1
    ```
  - [ ] API コスト監視
  - [ ] エラー率監視 (アラート設定: > 10% で通知)
- [ ] **並列処理安定性確認**:
  - [ ] 3ジョブ同時実行時の API 競合なし
  - [ ] メモリリーク確認
  - [ ] ディスク容量確認 (daily 2GB消費と想定)
- **期限**: 2026-04-08
- **見積時間**: 2時間 (セットアップ) + 毎日 30分 (監視)
- **担当**: Claude Code
- **ブロッカー**: P2-3 (Go判定)

#### P3-2: テーマ＆プロンプトライブラリ拡充 [優先度: 🟠]
- [ ] **テーマ追加** (Phase 1 の 4つ から拡張):
  - [ ] "トレンド図解": X/TikTok トレンドを図解化
  - [ ] "AI似顔絵": 指定キャラクター風イラスト
  - [ ] "風景アート": AI が描く幻想的風景
  - [ ] "タイムラプス": 制作過程の高速再生
- [ ] **Groq プロンプトテンプレート拡張**:
  - [ ] テーマごとに 5-10 バリエーション
  - [ ] プロンプト品質チェック (FLUX生成テスト)
  - [ ] CSV で管理 (`assets/prompts/prompts_library.csv`)
- [ ] **キャプション自動生成テンプレート**:
  - [ ] テーマ別 固定句 + 動的部分 の組み合わせ
  - [ ] ハッシュタグ自動選択ロジック
- **期限**: 2026-04-12
- **見積時間**: 3時間
- **担当**: Claude Code
- **ブロッカー**: なし (並行)

#### P3-3: ダッシュボード＆分析自動化 [優先度: 🟠]
- [ ] **Google Sheets 自動化**:
  - [ ] Google Sheets API 連携
  - [ ] 日次自動記入 (投稿直後)
  - [ ] グラフ自動更新 (日次/週次/月次)
- [ ] **ダッシュボード構成**:
  - Sheet 1: Daily Log (投稿データ)
  - Sheet 2: Weekly Summary (テーマ別, PF別)
  - Sheet 3: KPI トレンド (グラフ)
  - Sheet 4: Budget Tracking (API コスト)
  - Sheet 5: Content Calendar (次週計画)
- [ ] **通知自動化**:
  - [ ] 週1回レポート (日曜21:00 メール)
  - [ ] 異常値アラート (views < 平均30%で Slack)
  - [ ] API コストアラート (月額 ¥6,000 超過時)
- **期限**: 2026-04-14
- **見積時間**: 3時間
- **担当**: Claude Code
- **ブロッカー**: なし (並行)

### Week 3-4: 最適化＆月次レビュー (4/22～4/30)

#### P3-4: テーマ別パフォーマンス最適化 [優先度: 🟠]
- [ ] **2週間データ (42-60本) 分析**:
  - [ ] テーマ別 AVG_VIEWS ランキング
  - [ ] PF別 相性分析 (TikTok は短編向き等)
  - [ ] 時間帯別 反応パターン (更新)
- [ ] **低パフォーマンステーマの改善**:
  - [ ] キャプション 10パターン試行
  - [ ] BGM 変更試行
  - [ ] 尺 (15秒 vs 30秒) 最適化
- [ ] **高パフォーマンステーマの拡大**:
  - [ ] 予算配分増加 (毎日投稿比率)
  - [ ] バリエーション拡充
- **期限**: 2026-04-25
- **見積時間**: 2.5時間
- **担当**: Claude Code
- **ブロッカー**: P3-1 (最低2週間データ)

#### P3-5: 月次ビジネス分析＆ROI確認 [優先度: 🔴]
- [ ] **投稿統計**:
  - [ ] 本数: 90本 達成確認
  - [ ] テーマ別breakdown
  - [ ] ダウンタイム: エラー率 < 5% か
- [ ] **パフォーマンス指標**:
  - [ ] 総 views
  - [ ] 総 engagement
  - [ ] 新規フォロワー数 (3PF合計)
  - [ ] クリック数 (description links)
- [ ] **財務分析**:
  - [ ] 実績 API コスト
  - [ ] 推定広告収益 (CPM ベース)
  - [ ] ROI = (推定収益 - コスト) / コスト × 100%
  - [ ] 本あたりコスト＆収益
- [ ] **報告書作成** (`03_PROJECTS/ai_shorts_factory/P3_monthly_report.md`):
  - 月間サマリー
  - KPI ダッシュボード (スクリーンショット)
  - 次月計画＆改善施策
  - ユーザーへの報告
- **期限**: 2026-04-30
- **見積時間**: 2.5時間
- **担当**: Claude Code
- **ブロッカー**: 月末まで

#### P3-6: 自動化機能の追加 (オプション) [優先度: 🟡]
- [ ] **テーマ自動選択アルゴリズム**:
  - [ ] 前週パフォーマンス学習
  - [ ] 今週推奨テーマを提示
  - [ ] ユーザー手動オーバーライド可能
- [ ] **キャプション自動最適化**:
  - [ ] 過去高パフォーマンス キャプション から類似度計算
  - [ ] 推奨キャプション候補を提示
- [ ] **投稿スケジューリング最適化**:
  - [ ] プラットフォーム別 最適時間帯を自動選択
- **期限**: 2026-04-28
- **見積時間**: 3時間
- **担当**: Claude Code
- **ブロッカー**: P3-4 (データ十分集積後)

### Phase 3 チェックリスト

**Week 1-2 (本運用)**
- [ ] P3-1 ⏳ (完了予定: 4/8, 継続運用)
- [ ] P3-2 ⏳ (完了予定: 4/12 20:00)
- [ ] P3-3 ⏳ (完了予定: 4/14 20:00)

**Week 3-4 (最適化)**
- [ ] P3-4 ⏳ (完了予定: 4/25 20:00)
- [ ] P3-5 ⏳ (完了予定: 4/30 23:59)
- [ ] P3-6 ⏳ (完了予定: 4/28 20:00, Optional)

---

## KPI モニタリング項目

### リアルタイム監視 (毎日)

| 項目 | ターゲット | 警告閾値 | 担当 |
|------|-----------|--------|------|
| Daily Pipeline Success Rate | > 95% | < 90% | Claude Code |
| API Error Rate | < 5% | > 10% | Claude Code |
| Avg Processing Time / Video | < 5 min | > 8 min | Claude Code |
| Disk Storage Used | < 50GB | > 60GB | Claude Code |

### 週次分析 (毎週日曜)

| 項目 | ターゲット | 期間 | 分析方法 |
|------|-----------|------|--------|
| Avg Views / Video | > 500 | 7日移動平均 | Google Sheets |
| Avg Engagement Rate | > 2% | 7日移動平均 | API集計 |
| Follower Growth | > 50 | 週単位 | Ayrshare Dashboard |
| CTR Estimate | > 1% | 推定値 | Google Sheets |

### 月次報告 (毎月末)

| 項目 | 期間 | 出力 |
|------|------|------|
| Total Videos Posted | 月間 | 90本 目標 |
| Platform Performance Ranking | 月間 | YT > IG > TT 想定 |
| Revenue Estimate | 月間 | CPM × views × 0.1 |
| API Cost | 月間 | Dashboard |
| ROI | 月間 | (Revenue - Cost) / Cost |
| Content Theme Ranking | 月間 | Top 3 テーマ特定 |

---

## 付録: コマンドリファレンス

### ローカル実行

```bash
# 単一ビデオ生成 (ドライラン)
python main_pipeline.py --dry_run --num_videos 1

# 3本本番投稿
python main_pipeline.py --num_videos 3

# テーマ指定
python main_pipeline.py --theme "aiart" --num_videos 1

# ログ確認
tail -f logs/$(date +%Y%m%d).log
```

### EC2 デプロイ

```bash
# SSH接続
ssh -i ~/key.pem ubuntu@{EC2_IP}

# スクリプト実行確認
cd ~/ai_shorts_factory
./run_daily.sh --num 1

# Cron 状態確認
crontab -l

# ログ確認
tail -100 logs/latest.log
```

### 分析＆レポート

```bash
# Google Sheets 更新
python utils/sync_analytics.py

# ダッシュボード確認
open "https://docs.google.com/spreadsheets/d/..."

# 月次報告書生成
python utils/generate_report.py --month "2026-04"
```

---

**最終更新**: 2026-03-07
**次回見直し**: 2026-04-07 (Phase 2終了時)
