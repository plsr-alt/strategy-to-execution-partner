# YouTube自動化パイプライン — 実装指示書（Groq/Claude向け）

## 概要

**入力**: なし（完全自動化）
**出力**:
- `./out/final_<YYYYMMDD_HHMMSS>.mp4` — 編集済み動画（字幕焼き込み）
- `./out/metadata_<YYYYMMDD_HHMMSS>.json` — YouTube メタデータ（タイトル・説明・タグ）
- `./out/edit_log_<YYYYMMDD_HHMMSS>.json` — 処理ログ

**処理時間**: 約 15-25分/動画（EC2 t3.medium）

---

## パイプラインのフロー

```
Step 1: 企画エンジン
  ↓ トレンド分析 → テーマ決定 → キーワード抽出
Step 2: 台本生成
  ↓ Groq が台本を作成
Step 3: 音声生成
  ↓ VOICEVOX で 日本語ナレーション
Step 4: 映像素材収集
  ↓ Pexels API + matplotlib 図解
Step 5: 動画編集
  ↓ video_auto_edit パイプライン（無音カット→テンポ調整→字幕）
Step 6: サムネイル生成
  ↓ PIL + テンプレ
Step 7: メタデータ最適化
  ↓ Claude/Groq で SEO タイトル＆説明生成
Step 8: YouTube アップロード
  ↓ YouTube Data API v3 で投稿
```

---

## 詳細実装仕様

### Step 1: 企画エンジン

**役割**: トレンドテーマを分析し、YouTube動画ネタを決定する

**実装**:
```python
def generate_theme(theme_mode: str = "auto") -> dict:
    """
    theme_mode:
      - "auto": Groq が「今週のトレンドテーマ」を分析
      - "finance": 金融・投資・節約
      - "tech": テック・AI
      - "business": ビジネス・自己啓発

    Returns:
      {
        "theme": "AI で月5万円節約する方法",
        "keywords": ["AI", "節約", "家計管理"],
        "hook": "多くの人は...",
        "category": "finance"
      }
    """
```

**Groq プロンプト例**:
```
あなたは YouTube ビデオエディターです。今週のトレンドを分析して、
日本のサラリーマン向けに「金融・テック・ビジネス」ジャンルの
動画ネタ1つを提案してください。

出力形式:
{
  "theme": "...",
  "keywords": [...],
  "hook": "...",
  "duration_min": 8,
  "audience": "日本のサラリーマン"
}
```

### Step 2: 台本生成

**役割**: 企画テーマから YouTube 動画用の台本を生成

**構成**:
- **フック**（0-15秒）: 視聴者の関心を引く
- **本題**（15秒-6分）: メインコンテンツ（3-5ポイント）
- **CTA**（6-7分）: 行動喚起（チャンネル登録、コメント等）

**実装**:
```python
def generate_script(theme: dict, language: str = "ja") -> str:
    """
    Groq Llama 3.1 で台本生成

    プロンプト:
      テーマ: {theme}
      言語: {language}
      動画尺: 8-12分

      == 出力形式 ==
      [フック]
      ...
      [本題]
      ...
      [CTA]

    Returns:
      台本テキスト（改行で区切られた形式）
    """
```

**台本フォーマット**:
```
[フック]
「AI で月5万円節約？聞いたことありますか？」
「多くの人は家計管理に時間を使いすぎています。」
「でも、あるツールを使えば、わずか5分で月5万円節約できるんです。」

[本題]
「ポイント1: 自動振り分け」
「AI が支出を分析して、自動で貯蓄に回します。」

「ポイント2: 手数料0円」
「完全無料。隠れコストはありません。」

...

[CTA]
「この方法で月5万円節約する人、続出中です。」
「チャンネル登録してみてください。」
```

### Step 3: 音声生成

**役割**: 台本を日本語ナレーション音声に変換

**実装**:
```python
def generate_voiceover(script: str, voicevox_url: str = "http://localhost:50021") -> str:
    """
    VOICEVOX API を呼び出して音声生成

    Args:
      script: 台本（改行で区切られた形式）
      voicevox_url: VOICEVOX サーバーURL

    Returns:
      音声ファイルパス（WAV形式）

    仕様:
      - 話者: 初音ミク（ID: 0）or 好みの話者
      - 速度: 1.2x（少し早口で視聴者維持率向上）
      - ポーズ長: 各段落間に 500ms
    """
```

