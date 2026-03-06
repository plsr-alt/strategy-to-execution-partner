# AI Shorts Factory — 仕様書

**版番号**: v1.0
**作成日**: 2026-03-07
**最終更新**: 2026-03-07
**ステータス**: 仕様確定

---

## 1. プロジェクト概要

### 目的
既存YouTubeパイプライン（長尺動画）の資産を活用し、YouTube Shorts / Instagram Reels / TikTok 向けショート動画（15-60秒）を自動量産する。3プラットフォーム同時投稿により、リーチ最大化と収入源の多角化を実現。

### 投資効果
| 指標 | 1ヶ月目 | 3ヶ月目 | 6ヶ月目 | 12ヶ月目 |
|------|--------|--------|--------|----------|
| 本数 | 60本 | 90本 | 90本 | 90本 |
| 本数/日 | 2本 | 3本 | 3本 | 3本 |
| 想定月収 | 0-1万 | 1-3万 | 5-15万 | 10-30万 |
| API月額 | ¥2,500 | ¥2,500 | ¥2,500 | ¥2,500 |

---

## 2. パイプラインアーキテクチャ

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI Shorts Factory Pipeline                    │
└─────────────────────────────────────────────────────────────────┘

[Phase 0: 企画・台本生成]
  ├─ Groq LLM (既存): コンテンツ企画＆台本生成
  │  └─ Input: 日次テーマ（金融・AIアート・トレンド等）
  │  └─ Output: 30-60秒台本 (JSON形式)
  │
[Phase 1: 画像生成]
  ├─ fal.ai FLUX.2: プロンプト→画像生成 ($0.03/枚)
  │  └─ Input: Groqが生成したプロンプト
  │  └─ Output: 1024x1024 PNG (3-5枚)
  │  └─時間: 約30秒/枚
  │
[Phase 2: 画像→動画変換]
  ├─ Pika API ($8/月) OR Runway Gen-3 ($28/月): 静止画→動画化
  │  └─ Input: 画像3-5枚 + テキスト指示
  │  └─ Output: MP4 (15-60秒)
  │  └─ 解像度: 1080x1920 (Shorts/Reels), 1080x1080 (TikTok)
  │  └─ 形式: MP4 H.264
  │
[Phase 3: 編集＆BGM追加]
  ├─ moviepy (既存資産): クリップ結合＆エフェクト
  │  ├─ 字幕: Groq台本から自動抽出 (SRT形式)
  │  ├─ BGM: Epidemicサウンドライセンス ($99.99/年) or Pixabay
  │  ├─ 尺調整: 15-60秒に正規化
  │  └─ Output: Shorts/Reels/TikTok フォーマット別MP4
  │
[Phase 4: 投稿]
  ├─ Ayrshare API ($29/月): 3プラットフォーム同時投稿
  │  ├─ YouTube Shorts (youtube_upload APIと並行)
  │  ├─ Instagram Reels (business account)
  │  └─ TikTok (TikTok API)
  │
[Phase 5: モニタリング]
  ├─ Google Sheets: 日次統計
  ├─ メトリクス: 再生数・エンゲージメント・フォロワー
  └─ A/Bテスト: テーマ・長さ・BGM効果測定
```

---

## 3. コンテンツフォーマット仕様

### 3.1 ショート動画フォーマット比較

| 項目 | YouTube Shorts | Instagram Reels | TikTok |
|------|---|---|---|
| **推奨尺** | 15-60秒 | 15-90秒 | 15-60秒 |
| **解像度** | 1080x1920 (9:16) | 1080x1920 (9:16) | 1080x1920 (9:16) |
| **フレームレート** | 30fps推奨 | 30fps推奨 | 24-60fps |
| **ビットレート** | 10-20 Mbps | 8-15 Mbps | 6-12 Mbps |
| **コーデック** | H.264 | H.264 | H.264 |
| **最大ファイルサイズ** | 未制限 | 4GB | 287.6MB |
| **字幕形式** | VTT/SRT (自動) | SRT | VTT |
| **BGM** | ライブラリ有 | ライブラリ有 | ライブラリ有 |

### 3.2 各プラットフォーム向け編集仕様

#### YouTube Shorts
```
解像度: 1080x1920 (9:16)
フレームレート: 30fps
ビットレート: 15 Mbps
字幕: 自動生成（SRT）
効果: エフェクト最小限（プラットフォームネイティブ機能使用推奨）
BGM: YouTube Audio Library（無料）or Epidemic Sounds
尺: 15-60秒
```

#### Instagram Reels
```
解像度: 1080x1920 (9:16)
フレームレート: 30fps
ビットレート: 10 Mbps
字幕: 埋め込み（hardcode）推奨
効果: Reels フォーマット最適化
BGM: 著作権フリー or Epidemic Sounds
尺: 15-90秒（推奨30-60秒）
```

#### TikTok
```
解像度: 1080x1920 (9:16) または 1080x1080 (1:1)
フレームレート: 30fps
ビットレート: 8 Mbps
字幕: 埋め込み（hardcode）推奨
効果: TikTok トレンド効果対応
BGM: TikTok音声ライブラリ（クリエイター向け）
尺: 15-60秒（推奨15-30秒）
```

### 3.3 コンテンツテンプレート

#### テンプレート 1: 「AIが描く○○」シリーズ
```
[構成: 8-12秒]
- Intro (字幕): "AIが描く〇〇" (2秒)
- シーン1: 画像1→動画化 (3秒)
- シーン2: 画像2→動画化 (3秒)
- シーン3: 画像3→動画化 (3秒)
- Outro (字幕+BGM fade-out): "#AIアート #FLUX" (1秒)

