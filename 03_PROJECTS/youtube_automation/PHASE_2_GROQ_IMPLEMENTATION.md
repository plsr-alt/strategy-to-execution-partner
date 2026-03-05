# Phase 2: YouTube自動化パイプライン — Groq 実装指示書

**対象**: Groq（EC2上で実行）
**実装期間**: 2-3時間
**出力**: youtube_pipeline.py の 8ステップ実装コード

---

## 📋 実装タスク一覧

| Step | タスク | 役割 | 優先度 |
|------|--------|------|-------|
| 1 | 企画エンジン（トレンド分析） | Groq API | 🔴 必須 |
| 2 | 台本生成 | Groq Llama 3.1 | 🔴 必須 |
| 3 | 音声生成 | VOICEVOX API | 🟡 重要 |
| 4 | 映像素材収集 | Pexels API + matplotlib | 🟡 重要 |
| 5 | 動画編集 | video_auto_edit 呼び出し | 🔴 必須 |
| 6 | サムネイル生成 | PIL + テンプレ | 🟡 重要 |
| 7 | メタデータ最適化 | Groq SEO | 🟡 重要 |
| 8 | YouTube アップロード | YouTube Data API v3 | 🟡 後回し可 |

---

## 🎯 Step 1: 企画エンジン（トレンド分析）

### 仕様

```python
def generate_theme(theme_mode: str = "auto") -> dict:
    """
    Groq API を呼び出して、トレンドテーマを分析

    Args:
        theme_mode: "auto" | "finance" | "tech" | "business"

    Returns:
        {
            "theme": "AI で月5万円節約する方法",
            "keywords": ["AI", "節約", "家計管理"],
            "hook": "多くの人は家計管理に時間を使いすぎています",
            "duration_min": 8,
            "category": "finance"
        }
    """
```

### Groq プロンプト

```
あなたは YouTube ビデオエディターです。
今週のトレンドを分析して、日本のサラリーマン向けに
「{theme_mode}」ジャンルの動画ネタ1つを提案してください。

出力形式（JSON のみ）:
{
  "theme": "...",
  "keywords": [...],
  "hook": "...",
  "duration_min": 8,
  "audience": "日本のサラリーマン"
}
```

### 実装ポイント

- Groq API キーは環境変数から読み込み
- エラーハンドリング: API 失敗時はデフォルトテーマを返す
- JSON パース: Groq 応答から JSON のみ抽出

---

## 🎯 Step 2: 台本生成

### 仕様

```python
def generate_script(theme: dict, language: str = "ja") -> str:
    """
    Groq Llama 3.1 で YouTube 動画用の台本を生成

    構成:
      - フック（0-15秒）
      - 本題（15秒-6分）: 3-5ポイント
      - CTA（6-7分）

    Returns:
        台本テキスト（改行で区切られた形式）
    """
```

### Groq プロンプト

```
以下のテーマで、YouTube 動画用の台本を生成してください。

テーマ: {theme['theme']}
キーワード: {', '.join(theme['keywords'])}
尺: 8-12分
言語: {language}

出力形式:
[フック]
...

[本題]
ポイント1: ...
ポイント2: ...
ポイント3: ...

[CTA]
...
```

### 実装ポイント

- 台本はマークダウン形式で段落分け
- 各セクション（フック、本題、CTA）を明確に区切る
- 話者の間（ポーズ）を指定（例: 「...」で 500ms ポーズ）

---

## 🎯 Step 3: 音声生成

### 仕様

```python
def generate_voiceover(script: str, voicevox_url: str = "http://localhost:50021") -> str:
    """
    VOICEVOX API を呼び出して、日本語ナレーション音声を生成

    Args:
        script: 台本（改行で区切られた形式）
        voicevox_url: VOICEVOX サーバーURL

    Returns:
        音声ファイルパス（WAV形式）
        例: "/home/ec2-user/task/tmp/voiceover_20260305_060000.wav"

    仕様:
      - 話者: 初音ミク（ID: 0）or 好みの話者
      - 速度: 1.2x（少し早口で視聴者維持率向上）
      - ポーズ長: 各段落間に 500ms
    """
```

### 実装ポイント

- VOICEVOX API エンドポイント:
  ```
  POST http://localhost:50021/audio_query?text={text}&speaker={speaker_id}
  ```
- 台本を文単位で分割して API 呼び出し
- 音声クリップを連結（ffmpeg or pydub）
- タイムアウト: 30秒/文
- フォールバック: VOICEVOX 不可時は wav 生成スキップ

---

## 🎯 Step 4: 映像素材収集

### 仕様

