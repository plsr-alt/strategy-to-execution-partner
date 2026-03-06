# AI Visual Influencer — TODO

## 進捗管理
**現在のフェーズ**: Pre-Launch（キャラクター確定待ち）
**開始予定日**: 2026-03-10
**目標ローンチ日**: 2026-03-17 (Week 1 完了後)

---

## Phase 0: キャラクター設計 & LoRA学習準備（Week 1: Mar 10-16）

### M0-1: キャラクター確定と詳細設定
**期限**: Mar 10（木）
**担当**: ユーザー決定 → Claude 実装

- [ ] **決定**: Mika / Rena / Sora の最終選択
  - 意思決定軸: 既存リソース（YouTube）との相乗効果度、個人興味、市場規模
  - 参照: SPEC.md Section 1 (各キャラ詳細)

- [ ] **確認**: 選定キャラの投稿テーマ 7個を確認・修正
  - 例（Mika）: 月=週間見通し、火=銘柄分析... etc
  - 修正があれば SPEC.md Section 4-1 を更新

- [ ] **確認**: キャラクタービジュアル定義が具体的か
  - 年齢・ドレスコード・背景・表情パターン（SPEC.md Section 1-1/-2/-3）
  - 不明な点は画像サンプル（Pinterest/Instagram）を集める

**成果物**: SPEC.md Section 1 確定版（確定日を明記）

---

### M0-2: LoRA 学習用データセット準備
**期限**: Mar 12（土）
**担当**: Claude / ユーザー（撮影 or リクエスト）

#### 撮影パターン（50-100枚）
- [ ] **角度バリエーション**: 正面 / 左横 45° / 右横 45° / 上目遣い / 俯瞰
- [ ] **照明バリエーション**: 昼光 / スタジオ（白背景）/ 温白色 / 屋外自然光
- [ ] **背景バリエーション**: 白背景 / オフィス / 屋外 / スタジオ（その他色）
- [ ] **衣装バリエーション**: メイン衣装 × 3-5色 / アクセサリー有無
- [ ] **表情バリエーション**: 笑顔 / 真摯 / 親切 / 驚き / リラックス

#### オプション（セルフ撮影推奨）
- [ ] **撮影環境準備**: スマートフォン / 背景布 / ライト
- [ ] **実際の撮影**: 上記パターンで 50-100 枚を 2-3 日かけて実施
  - **予想時間**: 2時間/day × 2-3day = 4-6時間
  - **機材コスト**: $0（スマートフォン既存利用）

#### 外注オプション（価格: $300-500）
- [ ] **プロ写真家リクエスト**: Fiverr / Upwork で「AI training dataset」で検索
  - 単価: $200-400
  - ターンアラウンド: 3-5日
  - 品質: 高い一貫性

**成果物**: `00_INBOX/lora_training_dataset_<character>.zip` (100MB 程度)

---

### M0-3: Python 自動化スクリプト開発
**期限**: Mar 14（月）
**担当**: Claude（実装） / ユーザー（テスト）

#### スクリプト 1: `generate_image.py`
**機能**: fal.ai API を通じた画像生成
```python
# 疑似コード
import fal
from datetime import datetime

def generate_daily_image(character: str, theme: str, expression: str):
    """
    - character: "mika", "rena", "sora"
    - theme: 投稿テーマ（コンテンツカレンダーから取得）
    - expression: 表情パターン
    """
    lora_id = get_lora_id(character)  # 学習済み LoRA ID
    prompt = build_prompt(character, theme, expression)

    image_url = fal.generate_image(
        model="flux-pro",
        lora_id=lora_id,
        prompt=prompt,
        output_format="jpeg",
        image_size=(1080, 1350)
    )

    # 出力: `outputs/YYYY-MM-DD_<character>_<theme>.jpg`
    return image_url

# 実行例
generate_daily_image("mika", "weekly_forecast", "serious")
```

**実装チェック**:
- [ ] fal.ai アカウント作成 & API キー取得
- [ ] `requirements.txt` に `fal-ai` を追加
- [ ] プロンプトテンプレート 5-6 パターンを定義（表情別）
- [ ] 出力ディレクトリ構造を定義