[使用ツール]
- Groq: プロンプト生成
- fal.ai FLUX.2: 画像3枚
- Pika/Runway: 各画像→動画化
- moviepy: 結合＋字幕＋BGM
```

#### テンプレート 2: ビフォーアフター系
```
[構成: 10-15秒]
- Before画像 (2秒)
- 変換過程（遷移） (5秒)
- After画像 (2秒)
- 字幕: "AIで〇〇風に変身！" (1秒)
- CTA: "フォロー→コメント" (2秒)

[使用ツール]
- fal.ai FLUX.2: Before/After 2パターン
- Runway Gen-3: 遷移アニメーション
- moviepy: 合成＋字幕
```

#### テンプレート 3: AIアート制作過程
```
[構成: 20-30秒]
- タイトル (2秒): "このプロンプトから生まれたのは..."
- プロンプト表示 (3秒): テキストで表示
- 画像生成過程 (時短版) (5秒): 複数の中間ステップ
- 完成画像 (3秒)
- ロール（複数作品の連続再生） (10秒)
- Outro＆CTA (3秒)

[使用ツール]
- Groq: プロンプト連続生成
- fal.ai FLUX.2: 複数枚並行生成
- Pika: 簡単な動画化
- moviepy: 高速カット＆BPM同期
```

#### テンプレート 4: 金融ワンポイント（既存CHとの連携）
```
[構成: 15-20秒]
- データ可視化 (3秒)
- 解説字幕 (8秒): Groq生成のワンポイント解説
- トレンドグラフ (3秒)
- 相場速報イラスト (2秒)
- CTA (2秒): "チャンネル登録で毎日更新"

[使用ツール]
- Groq: 今日の相場解説文 + プロンプト
- fal.ai: 相場関連イラスト (5秒作成)
- moviepy: グラフ＋テキスト合成
- BGM: 軽いBGM（テンション高め）
```

---

## 4. ツール・API 仕様書

### 4.1 外部API構成

| サービス | 用途 | 月額 | 特徴 | 代替 |
|---------|------|------|------|------|
| **fal.ai (FLUX.2)** | 画像生成 | ¥600 ($0.03/枚) | 高速・高品質 | Midjourney ($30) |
| **Pika** | 画像→動画化 | ¥800 ($8/月) | 最速・軽量 | Runway ($28) |
| **Ayrshare** | 3PF投稿管理 | ¥2,900 ($29/月) | スケジューリング＆分析 | Buffer ($29) |
| **Groq LLM** | 台本生成 | 無料 | 既存契約 | OpenAI |
| **Epidemic Sounds** | BGM | ¥8,000 ($99.99/年) | 商用利用OK | Pixabay (無料) |
| **YouTube Data API** | 投稿＆分析 | 無料 | 既存利用中 | — |
| **TikTok API** | TikTok投稿 | 無料 | ビジネスアカウント必須 | — |
| **Instagram Graph API** | Reels投稿 | 無料 | ビジネスアカウント必須 | — |

### 4.2 パイプライン処理フロー（詳細）

#### Step 1: テーマ＆台本生成（Groq）
```python
Input:
  - date: 2026-03-07
  - theme: "AIアート" or "金融ワンポイント"
  - template: "flux_animation" or "before_after"

Processing:
  - Groq LLM: プロンプト×3-5個生成
  - JSON形式: {
      "title": "AIが描く〇〇",
      "prompts": ["prompt1", "prompt2", ...],
      "captions": ["字幕1", "字幕2", ...],
      "duration_sec": 45,
      "bgm_tempo": "upbeat"
    }

