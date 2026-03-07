# マルチチャネル自動展開システム — SPEC.md

> 初版: 2026-03-07

---

## 1. システムアーキテクチャ概要

### 1.1 全体フロー図

```
YouTube 動画完成イベント
  ↓ (YouTube Data API webhook / Cron ポーリング)
  ↓
[トリガー検知モジュール]
  ├→ 動画メタデータ取得（タイトル・説明・サムネ）
  ├→ 処理ログ初期化
  └→ コンテンツ変換パイプラインへ
       ↓
[コンテンツ変換エンジン]
  ├→ Instagram 用テキスト生成 → 画像縮小 1080x1350
  ├→ X 用テキスト生成 → 画像保持 16:9
  ├→ Pinterest 用テキスト生成 → 画像拡大 1000x1500
  └→ (TikTok: 将来)
       ↓
[SNS 投稿モジュール]
  ├→ 直接API: Instagram Graph API + Pinterest API (X API は有料化のため除外)
  ├→ スケジュール管理（投稿時刻制御）
  └→ レスポンス検証 → ログ保存
       ↓
[効果測定・モニタリング]
  ├→ SNS 投稿後の反応監視（いいね・RT・PV）
  ├→ YouTube 訪問流入トラッキング
  └→ 週次レポート生成

```

### 1.2 投稿スケジュール戦略

| プラットフォーム | 投稿タイミング | 理由 |
|------------|----------|------|
| **YouTube** | T+0時間 | 投稿当日、9:00 JST |
| **X** | T+0時間 | 即座に反応獲得（リアルタイム性重視）⚠️ X API 2026年2月7日に完全有料化。手動投稿に切替 |
| **Instagram** | T+2時間 | 時間差で視聴者重複を避ける（エンゲージ分散） |
| **Pinterest** | T+24時間 | ピンの検索インデックス遅延を考慮 |
| **TikTok** | T+72時間 | 短尺動画トレンドに同期（将来） |

---

## 2. 各 SNS API 仕様・制限事項

### 2.1 投稿方式の変更（2026年3月更新）

**旧方式**: Ayrshare API ($29/月) による一括投稿
**新方式**: 各プラットフォームAPIへの直接投稿（無料）

| プラットフォーム | API | 月額 | 備考 |
|---|---|---|---|
| Instagram | Graph API v17.0 | ¥0 | ビジネスアカウント必須。フィード投稿のみ（Reels/Stories非対応） |
| Pinterest | Pinterest API v5 | ¥0 | ビジネスアカウント必須 |
| YouTube | YouTube Data API v3 | ¥0 | 既存利用中 |
| X (Twitter) | ❌ 有料化 | — | 2026年2月7日から従量課金。手動投稿に切替 |

#### 変更理由

- Ayrshare API は $29/月の固定費が発生。月産15本程度では費用対効果が低い
- Instagram Graph API / Pinterest API は無料で直接利用可能
- X API は2026年2月7日から完全有料化（Free tier 廃止）のため自動投稿を断念

---

### 2.2 Instagram Graph API（個別API、将来拡張用）

#### 基本仕様

| 項目 | 仕様値 |
|-----|------|
| **対応** | フィード投稿のみ（Reels/Stories NG） |
| **メディア上限** | 8ファイル/投稿 |
| **キャプション上限** | 2,200文字 |
| **ハッシュタグ上限** | 30個（ただしエンゲージ効果は10個まで） |

#### ハッシュタグ規約

```
# NG パターン
❌ #AI #AI #AI #AI ...（同一タグ連投）
❌ #xxxxx以上（ユーザー定義タグ禁止）

# OK パターン
✅ #AI #節約 #自動化 #テック #日本 #2026 ...（多様性・関連性重視）
```

---

### 2.3 X API v2

> ⚠️ **重要: X API は2026年2月7日から完全有料化**
> Free tier が廃止され、全てのリクエストが従量課金に移行。
> - 投稿読取: $0.005/リクエスト
> - ユーザー読取: $0.010/リクエスト
> - 投稿作成: 有料プラン必須
>
> **推奨対応**: 自動投稿は断念し、手動投稿 or IFTTT連携に切替。
> コンテンツ変換エンジンでテキスト生成のみ行い、手動コピペで投稿する運用とする。

#### 基本仕様