#### スクリプト 2: `generate_caption.py`
**機能**: Groq API で投稿文自動生成
```python
# 疑似コード
from groq import Groq

def generate_caption(character: str, theme: str, language: str = "ja"):
    """
    - character: キャラ人格定義
    - theme: 投稿テーマ（コンテンツカレンダーから）
    - language: "ja" or "en"

    出力: 150-300 文字の投稿文 + ハッシュタグ 10 個
    """

    system_prompt = f"""
    あなたは {character} というインフルエンサーです。
    人格: {get_character_personality(character)}
    投稿トーン: {get_character_tone(character)}

    与えられたテーマについて、Instagram 用の投稿文を作成してください。
    - 文字数: 150-300 字
    - ハッシュタグ: 10 個をリストアップ
    - 言語: {language}
    - CTA: 次投稿へのフックを含める
    """

    client = Groq()
    response = client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"テーマ: {theme}"}
        ],
        temperature=0.7,
        max_tokens=400
    )

    return response.choices[0].message.content

# 実行例
caption = generate_caption("mika", "週間相場見通し", "ja")
# 出力: "こんにちは。今週は日経平均が... #投資初心者向け #株式相場 ..."
```

**実装チェック**:
- [ ] Groq アカウント作成 & API キー取得
- [ ] キャラクター定義（人格・トーン）を `characters.py` に集約
- [ ] テーマ別プロンプトテンプレート 7 個（Mika 例: 月=週間見通し etc）

#### スクリプト 3: `post_to_instagram.py`
**機能**: Instagram Graph API で画像+キャプション投稿
```python
# 疑似コード
import instagrapi
from datetime import datetime, timedelta

def post_to_instagram(image_url: str, caption: str, schedule_time: str = "now"):
    """
    - image_url: 生成済み画像の URL
    - caption: 生成済みキャプション
    - schedule_time: "now" or "2026-03-17 07:00" 等
    """

    client = instagrapi.Client()
    client.login(username=os.getenv("IG_USERNAME"), password=os.getenv("IG_PASSWORD"))

    if schedule_time == "now":
        client.photo_upload(image_url, caption=caption)
    else:
        # スケジュール投稿（Instagram Creator Studio経由）
        # または24時間後に投稿するキューに登録
        schedule_post(image_url, caption, schedule_time)

    return post_id

# 実行例
post_to_instagram(
    image_url="outputs/2026-03-17_mika_weekly.jpg",
    caption="こんにちは。今週は...",
    schedule_time="2026-03-18 07:00"
)
```

**実装チェック**:
- [ ] Instagram Meta App ID 取得 & 権限設定
- [ ] Graph API トークン取得（長期トークン推奨）
- [ ] スケジュール投稿の仕組み決定（24時間後投稿 or Cloud Scheduler）

#### スクリプト 4: `post_to_x.py`
**機能**: X API v2 で投稿
```python
# 疑似コード
import tweepy

def post_to_x(image_url: str, caption: str, schedule_offset_minutes: int = 30):
    """
    - image_url: 生成済み画像 URL
    - caption: 投稿文（280字以内に短縮）
    - schedule_offset_minutes: Instagram投稿の何分後に投稿するか

    注: X API v2 はスケジュール機能がないため、30分後に別プロセスで実行
    """

    client = tweepy.Client(
        bearer_token=os.getenv("X_BEARER_TOKEN"),
        consumer_key=os.getenv("X_CONSUMER_KEY"),
        consumer_secret=os.getenv("X_CONSUMER_SECRET"),
        access_token=os.getenv("X_ACCESS_TOKEN"),
        access_token_secret=os.getenv("X_ACCESS_TOKEN_SECRET")
    )

    # 画像アップロード
    media = client.upload_media(filename=image_url)

    # 投稿文を 280 字以内に短縮
    short_caption = caption[:280]

    response = client.create_tweet(
        text=short_caption,
        media_ids=[media.data['media_key']]
    )

    return response.data['id']

# 実行例（30分後実行用）
post_to_x(image_url="outputs/2026-03-17_mika_weekly.jpg", caption="こんにちは。今週の相場は...")
```

**実装チェック**:
- [ ] X API v2 アクセス取得（Verified Account 必須）
- [ ] Bearer Token + OAuth 1.0a 認証設定
- [ ] Cloud Scheduler で 30 分遅延実行を設定

#### スクリプト 5: `daily_pipeline.py`（オーケストレーション）
**機能**: 上記スクリプト 1-4 を順次実行
```python
# 疑似コード
from generate_image import generate_daily_image
from generate_caption import generate_caption
from post_to_instagram import post_to_instagram
from post_to_x import post_to_x
from get_content_calendar import get_today_content

def run_daily_pipeline():
    """
    毎日 23:00 に実行（翌日の投稿を事前生成）
    """

    # 1. 本日のコンテンツプランを取得
    today_plan = get_today_content(character="mika")  # SPEC.md コンテンツカレンダーから
    character = today_plan['character']
    theme = today_plan['theme']
    expression = today_plan['expression']

    # 2. 画像生成
    image_url = generate_daily_image(character, theme, expression)
    print(f"✓ Image generated: {image_url}")

    # 3. キャプション生成
    caption = generate_caption(character, theme, language="ja")
    print(f"✓ Caption generated: {caption[:100]}...")

    # 4. Instagram に投稿スケジュール（24時間後）
    tomorrow_time = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d 07:00")
    ig_post_id = post_to_instagram(image_url, caption, schedule_time=tomorrow_time)
    print(f"✓ Instagram scheduled: {ig_post_id}")

    # 5. X 投稿を 30 分後に実行予約
    # （Cloud Scheduler で再度このスクリプトを呼び出し、post_to_x フェーズのみ実行）
    queue_x_post(image_url, caption, delay_minutes=30)
    print(f"✓ X post queued: {delay_minutes}min later")

    # 6. ログ記録
    log_to_sheets(
        date=datetime.now().strftime("%Y-%m-%d"),
        character=character,
        theme=theme,
        image_url=image_url,
        caption=caption,
        status="scheduled"
    )

# 実行例
if __name__ == "__main__":
    run_daily_pipeline()
```