Output:
  - shorts_script_YYYYMMDD_HHmmss.json
```

#### Step 2: 画像生成（fal.ai FLUX.2）
```python
Input:
  - prompts: ["prompt1", "prompt2", "prompt3"]
  - model: "fal-ai/flux.2" or "fal-ai/flux.1-pro"
  - dimensions: "1024x1024"

API Call:
  POST https://api.fal.ai/runs
  Body: {
    "model": "fal-ai/flux.2",
    "input": {
      "prompt": "...",
      "image_size": "1024x1024",
      "num_inference_steps": 30
    }
  }
  Cost: $0.03/枚 (約30秒生成)

Output:
  - image_{n}.png (1024x1024 PNG)
  - metadata.json (生成情報)
```

#### Step 3: 動画化（Pika API）
```python
Input:
  - images: [image_1.png, image_2.png, image_3.png]
  - motion_direction: "pan_left" or "zoom" or "flow"
  - duration: 15-60 秒

API Call:
  POST https://api.pika.art/v1/generations
  Body: {
    "model": "pika-1.0",
    "input": {
      "prompt": "smooth motion, cinematic",
      "image": "base64_encoded_image",
      "motion": "subtle"
    }
  }
  Cost: ¥800/月 (無制限)

Output:
  - video_{n}.mp4 (1080x1920, 30fps, 15-60秒)
```

#### Step 4: 編集＆BGM追加（moviepy）
```python
Input:
  - videos: [video_1.mp4, video_2.mp4, ...]
  - captions: SRT形式
  - bgm_path: bgm_upbeat.mp3
  - format: "shorts" or "reels" or "tiktok"

Processing:
  - VideoFileClip: 各動画読み込み
  - concatenate_videoclips: 並列結合
  - TextClip: 字幕 (Roboto, 50px, white)
  - CompositeAudioClip: 音声トラック合成
  - write_videofile: 最終エンコード

Output:
  - final_shorts_YYYYMMDD_001.mp4 (1080x1920)
  - final_reels_YYYYMMDD_001.mp4 (1080x1920)
  - final_tiktok_YYYYMMDD_001.mp4 (1080x1920)
```

#### Step 5: 投稿（Ayrshare API）
```python
Input:
  - video_path: final_shorts_YYYYMMDD_001.mp4
  - platforms: ["youtube", "instagram", "tiktok"]
  - caption: "🎨AIが描く○○..."
  - hashtags: ["#AIアート", "#FLUX", "#ショート動画"]
  - schedule_time: "2026-03-07T20:00:00Z" (オプション)

API Call:
  POST https://app.ayrshare.com/api/post
  Body: {
    "post": "🎨AIが描く○○...",
    "platforms": ["youtube", "instagram", "tiktok"],
    "media": ["video_base64"],
    "mediaType": "video",
    "schedule": "2026-03-07T20:00:00Z"
  }

Output:
  - Ayrshare Dashboard: 投稿状態確認
  - post_ids: ["youtube_xxxx", "ig_xxxx", "tiktok_xxxx"]
```

#### Step 6: 分析＆モニタリング
```python
Input:
  - post_ids: ["youtube_xxxx", "ig_xxxx", "tiktok_xxxx"]
  - date_range: 過去24-72時間

Metrics:
  [YouTube Shorts]
  - views
  - engagement_rate (コメント＋いいね)
  - click_through_rate (description link)

  [Instagram Reels]
  - views
  - likes
  - comments
  - saves
  - shares

  [TikTok]
  - views
  - engagement_rate
  - completion_rate
  - follower_increase

Output:
  - daily_stats_YYYYMMDD.json
  - analytics_dashboard (Google Sheets)