**API 呼び出し例**:
```bash
curl -X POST "http://localhost:50021/audio_query?text=AI%E3%81%A7%E8%8A%82%E7%B4%84&speaker=0"
```

### Step 4: 映像素材収集

**役割**: Pexels API + matplotlib で 動画素材を取得/生成

**実装**:
```python
def collect_footage(keywords: list, num_clips: int = 5) -> list:
    """
    Pexels API で キーワード検索 → ビデオ DL

    Args:
      keywords: 検索キーワード（例: ["AI", "節約"]）
      num_clips: 取得するビデオ数

    Returns:
      [
        {"path": "素材/video_001.mp4", "duration": 10.5},
        ...
      ]

    フォールバック:
      - Pexels で見つからない場合 → matplotlib で図解スライドを自動生成
    """

def generate_infographics(theme: dict) -> list:
    """
    matplotlib + Pillow で図解スライドを自動生成

    例:
      - 「月5万円節約」の金額グラフ
      - 「3つのポイント」の箇条書きスライド
      - 比較表（手動 vs AI 自動化）

    Returns:
      [
        {"path": "素材/slide_001.png", "duration": 3.0},
        ...
      ]
    """
```

### Step 5: 動画編集

**役割**: 素材 + 音声 + 字幕を組み合わせて最終動画を作成

**実装**:
```python
def edit_video(
    footage: list,
    voiceover_path: str,
    script: str,
    output_path: str,
) -> str:
    """
    video_auto_edit/main.py を subprocess で呼び出し

    Steps:
      1. 素材を繋ぎ合わせる（moviepy）
      2. ナレーション音声を合成
      3. 字幕を生成（script から SRT を作成）
      4. video_auto_edit で無音カット→テンポ調整→字幕焼き込み

    Returns:
      output_path（最終動画）

    処理時間: 約 5-10分
    """

    # subprocess で video_auto_edit を呼び出し
    cmd = [
        "python",
        "/home/ubuntu/task/03_PROJECTS/video_auto_edit/main.py",
        "--input", temp_video,
        "--config", "config.yaml"
    ]
    subprocess.run(cmd, check=True)
```

### Step 6: サムネイル生成

**役割**: YouTube サムネイル画像を自動生成

**実装**:
```python
def generate_thumbnail(theme: dict, output_path: str) -> str:
    """
    PIL + テンプレを使用

    Steps:
      1. テンプレ画像を読み込む（assets/thumbnail_template.png）
      2. テーマに関連するテキストを配置
      3. フォント: Noto Sans JP Bold, サイズ 48
      4. 色: 白文字 + 黒縁取り
      5. PNG で保存

    Returns:
      thumbnail_path

    サムネイルガイドライン:
      - サイズ: 1280x720px
      - テキスト: 3-5 words（視認性重視）
      - コントラスト: 高め（モバイル表示対応）
    """
```

### Step 7: メタデータ最適化

**役割**: YouTube SEO を意識した タイトル・説明・タグを生成

**実装**:
```python
def optimize_metadata(theme: dict, script: str) -> dict:
    """
    Claude/Groq で タイトル＆説明を最適化

    Groq プロンプト:
      テーマ: {theme}
      ターゲット: 日本のサラリーマン

      以下の形式で、YouTube 最適化済みのメタデータを生成してください:
      {
        "title": "...",  # 50文字以内、キーワード含有
        "description": "...",  # 500文字以内
        "tags": [...],  # 15個以下
        "category": "Education"
      }

    Returns:
      metadata dict

    SEO チェックリスト:
      ✓ タイトルに主キーワード（最初の 5単語内）
      ✓ 説明に 2次キーワード＋リンク
      ✓ タグ: 大分類 3 + 中分類 5 + 小分類 7
    """
```

### Step 8: YouTube アップロード

**役割**: YouTube Data API v3 で 動画を投稿