**実装チェック**:
- [ ] エラーハンドリング（API 失敗時のリトライ）
- [ ] ログレベル（DEBUG/INFO/ERROR）を設定
- [ ] Google Cloud Scheduler or GitHub Actions で毎日 23:00 実行

#### スクリプト 6: `monitor_engagement.py`
**機能**: Instagram/X メトリクスを毎日取得
```python
# 疑似コード
from instagram_api import get_insights
from x_api import get_tweet_metrics
from google_sheets import append_to_sheet

def monitor_daily_engagement():
    """
    毎日 08:00 に実行（前日投稿のメトリクス取得）
    """

    # 1. Instagram 前日投稿のメトリクス
    ig_metrics = get_insights(
        metric_types=["likes", "comments", "shares", "saves"],
        date_from=(datetime.now() - timedelta(days=1))
    )

    # 2. X 前日投稿のメトリクス
    x_metrics = get_tweet_metrics(days_back=1)

    # 3. エンゲージメント率算出
    ig_engagement_rate = (ig_metrics['likes'] + ig_metrics['comments']) / followers
    x_engagement_rate = (x_metrics['likes'] + x_metrics['retweets']) / x_followers

    # 4. Google Sheets に追記
    append_to_sheet(
        sheet_id=SHEET_ID,
        values=[
            [datetime.now().strftime("%Y-%m-%d"), ig_metrics, x_metrics, ig_engagement_rate]
        ]
    )

    return ig_metrics, x_metrics

# 実行例
if __name__ == "__main__":
    monitor_daily_engagement()
```

**実装チェック**:
- [ ] Instagram Graph API Insights 権限確認
- [ ] X API v2 Metrics 権限確認
- [ ] Google Sheets 追記権限確認

**成果物**:
- [ ] `src/generate_image.py`
- [ ] `src/generate_caption.py`
- [ ] `src/post_to_instagram.py`
- [ ] `src/post_to_x.py`
- [ ] `src/daily_pipeline.py`
- [ ] `src/monitor_engagement.py`
- [ ] `requirements.txt`（fal-ai, groq, instagrapi, tweepy, google-sheets等）
- [ ] `.env.example`（API キーテンプレート）

---

### M0-4: SNS アカウント開設 & プロフィール設定
**期限**: Mar 15（火）
**担当**: ユーザー（アカウント作成） → Claude（プロフィール最適化）

#### Instagram
- [ ] **アカウント開設**: @mika_financial_analyst （キャラに応じて名前変更）
- [ ] **プロフィール画像**: 第1投稿で使用する典型的なキャラ画像
- [ ] **バイオ記述（150字以内）**:
  ```
  📈 AI金融アナリスト | 毎日投資を学べる
  💼 初心者向けテクニカル分析＆ファンダメンタルズ
  ⚠️ このアカウントはAI生成コンテンツを配信しています
  → リンク: [YouTube チャネル]
  ```
- [ ] **リンク**: YouTube チャネル / ブログ等へのリダイレクト
- [ ] **ハイライト**: 「投資入門」「チャート解説」「Q&A」等 3-5個作成予定
- [ ] **Close Friends**: 初期はなし（フォロワー増後に限定機能を検討）

#### X（Twitter）
- [ ] **アカウント開設**: @mika_analyst
- [ ] **プロフィール**:
  ```
  📊 AI金融アナリスト Mika
  毎日の相場解説 & 初心者向け投資教育
  🔗 Instagram で毎日投稿 @mika_financial_analyst
  ```
- [ ] **アバター**: Instagram と同一（一貫性）
- [ ] **ヘッダー**: 金融チャートのビジュアル（1500x500px）

**成果物**: SNS アカウント 2 個（Instagram + X）設定完了

---

### M0-5: コンテンツカレンダー初期化
**期限**: Mar 16（水）
**担当**: Claude（テンプレート作成） → ユーザー（確認）