| 項目 | 仕様値 |
|-----|------|
| **テキスト上限** | 280文字 |
| **メディア** | 画像4枚 or 動画1本 |
| **リプライ制限** | 連続リプライ不可（1リプライ = 1投稿扱い） |
| **URL短縮** | `t.co` 自動（計23文字） |
| **API料金** | ❌ 有料化（2026年2月7日〜）— 自動投稿不可 |

#### テキスト最適化例

```
【AI×節約】月5万円を自動節約？
多くの人は…🤔
✅ 3つのポイントで解説
📺 動画で詳細を確認
https://youtube.com/watch?v=ABC123
#AI #節約 #自動化
```

**文字数**: 280文字以内、絵文字・記号で視認性向上。

---

### 2.4 Pinterest API

#### 基本仕様

| 項目 | 仕様値 |
|-----|------|
| **ピン説明** | 500文字以上推奨（SEO） |
| **リンク** | 商用リンク必須（ピンURL + 流入元URL） |
| **画像サイズ** | 1000x1500px（縦長）推奨 |

#### SEO キーワード配置

```
【タイトル（30字以内）】: AI で月5万円節約する3つの方法

【説明（80-150字）】:
AI を使った自動貯蓄・家計管理で、手間なく月5万円を節約できます。
手数料は0円。初心者向けに3つの実践方法を紹介。
多くのサラリーマンが実践中。

【キーワード】: AI 節約 家計管理 貯蓄 自動化 テック 初心者向け 無料
```

---

### 2.5 TikTok Business API（将来用、V1では非対応）

#### 基本仕様

| 項目 | 仕様値 |
|-----|------|
| **対応** | 審査必須。月間10万フォロワー推奨 |
| **動画長** | 15秒～60秒 |
| **エンドポイント** | `https://open.tiktokapis.com/v1/post/publish/video/init/` |
| **ハッシュタグ上限** | 10個 |

**参考**: TikTok API は個人アカウントでの利用困難（申請難度高）。
初期段階は手動投稿 or 外部ツール（Later等）で対応。

---

## 3. コンテンツ変換ロジック（プラットフォーム別）

### 3.1 変換エンジンの構成

```python
class ContentTransformer:
    def __init__(self, youtube_metadata: dict):
        self.title = youtube_metadata["title"]  # 例: "AI で月5万円節約する3つの方法"
        self.description = youtube_metadata["description"]
        self.thumbnail_url = youtube_metadata["thumbnail"]
        self.video_id = youtube_metadata["video_id"]
        self.duration_sec = youtube_metadata["duration"]

    def to_instagram(self) -> dict:
        """Instagram 用コンテンツ生成"""
        pass

    def to_twitter(self) -> dict:
        """X 用コンテンツ生成"""
        pass

    def to_pinterest(self) -> dict:
        """Pinterest 用コンテンツ生成"""
        pass

    def to_tiktok(self) -> dict:
        """TikTok 用コンテンツ生成（将来）"""
        pass
```

### 3.2 Instagram 用変換ルール

#### テキスト生成

**入力**: YouTube タイトル + 説明（動画時間15分想定）
**出力**: 要約150字 + ハッシュタグ10個

**プロンプト** (Groq):

```
以下の YouTube 動画を Instagram フィード投稿用に要約してください。

動画タイトル: {title}
動画説明: {description}
動画長: {duration_sec}秒

要件:
- 要約テキスト: 150字以下
- トーン: カジュアル・親しみやすい
- 絵文字: 2-3個活用
- ハッシュタグ: 関連度の高い順に10個

出力形式:
{
  "caption": "...",
  "hashtags": ["#...", "#...", ...]
}
```

**例**:
```
AI が自動で家計を最適化？🤖
月5万円の貯蓄を手間なく実現。

✅ 初心者でもわかる3つのステップ
✅ 手数料は0円
✅ すぐ始められる

動画では詳しく解説しています。
プロフィールのリンク or YouTube で確認🎥

#AI #節約 #家計管理 #貯蓄 #自動化 #テック #初心者向け #無料ツール #副業 #資産運用
```

#### 画像変換

**入力**: YouTube サムネイル（1280x720）
**出力**: Instagram 縦長サムネイル（1080x1350）

**変換ロジック** (Pillow):