**実装**:
```python
def upload_to_youtube(
    video_path: str,
    metadata: dict,
    thumbnail_path: str,
    publish_mode: str = "SCHEDULE",  # SCHEDULE / PRIVATE / PUBLIC
) -> str:
    """
    YouTube Data API v3 で投稿

    Steps:
      1. OAuth 認証（.env の YOUTUBE_CLIENT_ID/SECRET）
      2. 動画アップロード（resumable upload）
      3. サムネイル設定
      4. メタデータ設定（タイトル・説明・タグ・カテゴリ）
      5. 公開設定（予約公開 or 非公開）

    Returns:
      video_id

    publish_mode:
      - "SCHEDULE": 翌日朝 6:00 に予約公開（デフォルト）
      - "PRIVATE": 非公開で保存（手動投稿向け）
      - "PUBLIC": 即座に公開（テスト時のみ）

    処理時間: 約 5-10分（動画サイズに依存）
    """
```

---

## エラーハンドリング & ログ

### 各ステップでのエラー耐性

```python
def run_pipeline(config: dict) -> dict:
    """
    メインパイプライン

    各ステップで try-except を実装
    失敗時も次へ進む（スキップ）
    """

    edit_log = {
        "timestamp": datetime.now().isoformat(),
        "steps": []
    }

    try:
        # Step 1
        edit_log["steps"].append({
            "step": "theme_generation",
            "status": "running"
        })
        theme = generate_theme()
        edit_log["steps"][-1]["status"] = "success"

    except Exception as e:
        edit_log["steps"][-1]["status"] = "failed"
        edit_log["steps"][-1]["error"] = str(e)
        # 次へ進む
        return edit_log

    # ... 以降も同様に try-except でラップ
```

### ログ出力

```json
{
  "timestamp": "2026-03-05T06:00:00",
  "theme": "AI で月5万円節約",
  "steps": [
    {
      "step": "theme_generation",
      "status": "success",
      "duration_sec": 2.5
    },
    {
      "step": "script_generation",
      "status": "success",
      "duration_sec": 15.3,
      "script_length": 1250
    },
    ...
  ],
  "total_duration_sec": 480,
  "output": {
    "video": "./out/final_20260305_060000.mp4",
    "thumbnail": "./out/thumbnail_20260305_060000.png",
    "metadata": "./out/metadata_20260305_060000.json"
  }
}
```

---

## 実装のコツ・注意点

### 1. パス互換性
```python
import platform

if platform.system() == "Windows":
    OUTPUT_DIR = "C:\\..."
else:  # Linux / Darwin
    OUTPUT_DIR = "/home/ubuntu/task/..."
```

### 2. API キーの安全管理
```python
from dotenv import load_dotenv
import os

load_dotenv(".env")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
```

### 3. タイムアウト設定
```python
# 各 API 呼び出しに タイムアウトを設定（Pexels等）
requests.get(url, timeout=30)
```

### 4. 再開可能性
```python
# 途中で失敗しても、既存ファイルを再利用できるよう
if os.path.exists("voiceover.wav"):
    # スキップ
    voiceover_path = "voiceover.wav"
else:
    voiceover_path = generate_voiceover(script)
```

---

## テストケース（Phase 2 完成時）

```bash
# 1. 手動実行テスト
python youtube_pipeline.py --theme "finance" --output ./test_out

# 2. 出力確認
ls -lh ./test_out/
# → final_*.mp4 / metadata_*.json / edit_log_*.json が生成されるか

# 3. 動画再生確認
ffplay ./test_out/final_*.mp4

# 4. メタデータ確認
cat ./test_out/metadata_*.json | jq .

# 5. EC2 Cron テスト
# .env を設定 → wait 6:00 → ログ確認
tail -f /home/ubuntu/task/youtube_pipeline_cron.log
```

---

## 参考資料

- **Groq API**: https://console.groq.com
- **VOICEVOX**: https://voicevox.ru/ (API docs)
- **Pexels API**: https://www.pexels.com/api/
- **YouTube Data API v3**: https://developers.google.com/youtube/v3/docs
- **video_auto_edit**: `../video_auto_edit/README.md`

---

## 次のステップ

1. ✅ Phase 1 ファイル作成（完了）
2. 🔄 **Phase 2: youtube_pipeline.py 実装** ← Groq に委譲
3. 🔄 **Phase 3: EC2 デプロイ＆テスト**
4. 🚀 **本番自動化スタート**