**Google Sheets** に以下を作成:

#### Sheet 1: `Content Calendar`
| Date | Character | Theme | Expression | Image Status | Caption Status | IG Status | X Status | Notes |
|------|-----------|-------|------------|--------------|----------------|-----------|---------|-------|
| 2026-03-17 | Mika | Weekly Forecast | Serious | Pending | Pending | Pending | Pending | - |
| 2026-03-18 | Mika | Individual Stock | Analytical | Pending | Pending | Pending | Pending | - |

**テンプレート**: SPEC.md Section 4-1 から自動インポート

#### Sheet 2: `LoRA Models`
| Character | Model ID | Status | Training Date | Accuracy | Notes |
|-----------|----------|--------|---------------|-----------| -----|
| Mika | lora_mika_v1 | Ready | 2026-03-15 | 98% | Basic model |

#### Sheet 3: `Analytics`
| Date | IG Followers | IG Likes | IG Comments | X Followers | X Likes | Engagement Rate |
|------|--------------|----------|-------------|-------------|---------|-----------------|

**成果物**: Google Sheets リンク + 初期データ入力完了

---

## Phase 1: アカウント構築 & 初期投稿 30 本（Week 2-3: Mar 17-30）

### M1-1: LoRA 学習実行 & モデルテスト
**期限**: Mar 17（木）
**担当**: Claude（実装と fal.ai API 実行）

- [ ] **データセット確認**: M0-2 で準備した 50-100 枚が `/data/training/` に揃っているか
- [ ] **fal.ai アカウント確認**: API キー正常性確認
- [ ] **LoRA 学習実行**:
  ```bash
  python src/train_lora.py \
    --character mika \
    --dataset_path data/training/mika_50 \
    --model_id lora_mika_v1 \
    --learning_rate 0.0002 \
    --iterations 800
  ```
- [ ] **学習時間**: 5-15 分（fal.ai クラウド実行）
- [ ] **コスト**: $0.50/実行 × 1 = $0.50
- [ ] **モデルID記録**: `lora_mika_v1` を `characters.py` に登録

- [ ] **テスト生成 10 枚**:
  ```bash
  python src/generate_image.py \
    --character mika \
    --lora_id lora_mika_v1 \
    --num_images 10 \
    --expressions "serious,friendly,analytical,surprised,relaxed"
  ```

- [ ] **一貫性評価**:
  - 視覚的に 5 枚を確認→顔・髪・肌が 95% 以上一致しているか確認
  - 問題あれば再学習（Learning Rate 調整）
- [ ] **InstantID 検討**: 一貫性が 95% 以下なら検討

**成果物**:
- `characters.py` に `lora_mika_v1` 登録
- `outputs/lora_test_samples/` に テスト画像 10 枚

---

### M1-2: 初期投稿 30 本生成（スプリント生成）
**期限**: Mar 19（土）
**担当**: Claude（自動生成スクリプト実行）

**目標**: 3 週分の投稿（月-日 × 3 週 = 21 本 + 予備 9 本 = 30 本）

```bash
# 自動生成スクリプト実行
python src/batch_generate.py \
  --character mika \
  --num_posts 30 \
  --start_date 2026-03-17 \
  --output_format both  # "image+caption"
```

**生成フロー**:
1. コンテンツカレンダーから 30 日分のテーマ・表情を取得
2. 各テーマ+表情の組み合わせで `generate_image.py` 実行
3. 各テーマに対して `generate_caption.py` 実行
4. `outputs/batch_30/` に ファイル命名規則で保存:
   ```
   outputs/batch_30/
   ├── 2026-03-17_mika_weekly_serious.jpg
   ├── 2026-03-17_mika_weekly_serious.txt (caption)
   ├── 2026-03-18_mika_individual_analytical.jpg
   ├── 2026-03-18_mika_individual_analytical.txt
   ... (30 pairs)
   ```

**コスト**:
- 画像生成: 30 × $0.08 = $2.40
- Groq API: 30 × (300 tokens) × $0.0005 = $4.50
- **合計**: $6.90

**QA チェック**:
- [ ] 30 枚すべてがダウンロード完了したか確認
- [ ] キャプション生成エラーがないか（JSON パース確認）
- [ ] ファイル命名規則が統一されているか

**成果物**: `outputs/batch_30/` に 60 ファイル（画像 30 + テキスト 30）

---

### M1-3: Instagram 初期投稿開始（1 週間 7 本）
**期限**: Mar 17（木）開始 → Mar 23（月）まで
**担当**: Claude（自動スケジュール投稿） / ユーザー（エンゲージメント監視）

