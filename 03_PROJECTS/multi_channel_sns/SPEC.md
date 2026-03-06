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
  ├→ Ayrshare API / 個別 API 呼び出し
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
| **X** | T+0時間 | 即座に反応獲得（リアルタイム性重視） |
| **Instagram** | T+2時間 | 時間差で視聴者重複を避ける（エンゲージ分散） |
| **Pinterest** | T+24時間 | ピンの検索インデックス遅延を考慮 |
| **TikTok** | T+72時間 | 短尺動画トレンドに同期（将来） |

---

## 2. 各 SNS API 仕様・制限事項

### 2.1 Ayrshare API

#### 基本仕様

| 項目 | 仕様値 | 備考 |
|-----|------|------|
| **エンドポイント** | `https://api.ayrshare.com/api/post` | POST リクエスト |
| **認証** | Bearer Token（API Key） | `.env` で管理 |
| **レート制限** | 300 req/10分 | $29/月プラン |
| **タイムアウト** | 30秒 | リトライ 3回（指数バックオフ） |
| **対応 SNS** | Instagram / X / Pinterest / TikTok | TikTok は審査必須 |

#### リクエスト形式

```json
{
  "post": "投稿テキスト",
  "platforms": ["instagram", "twitter", "pinterest"],
  "mediaUrls": ["https://example.com/image.jpg"],
  "scheduledDate": "2026-03-07T10:00:00Z",
  "shortUrls": {
    "instagram": "https://youtube.com/watch?v=ABC123"
  }
}
```

#### レスポンス形式

```json
{
  "id": "POST_ID_xxx",
  "success": true,
  "platforms": {
    "instagram": {
      "id": "IG_POST_ID",
      "url": "https://instagram.com/p/ABC123"
    },
    "twitter": {
      "id": "TWEET_ID",
      "url": "https://twitter.com/user/status/123456"
    },
    "pinterest": {
      "id": "PIN_ID",
      "url": "https://pinterest.com/pin/123456"
    }
  }
}
```

#### 制限事項

- **メディアアップロード**: URL参照のみ（ローカルファイルアップロード不可）
  → YouTube CDN に動画をホストし、そのURLをAyrshareに渡す
- **Instagram 動画**: リール（Reels）は非対応、フィード投稿のみ
- **X 動画**: 15MB以下、MP4形式
- **Pinterest**: 最大2000x2000px、SVGは非対応

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

#### 基本仕様

| 項目 | 仕様値 |
|-----|------|
| **テキスト上限** | 280文字 |
| **メディア** | 画像4枚 or 動画1本 |
| **リプライ制限** | 連続リプライ不可（1リプライ = 1投稿扱い） |
| **URL短縮** | `t.co` 自動（計23文字） |

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

## 4. Ayrshare API 統合方法

### 4.1 基本フロー

```python
import aiohttp
from datetime import datetime, timedelta

class AyrshareClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.ayrshare.com/api"
        self.session = None

    async def post_to_sns(
        self,
        text: str,
        platforms: list,
        media_urls: list = None,
        scheduled_date: str = None,
        short_urls: dict = None,
    ) -> dict:
        """
        複数 SNS への一括投稿

        Args:
            text: 投稿テキスト
            platforms: ["instagram", "twitter", "pinterest"]
            media_urls: ["https://...image.jpg"]
            scheduled_date: ISO 8601 形式（例: "2026-03-07T10:00:00Z"）
            short_urls: プラットフォーム別のURL短縮設定

        Returns:
            {
              "id": "POST_ID",
              "success": true,
              "platforms": {...}
            }
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "post": text,
            "platforms": platforms,
        }

        if media_urls:
            payload["mediaUrls"] = media_urls

        if scheduled_date:
            payload["scheduledDate"] = scheduled_date

        if short_urls:
            payload["shortUrls"] = short_urls

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/post",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    raise Exception(f"Ayrshare API Error: {resp.status}")
```

### 4.2 エラーハンドリング

```python
class AyrshareRetryHandler:
    """
    Ayrshare API 呼び出しのリトライ・エラーハンドリング
    """

    @staticmethod
    async def post_with_retry(
        client: AyrshareClient,
        text: str,
        platforms: list,
        media_urls: list = None,
        max_retries: int = 3,
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
                result = await client.post_to_sns(
                    text=text,
                    platforms=platforms,
                    media_urls=media_urls,
                )
                return {"status": "success", "data": result}

            except Exception as e:
                wait_time = 5 * (3 ** attempt)  # 5, 15, 45
                logger.warning(
                    f"Ayrshare API failed (attempt {attempt+1}/{max_retries}). "
                    f"Retrying in {wait_time}s. Error: {str(e)}"
                )

                if attempt < max_retries - 1:
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Ayrshare API failed after {max_retries} retries.")
                    return {"status": "failed", "error": str(e)}
```

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
    def __init__(self, ayrshare_client: AyrshareClient):
        self.scheduler = AsyncIOScheduler()
        self.client = ayrshare_client
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
        """実際の投稿実行"""
        result = await AyrshareRetryHandler.post_with_retry(
            client=self.client,
            **content,
        )

        # ログ保存
        self._save_posting_log(post_id, result)
```

---

## 6. エラーハンドリング

### 6.1 想定エラー・対応策

| エラーシナリオ | 原因 | 対応策 |
|------------|------|--------|
| **Ayrshare API 5XX** | サーバー側エラー | 指数バックオフリトライ（3回） |
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
| **Ayrshare API** | $29/月 | 月産15本 × 3SNS = 45投稿 | $29 | レート制限：300/10分（余裕十分） |
| **Groq API** | $0 | 月産40本 × 5回/本 = 200呼び出し | $0 | 無料枠内（FreeモデルLlama 3.1） |
| **YouTube Data API** | $0 | 無料 | $0 | 400万 requests/日まで無料 |
| **Pexels/Unsplash** | $0 | API 呼び出し無制限 | $0 | 無料 |
| **EC2（既存）** | $10-15/月 | 既に運用中 | 含む | YouTube パイプライン共用 |
| **合計** | — | — | **$29/月** | 低コスト！ |

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
| **Ayrshare API 統合** | ✅ Instagram/X/Pinterest | + TikTok 個別API化 | **MUST** |
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
AYRSHARE_API_KEY=xxx
GROQ_API_KEY=xxx
INSTAGRAM_GRAPH_API_TOKEN=xxx（将来）
```

### 9.2 レート制限遵守

```python
# Groq: 30 req/min 以下
# Ayrshare: 300 req/10min 以下
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