```python
def collect_footage(keywords: list, num_clips: int = 5) -> list:
    """
    Pexels API で キーワード検索 → ビデオ DL

    Returns:
        [
            {"path": "素材/video_001.mp4", "duration": 10.5},
            {"path": "素材/slide_001.png", "duration": 3.0},
            ...
        ]
    """

def generate_infographics(theme: dict) -> list:
    """
    matplotlib + Pillow で図解スライドを自動生成

    例:
      - 「月5万円節約」の金額グラフ
      - 「3つのポイント」の箇条書きスライド
      - 比較表（手動 vs AI 自動化）

    Returns:
        [{"path": "素材/slide_001.png", "duration": 3.0}, ...]
    """
```

### 実装ポイント

- **Pexels API**:
  ```
  GET https://api.pexels.com/videos/search?query={query}&per_page=5
  ```
  ヘッダー: `Authorization: {PEXELS_API_KEY}`

- 取得した MP4 を `/home/ec2-user/task/tmp/` に DL

- **matplotlib での図解生成**:
  - 16:9 アスペクト比（1280x720）
  - フォント: Noto Sans JP（日本語対応）
  - カラー: モダンな配色（青系推奨）

- フォールバック: Pexels 見つからない場合 → 自動生成スライド

---

## 🎯 Step 5: 動画編集

### 仕様

```python
def edit_video(
    footage: list,
    voiceover_path: str,
    script: str,
    output_path: str,
) -> str:
    """
    素材 + 音声 + 字幕を組み合わせて最終動画を作成

    Steps:
      1. 素材を繋ぎ合わせる（moviepy）
      2. ナレーション音声を合成
      3. 字幕を生成（script から SRT を作成）
      4. video_auto_edit を subprocess 呼び出し

    Returns:
        output_path（最終動画）

    処理時間: 約 5-10分
    """
```

### 実装ポイント

- **moviepy で素材結合**:
  ```python
  from moviepy.editor import concatenate_videoclips, ImageClip, VideoFileClip
  clips = [VideoFileClip(f["path"]) for f in footage]
  final = concatenate_videoclips(clips)
  final = final.set_audio(AudioFileClip(voiceover_path))
  ```

- **SRT 字幕生成**:
  ```
  1
  00:00:00,000 --> 00:00:15,000
  「AI で月5万円節約？聞いたことありますか？」

  2
  00:00:15,000 --> 00:00:30,000
  「多くの人は家計管理に時間を使いすぎています。」
  ```

- **video_auto_edit 呼び出し**:
  ```python
  subprocess.run([
      "python",
      "/home/ec2-user/task/03_PROJECTS/video_auto_edit/main.py",
      "--input", temp_video,
      "--config", "config.yaml"
  ], check=True)
  ```

---

## 🎯 Step 6: サムネイル生成

### 仕様

```python
def generate_thumbnail(theme: dict, output_path: str) -> str:
    """
    PIL + テンプレを使用して YouTube サムネイルを生成

    Returns:
        thumbnail_path

    ガイドライン:
      - サイズ: 1280x720px
      - テキスト: 3-5 words（視認性重視）
      - コントラスト: 高め（モバイル表示対応）
    """
```

### 実装ポイント

- **テンプレ読み込み**:
  ```python
  template = Image.open("assets/thumbnail_template.png")
  # テンプレートは事前に用意（背景 + デザイン）
  ```

- **テキスト配置**:
  - フォント: Noto Sans JP Bold, サイズ 48
  - 色: 白文字 + 黒縁取り
  - 位置: 中央寄り下部

- **フォールバック**: テンプレなし時は、単純な背景 + テキスト

---

## 🎯 Step 7: メタデータ最適化

### 仕様

```python
def optimize_metadata(theme: dict, script: str) -> dict:
    """
    Groq で タイトル＆説明を最適化

    Returns:
        {
            "title": "AI で月5万円節約？最新手法3つ【2026年版】",
            "description": "...",
            "tags": [...],
            "category": "Education"
        }

    SEO チェックリスト:
      ✓ タイトルに主キーワード（最初の 5単語内）
      ✓ 説明に 2次キーワード＋リンク
      ✓ タグ: 大分類 3 + 中分類 5 + 小分類 7
    """
```

### Groq プロンプト

```
以下の動画について、YouTube SEO 最適化済みのメタデータを生成してください。

テーマ: {theme['theme']}
ターゲット: 日本のサラリーマン

以下の形式で JSON のみ出力:
{
  "title": "...",  # 50文字以内、キーワード含有
  "description": "...",  # 500文字以内
  "tags": [...],  # 15個以下
  "category": "Education"
}
```