**投稿スケジュール**:
```
2026-03-17 (Mon) 07:00 — Weekly Forecast （事前生成から 8h 後）
2026-03-18 (Tue) 07:00 — Individual Stock Analysis
2026-03-19 (Wed) 07:00 — Technical Analysis
2026-03-20 (Thu) 07:00 — Beginner Q&A
2026-03-21 (Fri) 07:00 — Weekly Summary
2026-03-22 (Sat) 07:00 — Macro Economics
2026-03-23 (Sun) 07:00 — Portfolio Building
```

**投稿実行**:
```bash
python src/daily_pipeline.py \
  --character mika \
  --platform instagram \
  --schedule_mode hourly  # 毎日 07:00 に投稿
```

**エンゲージメント監視**:
- [ ] 毎日 08:00 に `monitor_engagement.py` で前日投稿メトリクス取得
- [ ] フォロワー数増加率を追跡（目標: 初週 +50-100）
- [ ] コメント・いいね率が 1-2% 以上あるか確認
- [ ] トレンドハッシュタグ（#投資初心者向け）でのリーチ確認

**トラブルシューティング**:
- 投稿失敗時: API キー再確認 → Graph API 権限確認
- キャプション生成エラー: Groq API ステータス確認

**成果物**: Instagram 7 投稿完了 + Analytics シート更新

---

### M1-4: X（Twitter）投稿開始（1 週間 7 本、30 分遅延）
**期限**: Mar 17（木）開始 → Mar 23（月）まで
**担当**: Claude（自動スケジューリング）

**投稿スケジュール**:
```
Instagram 投稿 → 30 分後に X でも投稿（テキスト調整版）
```

**実装**:
```bash
python src/post_to_x.py \
  --image_url outputs/batch_30/2026-03-17_mika_weekly_serious.jpg \
  --caption_file outputs/batch_30/2026-03-17_mika_weekly_serious.txt \
  --delay_minutes 30
```

**キャプション調整**:
- Instagram: 150-300 字 + ハッシュタグ 10 個
- X: 280 字以内 + ハッシュタグ 3-4 個（キャラ限定あり）

**フォロワー数目標（Week 1 終了時）**:
- Instagram: 100-300 フォロワー（初期フォロー枠）
- X: 50-150 フォロワー

---

### M1-5: エンゲージメント最適化実験（Week 2-3）
**期限**: Mar 24（火） → Mar 30（月）
**担当**: Claude （A/B テスト実装） / ユーザー（結果確認）

**実験 1: 投稿時間最適化**
- 仮説: 朝 7 時よりも朝 8 時のほうがエンゲージメント率が高い
- テスト期間: Week 2 後半（3-4 投稿）
- 測定: 各投稿のいいね・コメント・シェア数を記録
- 判定基準: エンゲージメント率が +0.5% 以上なら採用

**実験 2: ハッシュタグ戦略**
- 仮説: トレンド + 弱いハッシュタグの組み合わせのほうがリーチが高い
- テスト:
  - Control：#投資初心者向け #株式相場 #相場見通し × 3
  - Test：#投資初心者向け + #テクニカル分析 + #Mika金融塾（弱いタグ）
- 測定: インプレッション数 / フォロワー新規クリック数
- 判定基準: Test グループのインプレッションが +20% 以上なら採用

**実験 3: キャプション長さ最適化**
- 仮説: 100-150 字（短い）のほうがコメント率が高い
- テスト期間: Week 3（2-3 投稿）
- 測定: コメント数 / コメント率
- 判定基準: コメント率が +1% 以上なら採用

**成果物**:
- `analytics/A_B_test_results.md` に実験結果まとめ
- 最適化された投稿テンプレート更新

---

### M1-6: 初期フォロワー 200+ 達成確認
**期限**: Mar 30（月）
**担当**: ユーザー（確認） / Claude（トラッキング）

**確認項目**:
- [ ] Instagram フォロワー: 200+ ✓
- [ ] X フォロワー: 100+ ✓
- [ ] Instagram エンゲージメント率: 1.5%+ ✓
- [ ] コメント数: 累積 50+件 ✓
- [ ] シェア数: 累積 20+件 ✓

**KPI トラッキング**:
| 項目 | 目標 | 実績 | 判定 |
|------|------|------|------|
| IG Followers | 200+ | ? | ? |
| IG Engagement Rate | 1.5%+ | ? | ? |
| X Followers | 100+ | ? | ? |
| Comments | 50+件 | ? | ? |

---

## Phase 2: 成長施策 & エンゲージメント最適化（Month 2-3: Apr 1-May 31）

### M2-1: クロスプロモーション開始
**期限**: Apr 1（火）
**担当**: Claude（YT連携実装） / ユーザー（既存チャネル確認）