```python
def resize_to_instagram(youtube_thumbnail_path: str) -> str:
    """
    YouTube 16:9 → Instagram 4:5 に変換

    方法: キャンバス拡大 + 中央配置 + グラデーション背景
    """
    img = Image.open(youtube_thumbnail_path)

    # 1. 元画像を 1080x607 にリサイズ（4:5アスペクト内に収まるように）
    img_resized = img.resize((1080, 607), Image.Resampling.LANCZOS)

    # 2. 1080x1350 のキャンバスを作成（グラデーション背景）
    canvas = Image.new('RGB', (1080, 1350))
    gradient = _create_gradient_background()  # グラデーション生成
    canvas.paste(gradient, (0, 0))

    # 3. 元画像を中央に配置
    offset_y = (1350 - 607) // 2  # 垂直中央
    canvas.paste(img_resized, (0, offset_y))

    # 4. テキストオーバーレイ（タイトル・CTA）
    draw = ImageDraw.Draw(canvas)
    draw.text((540, 1200), "動画をチェック ↓", fill='white', anchor='mm')

    return canvas.save(f"instagram_{uuid.uuid4().hex[:8]}.png")
```

---

### 3.3 X 用変換ルール

#### テキスト生成

**入力**: YouTube タイトル（40字以内に要約）
**出力**: 核心1行 + URL + ハッシュタグ3個（計280字以下）

**プロンプト** (Groq):

```
YouTube 動画を X（Twitter）投稿用にまとめてください。

動画タイトル: {title}

要件:
- キャッチ: 「【分野 × キーワード】」形式（パワーワード優先）
- 説明: 1-2行で核心を伝える
- URL: YouTube リンク
- ハッシュタグ: 関連度の高い順に3個
- 合計280文字以下

出力形式:
{
  "text": "...",
  "hashtags": ["#...", "#..."]
}
```

**例**:
```
【AI × 節約】月5万円を自動化？
多くの人は家計管理に時間を使いすぎています。
AI ツールを使えば、わずか5分で月5万円を節約できます。
3つの実践方法を動画で解説👇
https://youtu.be/ABC123
#AI #節約 #自動化
```

**文字数計算**: URL は t.co で23文字に自動短縮。

---

### 3.4 Pinterest 用変換ルール

#### テキスト生成

**入力**: YouTube タイトル + 説明（15分動画想定）
**出力**: SEO 最適化テキスト（80-150字）+ キーワード

**プロンプト** (Groq):

```
YouTube 動画を Pinterest ピン用に最適化してください。

動画タイトル: {title}
動画説明: {description}

要件:
- ピンタイトル: 40字以内、キーワードを含む
- 説明: 80-150字、SEO キーワード自然配置
- キーワード: 7-10個（検索性重視）
- リンク: YouTube URL（クリックスルー）

出力形式:
{
  "title": "...",
  "description": "...",
  "keywords": ["...", "..."]
}
```

**例**:
```
【ピンタイトル】
AI で月5万円節約する3つの方法｜自動貯蓄・家計管理ガイド

【説明】
AI を使った自動貯蓄・家計管理で、手間なく月5万円を節約できます。
手数料は0円。初心者向けに3つの実践方法を紹介。
多くのサラリーマンが実践中の方法をステップバイステップで解説。

【キーワード】
AI 節約 家計管理 貯蓄 自動化 テック 初心者向け 無料 資産運用
```

#### 画像変換

**入力**: YouTube サムネイル（1280x720）
**出力**: Pinterest 縦長ピン（1000x1500）

**変換ロジック** (Pillow):

```python
def resize_to_pinterest(youtube_thumbnail_path: str, title: str) -> str:
    """
    YouTube 16:9 → Pinterest 2:3 に変換

    方法: 上部に元画像、下部にタイトル・説明文を配置
    """
    img = Image.open(youtube_thumbnail_path)

    # 1. 元画像を 1000x562 にリサイズ（2:3 の上部に収まるように）
    img_resized = img.resize((1000, 562), Image.Resampling.LANCZOS)

    # 2. 1000x1500 のキャンバスを作成
    canvas = Image.new('RGB', (1000, 1500), color='#FFFFFF')

    # 3. 元画像を上部に配置
    canvas.paste(img_resized, (0, 0))

    # 4. テキスト領域（下部700px）
    draw = ImageDraw.Draw(canvas)

    # タイトル
    draw.text((50, 600), title, fill='#000000', font=_load_font('bold', 28),
              anchor='lm', align='center')

    # サブテキスト
    subtext = "クリックして動画で詳しく学ぶ"
    draw.text((50, 700), subtext, fill='#666666', font=_load_font('regular', 18))

    return canvas.save(f"pinterest_{uuid.uuid4().hex[:8]}.png")
```

---

## 4. SNS 直接API統合方法（Ayrshare 廃止後）