```

---

## 5. 技術要件＆規約対応

### 5.1 3プラットフォーム同時投稿の技術要件

#### YouTube Shorts
- **必須**: YouTube Creator Studio（自動アップロード経由）
- **推奨**: youtube_upload API （OAuth2）
- **チャンネル条件**: 1,000フォロワー以上推奨（初期段階は不要）
- **API日次クォータ**: 10,000ユニット/日（1動画 = 1-2ユニット）
- **ブロック対策**:
  - 同一コンテンツの重複投稿禁止（YouTubeは他PFと異なるサムネイル推奨）
  - アップロード間隔: 2時間以上
  - 月額上限: 推奨100本（API/ポリシー範囲内）

#### Instagram Reels
- **必須**: ビジネスアカウント（Instagram Graph API v17.0以上）
- **認証**: Facebook App ID + Access Token （有効期限: 無期限）
- **投稿方法**: Media Container → Reels Creation API
- **制限**:
  - 1日3本まで（Business Account）
  - スケジューリング: 最大10日先
  - ハッシュタグ: 最大30個
- **ブロック対策**:
  - 投稿間隔: 4時間以上（アルゴリズム学習）
  - キャプション重複禁止（テンプレート変更推奨）
  - 著作権チェック: Epidemic Sounds ライセンス確認

#### TikTok
- **必須**: TikTok Business Account + TikTok API Access
- **認証**: OAuth 2.0 with Scopes: `video.create`, `video.publish`
- **投稿方法**: Video Upload API → TikTok CDN
- **制限**:
  - 1日1本まで（開発者版）
  - スケジューリング: 不可（即時投稿のみ）
  - ファイルサイズ: 最大287.6MB
  - アカウント認証: 個人ID確認必須
- **ブロック対策**:
  - VPN/プロキシ使用禁止（アカウント停止リスク）
  - 投稿間隔: 実際には12時間以上推奨（アルゴリズム）
  - コンテンツ重複: TikTok内重複投稿NG（リーチ低下）

### 5.2 著作権＆規約リスク対策

| リスク | 対策 | 優先度 |
|--------|------|--------|
| **BGM著作権** | Epidemic Sounds ($99.99/年) ライセンス確認 + クレジット表記 | 🔴 必須 |
| **FLUX画像著作権** | 生成画像は個人商用OK（利用規約確認） | 🟠 重要 |
| **顔認識（AI生成）** | 実在人物の顔生成NG（各PF規約違反） | 🔴 必須 |
| **金融情報（免責事項）** | "投資助言ではありません" を必ずCTA表記 | 🟠 重要 |
| **プライバシー（背景人物）** | AI生成画像なので無関係（但しテンプレート確認） | 🟡 推奨 |
| **リンク誘導スパム** | 1ヶ月に3本以下に抑制 | 🟡 推奨 |
| **AI生成明記** | キャプション最後に #AIアート #生成AI | 🟡 推奨 |

### 5.3 プラットフォーム別規約チェックリスト

#### YouTube Shorts 規約
- [ ] アップロード前: 著作権チェック（Content ID）
- [ ] BGM: YouTube Audio Library OR Epidemic Sounds
- [ ] 字幕: 自動生成を確認（英語設定で自動翻訳）
- [ ] タグ: "#Shorts" 必須
- [ ] サムネイル: 自動生成 OR カスタム (最小1280x720)
- [ ] 説明欄: キャプション＋外部リンク（1個まで）
- [ ] コンテンツID登録: Epidemic Sounds CDN提供

#### Instagram Reels 規約
- [ ] ビジネスアカウント確認
- [ ] 著作権: Instagram Licensed Music Library OR Epidemic
- [ ] キャプション: 最大2200文字（Shorts規約はなし）
- [ ] ハッシュタグ: 最大30個（スパム防止）
- [ ] リンク: Linktree等に統一（direct link NG）
- [ ] スケジュール: 最大10日先
- [ ] 年齢制限: なし（13才以上）

#### TikTok 規約
- [ ] 個人認証: 身分証による本人確認
- [ ] BGM: TikTok Sounds Library OR Epidemic（注意）
- [ ] コンテンツポリシー: AI明記推奨（#AIアート）
- [ ] リンク: プロフィールのみ（キャプション内NG）
- [ ] 動画長: 15-60秒推奨（15-10分対応だが短尺最適）
- [ ] 投稿頻度: 1日1本（API制限）
- [ ] アカウント年齢: 最低3ヶ月（新規アカウント要注意）

---

## 6. コスト試算（月間）

### 6.1 月間コスト概算（90本/月 = 3本/日）

| 項目 | 単価 | 月間使用量 | 月額 | 備考 |
|------|------|-----------|------|------|
| **fal.ai FLUX.2** | $0.03/枚 | 300枚 (90本×3-4枚) | ¥900 | 最低保証なし |
| **Pika** | ¥800 | 無制限 | ¥800 | 副業向けプラン |
| **Ayrshare** | ¥2,900 | 無制限 | ¥2,900 | 3PF同時投稿管理 |
| **Epidemic Sounds** | ¥667/月 | 無制限BGM | ¥667 | 年額¥8,000÷12 |
| **Groq API** | 無料 | 無制限 | ¥0 | 既存契約 |
| **YouTube Data API** | 無料 | 10,000ユニット/日 | ¥0 | 既存利用中 |
| **Instagram/TikTok API** | 無料 | 無制限 | ¥0 | 認証済み |
| **EC2サーバー** (既存) | ¥3,000 | 共用 | ¥0 | youtube_pipeline と共用 |
| **ストレージ** (GCS/S3) | ¥100 | 動画キャッシュ | ¥100 | 30日自動削除 |
| **監視ツール** (Datadog等) | 無料 | 基本プラン | ¥0 | 必要に応じて拡張 |

**合計**: 約¥5,367/月 （90本/月時点）

### 6.2 スケール別コスト

| スケール | 本数/月 | 月額 | 本あたりコスト |
|---------|--------|------|---------------|
| **Phase 1** (2本/日) | 60本 | ¥4,200 | ¥70 |
| **Phase 2** (3本/日) | 90本 | ¥5,367 | ¥60 |
| **Phase 3** (5本/日) | 150本 | ¥7,200 | ¥48 |
| **Phase 4** (10本/日) | 300本 | ¥11,000 | ¥37 |

### 6.3 収入試算

| 期間 | 月本数 | YT Shorts推定 | IG推定 | TikTok推定 | 合計月収 | コスト | 利益 |
|------|--------|---|---|---|-----------|--------|------|
| 1ヶ月目 | 60 | ¥500 | ¥300 | ¥200 | ¥1,000 | ¥4,200 | -¥3,200 |
| 3ヶ月目 | 90 | ¥5,000 | ¥2,000 | ¥1,000 | ¥8,000 | ¥5,367 | +¥2,633 |
| 6ヶ月目 | 90 | ¥30,000 | ¥8,000 | ¥3,000 | ¥41,000 | ¥5,367 | +¥35,633 |
| 12ヶ月目 | 90 | ¥50,000 | ¥15,000 | ¥5,000 | ¥70,000 | ¥5,367 | +¥64,633 |

**[推測]** 収入試算は以下の仮定に基づく:
- 1PF平均 1,000-10,000 views/動画（成長曲線）
- CPMベース: YT ¥100, IG ¥50, TikTok ¥20 (地域差あり)
- エンゲージメント率: 3-5%

---

## 7. リスク対策＆ミティゲーション

### 7.1 技術リスク

| リスク | 発生確率 | 影響度 | 対策 |
|--------|---------|--------|------|
| **API Rate Limit超過** | 中 | 高 | キューイング システム＋バックオフ (Exponential) |
| **動画生成失敗（Pika）** | 低 | 中 | 自動リトライ (3回)＋ Runway フォールバック |
| **BGM著作権侵害** | 低 | 高 | Epidemic Sounds License 確認自動化 |
| **プラットフォーム停止** | 極低 | 高 | スケジュール投稿（事前）＋監視ダッシュボード |
| **データ損失** | 低 | 中 | GCS バックアップ (自動, 7日保持) |

### 7.2 ビジネスリスク

| リスク | 対策 | 優先度 |
|--------|------|--------|
| **新規アカウント制限** | TikTok アカウント作成3ヶ月前倒し（育成期間確保） | 🔴 必須 |
| **アルゴリズム変動** | 日次エンゲージメント分析 → 週次テーマ最適化 | 🟠 重要 |
| **競合増加** | ニッチテーマ深掘り（金融×AI 等の複合） | 🟡 推奨 |
| **プラットフォーム規約変更** | Ayrshare 監視＋月次規約チェック | 🟡 推奨 |

---

## 8. 改訂履歴

| 版番 | 日付 | 変更内容 | 作成者 |
|------|------|---------|--------|
| v1.0 | 2026-03-07 | 仕様書初版作成 | Claude Code |
| — | — | — | — |

---

## 付録: 用語集

- **FLUX.2**: fal.ai の最新画像生成モデル (FLUX.1 Pro の改良版)
- **CPM (Cost Per Mille)**: 1000インプレッションあたりの広告単価
- **Ayrshare**: YouTube/Instagram/TikTok/X 等を一元管理する投稿管理ツール
- **Epidemic Sounds**: 商用利用OKの BGM / SE ライセンスサービス
- **Pika**: テキストまたは画像から高速に動画を生成するAIツール
- **Runway Gen-3**: テキスト or 画像→動画変換（高品質・時間要要）
- **VTT / SRT**: 字幕フォーマット
- **Content ID**: YouTube の著作権管理システム
- **Graph API**: Meta が提供する Facebook/Instagram 向け API
- **OAuth 2.0**: 標準的な認証・認可プロトコル