**YouTube 統合（Mika 選択時）**:
- [ ] **既存チャネルの確認**: YouTube 金融チャネルが存在するか / 視聴者数
- [ ] **エンドスクリーン設定**: 各動画の最後 5 秒に Instagram アカウント表示
- [ ] **概要欄リンク**: 「Instagram @mika_financial_analyst で毎日投稿」
- [ ] **クロスリンク効果測定**:
  - YouTube → IG クリック数を Google Analytics で追跡
  - 目標: YouTube 月 100K 視聴 → IG 新規フォロワー +5K

**期待効果**: IG フォロワー +5,000 (1-2ヶ月)

### M2-2: 著名インフルエンサー・メディアとのコラボ
**期限**: Apr 15（火）
**担当**: Claude（リスト作成） / ユーザー（メール送付）

**対象 1: Fintech インフルエンサー**
- [ ] リスト作成: Instagram で「投資」「金融」で検索 → 1K-50K フォロワーのアカウント 10-20 個
- [ ] アプローチ: DM で「シャウトアウト交換」提案
- [ ] テンプレート:
  ```
  こんにちは！
  金融教育系 AI インフルエンサー「Mika」と言います。
  あなたの素晴らしい投資コンテンツのファンです。

  もし興味があれば、相互フォローとシャウトアウト交換をしませんか？
  - あなたのアカウント → Instagram ストーリーズで紹介
  - 私のアカウント → あなたのフォロワーに推奨

  いかがでしょうか？
  ```
- [ ] 期待: 成功率 30% → 5-6 件の相互シャウトアウト → IG フォロワー +500-1,000

**対象 2: 金融メディア・マネーフォワード等**
- [ ] リスト: 「マネーフォワード」「楽天証券」「SBI 証券」の公式 Instagram
- [ ] アプローチ: メール + DM で「Mika AI インフルエンサー紹介」
- [ ] 期待: PR / 提携記事 → フォロワー +1,000-2,000

**KPI**:
- [ ] コラボ件数: 5-10 件
- [ ] 獲得フォロワー: +1,500-3,000

---

### M2-3: ハッシュタグ戦略の最適化と自動化
**期限**: Apr 20（日）
**担当**: Claude（戦略実装）

**手法 1: ハッシュタグマッピング**
```python
# hashtags.py
HASHTAG_STRATEGY = {
    "mika": {
        "strong": ["#投資初心者向け", "#株式相場", "#相場見通し"],  # 1M+ posts
        "medium": ["#テクニカル分析", "#ファンダメンタルズ", "#ローソク足"],  # 100K-1M
        "weak": ["#Mika金融塾", "#Mika相場分析", "#金融アナリスト初心者"],  # <100K（コミュニティ作り）
    },
    "theme_mapping": {
        "weekly_forecast": ["#投資初心者向け", "#テクニカル分析", "#Mika相場予想"],
        "individual_stock": ["#銘柄分析", "#株価上昇", "#投資チャンス"],
        ...
    }
}
```

**手法 2: ハッシュタグ自動生成**
```bash
python src/generate_hashtags.py \
  --character mika \
  --theme weekly_forecast \
  --num_hashtags 10
# 出力: #投資初心者向け #テクニカル分析 #Mika相場予想 ... (10個)
```

**手法 3: コメント欄への弱いタグ配置**
- キャプション: 強い + 中程度タグ
- コメント 1 番目: 弱いタグ（リーチ稼ぎ）

---

### M2-4: ユーザー生成コンテンツ（UGC）キャンペーン
**期限**: May 1（水）
**担当**: Claude（キャンペーン実装） / ユーザー（景品準備）

**キャンペーン 1: フォロー+リツイート for Ebook**
```
投稿: 「Mika と一緒に投資を学ぼう！
初心者向け『株式投資 101ガイド』PDF を DM で進呈！

応募方法:
1️⃣ このアカウントをフォロー
2️⃣ この投稿をシェア
3️⃣ DM で「101」と送信

#Mika金融塾 #初心者向け」
```

**期待**:
- フォロワー +500-1,000
- メール リスト +200-300（DM で メールアドレス収集）

**キャンペーン 2: コメント参加キャンペーン**
```
投稿: 「この中で一番上昇しそな銘柄は？
コメント欄で予想してください！

正解者の中から抽選で 3 名に
『トレーディングボード』をプレゼント！」
```

**期待**: コメント率 +200%、エンゲージメント率 +2%

---

### M2-5: ストーリーズ・リール活用の本格化
**期限**: Apr 1（火）開始
**担当**: Claude （テンプレート作成） / ユーザー（日常記録）