### 4.1 Instagram Graph API クライアント

```python
import httpx
from datetime import datetime

class InstagramClient:
    """
    Instagram Graph API v17.0 を使ったフィード投稿

    前提:
    - ビジネスアカウント or クリエイターアカウント
    - Facebook ページと連携済み
    - Graph API トークン取得済み（.env で管理）
    """

    def __init__(self, access_token: str, ig_user_id: str):
        self.access_token = access_token
        self.ig_user_id = ig_user_id
        self.base_url = "https://graph.facebook.com/v17.0"

    async def post_image(self, image_url: str, caption: str) -> dict:
        """
        Instagram フィード画像投稿（2ステップ）

        Step 1: メディアコンテナ作成
        Step 2: メディア公開
        """
        async with httpx.AsyncClient(timeout=30) as client:
            # Step 1: コンテナ作成
            container_resp = await client.post(
                f"{self.base_url}/{self.ig_user_id}/media",
                params={
                    "image_url": image_url,
                    "caption": caption,
                    "access_token": self.access_token,
                },
            )
            container = container_resp.json()
            container_id = container["id"]

            # Step 2: 公開
            publish_resp = await client.post(
                f"{self.base_url}/{self.ig_user_id}/media_publish",
                params={
                    "creation_id": container_id,
                    "access_token": self.access_token,
                },
            )
            return publish_resp.json()
```

### 4.2 Pinterest API クライアント

```python
class PinterestClient:
    """
    Pinterest API v5 を使ったピン投稿

    前提:
    - ビジネスアカウント
    - API アプリ登録済み
    - アクセストークン取得済み
    """

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://api.pinterest.com/v5"

    async def create_pin(
        self, board_id: str, title: str, description: str,
        image_url: str, link: str
    ) -> dict:
        """
        Pinterest ピン作成

        Args:
            board_id: 投稿先ボード ID
            title: ピンタイトル（40字以内推奨）
            description: SEO最適化テキスト（80-150字）
            image_url: 画像 URL（1000x1500推奨）
            link: YouTube 動画リンク
        """
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{self.base_url}/pins",
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json",
                },
                json={
                    "board_id": board_id,
                    "title": title,
                    "description": description,
                    "media_source": {
                        "source_type": "image_url",
                        "url": image_url,
                    },
                    "link": link,
                },
            )
            return resp.json()
```

### 4.3 SNS リトライハンドラー（共通）

```python
class SNSRetryHandler:
    """
    各 SNS API 呼び出しの共通リトライ・エラーハンドリング
    """

    @staticmethod
    async def post_with_retry(
        post_func,
        max_retries: int = 3,
        **kwargs,
    ) -> dict:
        """
        指数バックオフでリトライ

        リトライ戦略:
          - 失敗1回目: 5秒後に再試行
          - 失敗2回目: 15秒後に再試行
          - 失敗3回目: 45秒後に再試行
          - 最終失敗: エラーログ記録＆スキップ
        """
        for attempt in range(max_retries):
            try:
                result = await post_func(**kwargs)
                return {"status": "success", "data": result}

            except Exception as e:
                wait_time = 5 * (3 ** attempt)  # 5, 15, 45
                logger.warning(
                    f"SNS API failed (attempt {attempt+1}/{max_retries}). "
                    f"Retrying in {wait_time}s. Error: {str(e)}"
                )

                if attempt < max_retries - 1:
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"SNS API failed after {max_retries} retries.")
                    return {"status": "failed", "error": str(e)}
```

> **Note**: YouTube は既存パイプラインで対応済み。X (Twitter) は API 有料化のため自動投稿対象外。
> X 向けテキストはコンテンツ変換エンジンで生成し、手動投稿する運用とする。

---

## 5. 投稿スケジューリング戦略

### 5.1 時刻制御ロジック

| プラットフォーム | 基準時間 | オフセット | 投稿時刻例（YouTube 9:00 JST） |
|------------|--------|---------|--------------------------|
| **YouTube** | T+0 | +0時間 | 09:00 |
| **X** | T+0 | +0時間 | 09:00 |
| **Instagram** | T+2 | +2時間 | 11:00 |
| **Pinterest** | T+24 | +24時間 | 翌日 09:00 |

**実装例**:

```python
from datetime import datetime, timedelta
import pytz

def calculate_posting_schedule(youtube_upload_time: datetime) -> dict:
    """
    YouTube アップロード時刻から各 SNS の投稿時刻を計算

    Args:
        youtube_upload_time: YouTube 動画の公開時刻（JST）

    Returns:
        {
          "instagram": "2026-03-07T11:00:00+09:00",
          "twitter": "2026-03-07T09:00:00+09:00",
          "pinterest": "2026-03-08T09:00:00+09:00"
        }
    """
    jst = pytz.timezone('Asia/Tokyo')

    schedule = {
        "twitter": youtube_upload_time.isoformat(),
        "instagram": (youtube_upload_time + timedelta(hours=2)).isoformat(),
        "pinterest": (youtube_upload_time + timedelta(hours=24)).isoformat(),
    }

    return schedule
```

### 5.2 キューイング・スケジューラー

```python
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

class SNSScheduler:
    def __init__(self, instagram_client: InstagramClient, pinterest_client: PinterestClient):
        self.scheduler = AsyncIOScheduler()
        self.instagram = instagram_client
        self.pinterest = pinterest_client
        self.queue = {}  # {post_id: [待機中の投稿]}

    async def schedule_post(
        self,
        post_id: str,
        content: dict,
        scheduled_date: datetime,
    ):
        """
        投稿をスケジュールに追加

        Args:
            post_id: YouTube 動画 ID
            content: {"text": "...", "platforms": [...], "media_urls": [...]}
            scheduled_date: 投稿予定時刻（JST）
        """
        # APScheduler に投稿タスクを登録
        self.scheduler.add_job(
            self._execute_post,
            trigger='date',
            run_date=scheduled_date,
            args=[post_id, content],
            id=f"{post_id}_{scheduled_date.timestamp()}",
        )

        logger.info(f"Scheduled post {post_id} at {scheduled_date}")

    async def _execute_post(self, post_id: str, content: dict):
        """実際の投稿実行（各プラットフォームAPI直接呼び出し）"""
        results = {}

        # Instagram 投稿
        if "instagram" in content.get("platforms", []):
            results["instagram"] = await SNSRetryHandler.post_with_retry(
                self.instagram.post_image,
                image_url=content["media_urls"][0],
                caption=content["text_instagram"],
            )

        # Pinterest 投稿
        if "pinterest" in content.get("platforms", []):
            results["pinterest"] = await SNSRetryHandler.post_with_retry(
                self.pinterest.create_pin,
                board_id=content["pinterest_board_id"],
                title=content["title_pinterest"],
                description=content["text_pinterest"],
                image_url=content["media_urls"][0],
                link=content["youtube_url"],
            )

        # X は手動投稿のため自動投稿対象外

        # ログ保存
        self._save_posting_log(post_id, results)
```

---

## 6. エラーハンドリング

### 6.1 想定エラー・対応策

| エラーシナリオ | 原因 | 対応策 |
|------------|------|--------|
| **SNS API 5XX** | サーバー側エラー | 指数バックオフリトライ（3回） |
| **ネットワークタイムアウト** | API応答遅延 | 30秒タイムアウト + リトライ |
| **認証エラー（401）** | API Key 無効 | `.env` 再確認・ログアラート |
| **メディアURL不正** | 画像 URL 期限切れ/存在しない | CDN キャッシュ確認・リアップロード |
| **テキストエンコーディング** | 絵文字・特殊文字エラー | UTF-8 検証 + 文字正規化 |
| **プラットフォームダウン** | SNS 側の障害 | 投稿スキップ + 手動リトライキュー記録 |

### 6.2 ログ構造

```python
import json
from datetime import datetime

class PostingLog:
    def __init__(self, post_id: str):
        self.post_id = post_id
        self.timestamp = datetime.now(pytz.timezone('Asia/Tokyo'))
        self.events = []

    def add_event(self, stage: str, status: str, detail: dict = None):
        """
        ログに事象を追加

        Args:
            stage: "trigger", "content_generation", "posting", "verification"
            status: "pending", "success", "failed", "skipped"
            detail: {"platform": "instagram", "error": "..."}
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "stage": stage,
            "status": status,
        }
        if detail:
            event.update(detail)

        self.events.append(event)

    def save(self, output_dir: str = "./logs/sns_posting"):
        """JSON ファイルに保存"""
        os.makedirs(output_dir, exist_ok=True)

        log_file = os.path.join(
            output_dir,
            f"post_{self.post_id}_{self.timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        )

        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump({
                "post_id": self.post_id,
                "timestamp": self.timestamp.isoformat(),
                "events": self.events,
            }, f, indent=2, ensure_ascii=False)
```

---

## 7. コスト試算