### 実装ポイント

- タイトル: 50文字以内、クリックしたくなる文言
- 説明: 動画リンク＆関連動画リンク含める
- タグ: キーワード、関連ワード、ロングテール

---

## 🎯 Step 8: YouTube アップロード

### 仕様

```python
def upload_to_youtube(
    video_path: str,
    metadata: dict,
    thumbnail_path: str,
    publish_mode: str = "SCHEDULE",
) -> str:
    """
    YouTube Data API v3 で 動画を投稿

    Steps:
      1. OAuth 認証（.env の YOUTUBE_CLIENT_ID/SECRET）
      2. 動画アップロード（resumable upload）
      3. サムネイル設定
      4. メタデータ設定
      5. 公開設定（予約公開 or 非公開）

    Returns:
        video_id

    publish_mode:
      - "SCHEDULE": 翌日朝 6:00 に予約公開（デフォルト）
      - "PRIVATE": 非公開で保存
      - "PUBLIC": 即座に公開

    処理時間: 約 5-10分（動画サイズに依存）
    """
```

### 実装ポイント

- **OAuth フロー**:
  ```python
  from google_auth_oauthlib.flow import InstalledAppFlow
  flow = InstalledAppFlow.from_client_config(...)
  credentials = flow.run_local_server()
  ```

- **Resumable Upload**:
  ```python
  youtube.videos().insert(
      part="snippet,status",
      body={...},
      media_body=MediaFileUpload(video_path, resumable=True)
  )
  ```

- **スケジュール公開** (publish_mode="SCHEDULE"):
  ```python
  status = {
      "privacyStatus": "scheduled",
      "publishAt": "2026-03-06T06:00:00Z"
  }
  ```

---

## 🔄 エラーハンドリング & ログ

### 各ステップでのエラー耐性

```python
def run_pipeline(config: dict) -> dict:
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
        # 次へ進む or 中止判定
        if should_stop_on_error(step_name):
            return edit_log

    # ... 以降も同様に try-except でラップ
```

### ログ出力形式

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
    "video": "/home/ec2-user/task/out/final_20260305_060000.mp4",
    "thumbnail": "/home/ec2-user/task/out/thumbnail_20260305_060000.png",
    "metadata": "/home/ec2-user/task/out/metadata_20260305_060000.json"
  }
}
```

---

## 📝 実装の注意点

### 1. パス互換性
```python
import platform

if platform.system() == "Windows":
    OUTPUT_DIR = "C:\\..."
else:  # Linux
    OUTPUT_DIR = "/home/ec2-user/task/..."
```

### 2. API キー管理
```python
from dotenv import load_dotenv
import os

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
```

### 3. タイムアウト設定
```python
# 各 API 呼び出しにタイムアウトを設定
requests.get(url, timeout=30)
```

### 4. 再開可能性
```python
# 途中で失敗しても、既存ファイルを再利用
if os.path.exists("voiceover.wav"):
    voiceover_path = "voiceover.wav"
else:
    voiceover_path = generate_voiceover(script)
```

---

## ✅ テストケース（Phase 2 完成時）

```bash
# 1. 手動実行テスト
cd /home/ec2-user/task/03_PROJECTS/youtube_automation
python3 youtube_pipeline.py --theme finance --output ./out

# 2. 出力確認
ls -lh ./out/
# → final_*.mp4 / metadata_*.json / edit_log_*.json が生成されるか

# 3. ログ確認
cat ./out/edit_log_*.json | python3 -m json.tool
```

---

## 📚 参考資料

- **Groq API**: https://console.groq.com
- **VOICEVOX**: https://voicevox.ru/ (API docs)
- **Pexels API**: https://www.pexels.com/api/
- **YouTube Data API v3**: https://developers.google.com/youtube/v3/docs
- **moviepy**: https://zulko.github.io/moviepy/
- **Pillow**: https://pillow.readthedocs.io/

---

## 🎯 まとめ

**Groq に実装を依頼する 8ステップ**：

1. ✅ Step 1-2: Groq API で企画＆台本生成
2. ⚠️ Step 3: VOICEVOX API で音声生成
3. ⚠️ Step 4: Pexels + matplotlib で素材収集
4. ⚠️ Step 5: moviepy + video_auto_edit で動画編集
5. ⚠️ Step 6: PIL で サムネイル生成
6. ✅ Step 7: Groq で メタデータ最適化
7. ⚠️ Step 8: YouTube API で アップロード

**優先実装順**: Step 1 → 2 → 7 → 3 → 4 → 5 → 6 → 8

---

**準備完了。EC2上で実装開始できます！！** 🚀