**ストーリーズ（毎日 3 本）**:
```
07:00 — 「朝のトレンド速報」（15 秒）
       - 日経先物の上げ幅
       - ドル円相場
       - CTA: 本投稿をチェック

12:00 — 「昼間のニュース」（15 秒）
       - NY 円相場
       - 米株先物
       - CTA: ストーリーズで詳細

17:00 — 「夜間チャートチェック」（15 秒）
       - 本日の収まり
       - 来週の準備
       - CTA: フォロー継続を促す
```

**リール（週 2 本）**:
```
火曜日: 「ダブルトップ分析」（30 秒）
       - チャートの図解
       - パターン解説
       - トレード例

金曜日: 「初心者ミス 5 選」（30 秒）
       - よくある失敗
       - 改善法
       - コメント促進
```

**期待**: ストーリーズ +100-200K インプレッション/月、リール シェア +50-100/月

---

### M2-6: フォロワー 10K 達成確認
**期限**: May 31（金）
**担当**: ユーザー（確認）

**確認項目**:
- [ ] Instagram フォロワー: 10,000+ ✓
- [ ] X フォロワー: 5,000+ ✓
- [ ] Instagram エンゲージメント率: 2.5%+ ✓
- [ ] リール 再生数: 累積 100K+ ✓
- [ ] ストーリーズ 完了率: 50%+ ✓

---

## Phase 3: 収益化（Month 4+: Jun 1 以降）

### M3-1: Instagram スポンサー機能申請
**期限**: Jun 1（月）
**担当**: Claude （申請書作成） / ユーザー（申請）

**条件確認（Instagram Partner Program）**:
- [ ] フォロワー: 10,000+ ✓（M2-6 で達成）
- [ ] 月間 600,000 インプレッション以上
- [ ] 13 歳以上
- [ ] コミュニティガイドラインに準拠

**申請**:
- Instagram Creator Studio → 「収益化ツール」→「スポンサーになる」申請
- 承認待ちが 1-2 週間

**期待月収**: $600-1,000（600K インプレッション × $1.00-1.67/1000）

---

### M3-2: アフィリエイト提携開始
**期限**: Jun 15（火）
**担当**: Claude （テンプレート作成） / ユーザー（営業）

**対象企業 1: 証券会社**
- GMO 証券（口座開設: $100-200）
- 楽天証券（口座開設: $150-300）
- SBI 証券（口座開設: $100-200）

**営業テンプレート**:
```
件名: AI インフルエンサー「Mika」のアフィリエイト提携のご提案

本文:
いつもお世話になっております。
AI 金融アナリスト「Mika」を運営している[名前]です。

現在、Instagram および X で以下の実績があります:
- Instagram フォロワー: 15,000+
- 月間エンゲージメント: 20,000+ (いいね+コメント)
- 月間インプレッション: 1,000,000+

金融教育系コンテンツを毎日配信しており、投資初心者層（20-40 代）との親和性が高いです。

貴社の口座開設キャンペーンをアフィリエイト対象として、以下の形式でプロモーションさせていただきたいです:

- Instagram フィード投稿: 月 1-2 件
- ストーリーズ: 週 2-3 件
- コメント欄での紹介: 週 1-2 件

条件: 1 口座開設あたり $150 の報酬

ご検討のほど、よろしくお願いいたします。
```

**期待**:
- 提携成功: 2-3 社
- 月間口座開設: 20-30 件
- 月間報酬: $3,000-4,500（3 社 × 20 件 × $150）

---

### M3-3: スポンサードポスト営業開始
**期限**: Jul 1（日）
**担当**: Claude （営業リスト作成） / ユーザー（メール営業）

**営業対象**:
1. **フィンテック企業**: Revolut, Wise, Crypto.com（北米・EU ターゲット）
2. **投資教育プラットフォーム**: Skillshare, Udemy, Schoo
3. **金融メディア**: マネーフォワード、楽天証券、SBI 証券
4. **消費財（アフィリエイト性）**: Amazon、楽天（ステーショナリー etc）

**料金モデル** (フォロワー 20,000 時点):
- 基準: フォロワー × $1.50-3.00
- 例: 20,000 × $2.00 = $40,000/月相当（年間契約時）
- 実績: 月 1-2 件の小型案件から開始

**期待**:
- 月 1-2 件の案件
- 月間報酬: $2,000-5,000（スポンサー + アフィリエイト合計）

---

### M3-4: 有料コース・Patreon 立ち上げ
**期限**: Aug 1（水）
**担当**: Claude （コース設計） / ユーザー（教材作成）

**コース案**: 「Mika と学ぶ株式投資 101」

**プラットフォーム**: Patreon / Circle / Skillshare

**ティアリング**:
| ティア | 月額 | 特典 |
|--------|------|------|
| **Supporter** | $4.99 | 月 1 回の Live Q&A 参加権 |
| **Investor** | $9.99 | 月 2 回 Live + 週 1 回の限定投稿（テク分析深掘り） |
| **Analyst** | $19.99 | 月 4 回 Live + 週 2 回限定投稿 + 月 1 回の個別相談（30 分） |