### 7.1 月間コスト内訳

| サービス | 料金 | 使用量（想定） | 月額 | 備考 |
|---------|------|-------------|------|------|
| **Instagram Graph API** | ¥0 | 月産15本投稿 | ¥0 | ビジネスアカウント必須。無料 |
| **Pinterest API v5** | ¥0 | 月産15本投稿 | ¥0 | ビジネスアカウント必須。無料 |
| **X (Twitter) API** | ❌ 除外 | — | — | 2026年2月7日から有料化。手動投稿に切替 |
| **Groq API** | ¥0 | 月産40本 × 5回/本 = 200呼び出し | ¥0 | 無料枠内（FreeモデルLlama 3.1） |
| **YouTube Data API** | ¥0 | 無料 | ¥0 | 400万 requests/日まで無料 |
| **Pexels/Unsplash** | ¥0 | API 呼び出し無制限 | ¥0 | 無料 |
| **EC2（既存）** | $10-15/月 | 既に運用中 | 含む | YouTube パイプライン共用 |
| **合計** | — | — | **¥0/月**（EC2除く） | Ayrshare $29/月を完全排除！ |

### 7.2 ROI 試算

**想定**: YouTube 月産15本 → SNS 経由で月+500~1000 登録者獲得

```
月間投稿数:
  YouTube: 15本
  Instagram: 15本
  X: 15本
  Pinterest: 15本
  ────────────────
  合計: 60本

想定エンゲージメント（月次）:
  Instagram: 15投稿 × 50いいね = 750 いいね
  X: 15投稿 × 30 RT = 450 RT
  Pinterest: 15ピン × 20保存 = 300保存
  ────────────────
  SNS 経由の YouTube リンククリック: 月+500~1000回

YouTube 登録者増加:
  月1000回訪問 × 5% CTR = 月+50登録者（保守的）
  6ヶ月後: 累計+300登録者
  12ヶ月後: 累計+600登録者

収益化目標:
  1000登録者 × 月2-3回再生 = 月1000-1500回再生
  年間目標: 年1万2000-1万8000回再生 → 月額 $100-200 収益化見込み
```

---

## 8. MVP 仕様 vs V1 差分

| 機能 | MVP（Phase 1） | V1（Phase 2+） | 優先度 |
|-----|-------------|-----------|--------|
| **SNS 直接API統合** | ✅ Instagram/Pinterest（X は手動） | + TikTok 個別API化 | **MUST** |
| **コンテンツ変換** | ✅ 3SNS用テキスト自動生成 | + 個別画像最適化 | **MUST** |
| **スケジューリング** | ✅ 時差投稿（T+0/+2/+24） | + A/Bテスト機能 | **SHOULD** |
| **エラーハンドリング** | ✅ リトライ3回 + ログ | + アラート通知 | **SHOULD** |
| **効果測定** | ✅ ログ記録 | + リアルタイムダッシュボード | **COULD** |
| **TikTok 対応** | ❌ 非対応 | ✅ 短尺切り出し | **FUTURE** |

---

## 9. セキュリティ・データ管理

### 9.1 API キー管理

```
.env（Git無視）:
GROQ_API_KEY=xxx
INSTAGRAM_GRAPH_API_TOKEN=xxx
INSTAGRAM_BUSINESS_ACCOUNT_ID=xxx
PINTEREST_API_KEY=xxx
```

### 9.2 レート制限遵守

```python
# Groq: 30 req/min 以下
# Instagram Graph API: 200 req/hour 以下
# Pinterest API: 1000 req/day 以下
# Pexels: 200 req/hour 以下

from ratelimit import limits, sleep_and_retry

@sleep_and_retry
@limits(calls=30, period=60)
async def call_groq_api():
    pass
```

### 9.3 ログ保有・削除ポリシー

- **保有期限**: 90日間
- **削除方針**: 自動削除スクリプト（月次実行）
- **機密情報**: API Key ・トークンは**ログに含めない**

---

## 10. テスト戦略（Phase 1 終了時）

| テスト | 方法 | 合格基準 |
|--------|------|--------|
| **単体テスト** | 各コンテンツ変換関数 | 100%カバレッジ |
| **統合テスト** | YouTube → 3SNS 投稿完全フロー | 3本の動画で成功 |
| **A/B テスト** | テキスト2パターン × 2投稿 | CTR / エンゲージ比較 |
| **エラーテスト** | API 遅延・失敗をシミュレート | リトライ動作確認 |