**初期コンテンツ**:
- 投稿: 「初心者向けテクニカル分析講座」（10 動画 × 5-10 分）
- 資料: スプレッドシート「年間銘柄スクリーニング」
- テンプレート: 「投資ノート」テンプレート PDF

**期待**:
- 月 200-500 サブスク
- 月間報酬: $1,000-5,000

**立ち上げ KPI**:
- [ ] Patreon ページ作成 & デザイン完了
- [ ] 初期動画 5 本アップロード
- [ ] 初月サブスク: 100+

---

### M3-5: グッズ化・物販開始
**期限**: Sep 1（火）
**担当**: Claude （デザイン） / ユーザー（商品確認）

**プロダクト**:
1. **Tシャツ**: 「Mika 推し」ロゴ + QR コード（Instagram へ）
   - 単価: $15-20
   - マージン: $5-8/枚

2. **キャップ**: 「Mika Financial Analyst」刺繍
   - 単価: $18-25
   - マージン: $6-10/枚

3. **ステッカー**: 「テクニカル分析できる女」
   - 単価: $2-3
   - マージン: $1-1.5/枚

4. **ノート**: 「投資ノート」（リライティング）
   - 単価: $10-15
   - マージン: $3-5/枚

**流通**: Amazon Merch on Demand / Printful / Teespring（ドロップシッピング）

**期待**:
- 月間販売: 200-300 個
- 月間報酬: $1,500-3,000

---

### M3-6: Year 1 収益目標確認
**期限**: Dec 31（日）
**担当**: ユーザー（確認）

**目標値**:
| 収入源 | 月額（平均） | 年間 |
|--------|-------------|------|
| 広告（Instagram） | $600 | $7,200 |
| アフィリエイト（証券） | $3,000 | $36,000 |
| スポンサーシップ | $3,000 | $36,000 |
| Patreon | $2,000 | $24,000 |
| グッズ販売 | $2,000 | $24,000 |
| その他 | $500 | $6,000 |
| **TOTAL** | **$11,100** | **$133,200** |

**Year 1 フォロワー目標**: 50,000-100,000

---

## KPI モニタリング（全 Phase 共通）

### Daily Metrics（毎日 08:00 集計）
```
Google Sheets "Analytics" シートに自動記録:
- IG フォロワー数
- IG いいね数（前日投稿）
- IG コメント数
- IG シェア数
- IG 保存数
- X フォロワー数
- X いいね数
- X リツイート数
```

### Weekly Metrics（毎週日 18:00）
```
Google Sheets "Weekly Summary" シートに集計:
- IG 週間エンゲージメント率（いいね+コメント / フォロワー）
- X 週間エンゲージメント率
- IG フォロワー増加数
- X フォロワー増加数
- リール 平均再生数
- ストーリーズ 完了率
```

### Monthly Metrics（毎月 1 日 10:00）
```
Google Sheets "Monthly KPI" シートに記録:
- 月間インプレッション（IG + X）
- 月間エンゲージメント率平均
- 新規フォロワー（IG + X）
- 案件獲得数
- 案件報酬金額
- 運営コスト
- 月間収益
- ROI（収益 / コスト）
```

### Dashboard（可視化）
```
Google Data Studio で以下をダッシュボード化:
- フォロワー推移グラフ
- エンゲージメント率推移
- 投稿別パフォーマンスランキング
- 収益推移
- コスト vs 収益 グラフ
```

---

## 決定待ちアイテム

### ユーザー確認必須
1. **キャラクター選択**: Mika / Rena / Sora
   - [ ] 決定日: ___________
   - [ ] 決定キャラ: ___________

2. **撮影方式**:
   - [ ] セルフ撮影（コスト: $0、時間: 4-6h）
   - [ ] 外注撮影（コスト: $300-500、時間: 3-5日、品質: 高）

3. **プラットフォーム優先度**:
   - [ ] Instagram 優先（投稿品質重視）
   - [ ] X 優先（フォロワー増加重視）
   - [ ] 並行（両プラットフォーム）

4. **初期投資予算確保**:
   - [ ] 初期投資 $300-500（撮影 + LoRA 学習）
   - [ ] 月額運営 $227（ツール利用料）
   - [ ] Year 1 目標 $133,200 達成への承認

---

## 参考ファイル
- SPEC.md — 仕様書（全体設計）
- PLAN.md — プロジェクト概要
- `src/` — Python スクリプト（実装コード）
- `outputs/` — 生成物置き場
- `analytics/` — 分析レポート置き場

**次レビュー日**: 2026-03-17（Week 1 完了時）
