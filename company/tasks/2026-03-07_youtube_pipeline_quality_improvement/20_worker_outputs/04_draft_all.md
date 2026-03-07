# 全成果物ドラフト — YouTube自動化パイプライン全面品質改善

> 作成日: 2026-03-07
> ステータス: ドラフト（レビュー前）

---

# 成果物1：競合分析レポート

## エグゼクティブサマリー

現状パイプラインは「gTTSの平坦な音声」「風景動画のみの映像」「機能しないサムネイル」「デフォルトブランディング」という4つの致命的課題を抱え、100K再生以上の競合チャンネルとは大きな品質差がある。

トップ10チャンネル（両学長289万人〜投資家バク10万人）の分析結果、成功の共通因子は以下5つ:
1. **オリジナルキャラクター＋ビジュアルアイデンティティ**（両学長のライオン、BANK ACADEMYの手書きイラスト）
2. **テロップ＋図解による「見える化」**（ゴシック体50pt、1秒4文字）
3. **自然な音声 or 個性的な合成音声**（gTTS以上の品質が必須）
4. **20分前後の標準尺＋詳細チャプター**
5. **統一カラースキーム＋ロゴ**

改善による期待効果: CTR 2.5%→4.0%+、視聴維持率 25%→35-40%、月間再生数 2,000→6,000-10,000回

## チャンネル横比較表

| チャンネル名 | 登録者 | 音声タイプ | 映像パターン | サムネイル配色 | 動画尺 | ブランディング |
|------------|--------|----------|------------|------------|--------|------------|
| 両学長 リベラルアーツ大学 | 289-382万 | 肉声+自然な抑揚 | アニメ+ライオンキャラ | 黄+白テキスト | 12-15分 | ライオンキャラ統一 |
| 中田敦彦 YouTube大学 | 550万+ | 肉声+テンポ速い | グリーンバック+ホワイトボード | 赤+黄テキスト | 15-25分 | 顔出し+ロゴ |
| BANK ACADEMY | 82万 | 聞き流し安定口調 | 手書きイラスト解説 | 青+白テキスト | 10-15分 | 手書き風統一 |
| バフェット太郎 | 49-50万 | 落ち着いた専門家口調 | チャート+データ分析 | 黒+黄テキスト | 10-20分 | シンプルロゴ |
| 投資家ぽんちよ | 49万 | 肉声+若者向け | アニメーション | 黄+オレンジ | 10-15分 | アニメキャラ |
| 松井証券×マヂラブ | 33.7万 | 芸人トーク+ナレ | 実写スタジオ | 赤+白+企業色 | 15-25分 | 企業+タレント |
| 投資家バク | 10万 | 落ち着いた口調 | チャート解説 | シンプル | 10-20分 | テキスト系 |
| ゆっくり解説系 | 数千〜数万 | 合成音声(VOICEVOX系) | スライドショー+テキスト | 黄+赤テキスト | 8-15分 | キャラクター |

## 音声パターン分析

成功パターン5つの中で、**パイプライン（自動生成）に最も適しているのはパターン5「合成音声個性化」**（ゆっくり解説型）。

| パターン | 代表 | gTTSとの差 | パイプライン適用可能性 |
|---------|------|----------|------------------|
| 肉声+自然な抑揚 | 両学長 | 大 | ✗（自動化不可） |
| 聞き流し安定口調 | BANK ACADEMY | 大 | ✗（自動化不可） |
| 落ち着き専門家口調 | バフェット太郎 | 大 | ✗（自動化不可） |
| 芸人トーク混合 | 松井証券 | 大 | ✗（自動化不可） |
| **合成音声個性化** | **ゆっくり解説** | **中** | **◎（VOICEVOX導入で実現可能）** |

**現状gTTSの問題**: 速度が一定で遅い、抑揚ゼロ、間がない、Google TTS特有の平坦さ
**改善方向**: VOICEVOX導入（速度1.2x、ポーズ自動挿入、キャラクター音声で個性化）

## 映像構成分析

現状は**Pexelsの風景動画をループ再生**しているだけ。競合は全て**テロップ＋図解＋キャラクター**で情報を「見える化」。

**競合の映像密度**: テロップは3-5秒ごとに更新、図解は2-3分ごとに挿入、キャラクターが常時画面に存在
**当チャンネルの映像密度**: テロップなし、図解はinfographic fallbackのみ、キャラクターなし

改善の優先度:
1. テロップ自動生成（台本と同期）— moviepy + PIL
2. インフォグラフィック図解の強化 — matplotlib + PIL
3. 背景を単色＋グラデーションに変更（風景動画廃止）

## サムネイルデザイン分析

成功サムネイルの共通ルール:
- **文字数**: 8-10文字（最頻値）
- **フォント**: 太ゴシック体 120px以上（スマホ視認性）
- **配色**: 黄色(#FFCC00)+黒背景 or オレンジ(#FF9900)+黒背景
- **レイアウト**: 左テキスト60%＋右画像/キャラ40%
- **縁取り**: 黒縁取り3-5px（白文字の場合）

現状PILサムネの問題: フォントサイズが小さい(72pt)、文字折り返しが機械的、キャラクターなし、テンプレバリエーションなし

## 動画尺・構成分析

| 項目 | 現状 | 競合平均 | 改善目標 |
|-----|------|---------|---------|
| 動画尺 | 8-15分（バラバラ） | 10-20分 | **20-25分（固定）** |
| 導入 | 比率不明 | 10-15% | 3-5分 |
| 本題 | 比率不明 | 70-80% | 12-16分 |
| まとめ | 比率不明 | 10-15% | 2-4分 |
| チャプター | なし | 5-8個 | 5-8個 |
| 広告枠 | 1-2枠 | 2-3枠 | **3枠（20分超で可能）** |

## 改善優先度マップ

| 優先度 | 項目 | 難易度 | インパクト | 実装期間 |
|--------|------|--------|----------|---------|
| **1** | 音声: VOICEVOX導入 | 低 | 高 | 1-2日 |
| **1** | 映像: テロップ自動生成 | 低-中 | 高 | 2-3日 |
| **2** | 尺: 20分以上統一 | 低 | 高 | 1日 |
| **2** | サムネイル: PIL大幅改修 | 中 | 高 | 1-2日 |
| **3** | ブランディング: チャンネル名・アイコン | 中 | 中 | 外部作業 |

---

# 成果物2：youtube_pipeline.py 改善仕様書

## フィードバック対応表

| FB# | フィードバック | 対応関数 | 行番号 | 改善内容 |
|-----|------------|---------|--------|---------|
| 1 | 音声が遅い・AI臭い | `generate_voiceover()` | 311-343 | VOICEVOX優先 + gTTS速度調整フォールバック |
| 2 | 映像が内容とマッチしない | `collect_footage()`, `edit_video()` | 350-554 | テロップ自動合成 + 図解強化 + 風景ループ廃止 |
| 3 | 動画尺20分以上統一 | `generate_theme()`, `generate_script()`, `.env` | 46-48, 122-310 | MIN=20, MAX=25 + スクリプト5セクション化 |
| 4 | サムネイルが機能しない | `generate_thumbnail()` | 589-686 | 配色・フォントサイズ・レイアウト全面改修 |
| 5 | アイコン初期値 | パイプライン外 | — | Canva/Figmaで手動作成（提案は成果物3） |
| 6 | チャンネル名デフォルト | パイプライン外 | — | 名前候補提案（成果物3） |

## 改善1: 音声（FB1対応）— `generate_voiceover()` L311-343

### 方針
VOICEVOX HTTP API を第一候補、gTTS を速度調整付きフォールバックとする。

### 変更内容

```python
# === 変更前 (L311-343) ===
def generate_voiceover(script: str, speaker_id: int = 3) -> str:
    """gTTS（Google Text-to-Speech）で日本語音声を生成"""
    from gtts import gTTS
    # ... gTTS のみ使用

# === 変更後 ===
def generate_voiceover(script: str, speaker_id: int = 3) -> str:
    """音声生成: VOICEVOX優先 → gTTS(速度調整)フォールバック"""
    lines = [l.strip() for l in script.split('\n')
             if l.strip() and not l.startswith('[') and len(l.strip()) > 2]
    if not lines:
        logger.warning("⚠️ 台本に有効な行がありません")
        return ""

    # VOICEVOX を試行
    voiceover = _try_voicevox(lines, speaker_id)
    if voiceover:
        return voiceover

    # gTTS フォールバック（速度調整付き）
    return _try_gtts_fast(lines)


def _try_voicevox(lines: list, speaker_id: int = 3) -> str:
    """VOICEVOX HTTP API で音声生成（自然なポーズ付き）"""
    try:
        # VOICEVOX接続テスト
        resp = requests.get(f"{VOICEVOX_URL}/speakers", timeout=5)
        resp.raise_for_status()
    except Exception:
        logger.info("   ℹ️ VOICEVOX未接続 → gTTSフォールバック")
        return ""

    from pydub import AudioSegment

    combined = AudioSegment.empty()
    pause_short = AudioSegment.silent(duration=300)   # 文中ポーズ 300ms
    pause_long = AudioSegment.silent(duration=800)    # 段落間ポーズ 800ms

    speed_scale = 1.2  # 1.2x で自然な速度感

    for i, line in enumerate(lines):
        try:
            # 音声合成クエリ生成
            query_resp = requests.post(
                f"{VOICEVOX_URL}/audio_query",
                params={"text": line, "speaker": speaker_id},
                timeout=30
            )
            query_data = query_resp.json()
            query_data["speedScale"] = speed_scale
            query_data["volumeScale"] = 1.5
            query_data["pitchScale"] = 0.0
            query_data["intonationScale"] = 1.2  # 抑揚を強調

            # 音声合成
            audio_resp = requests.post(
                f"{VOICEVOX_URL}/synthesis",
                params={"speaker": speaker_id},
                json=query_data,
                timeout=60
            )
            # WAV → pydub AudioSegment
            seg = AudioSegment.from_wav(io.BytesIO(audio_resp.content))
            combined += seg

            # ポーズ挿入（段落末は長め）
            if line.endswith("。") or line.endswith("？"):
                combined += pause_long
            else:
                combined += pause_short

        except Exception as e:
            logger.warning(f"⚠️ VOICEVOX行{i}失敗: {e}")
            continue

    if len(combined) < 1000:
        return ""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = TEMP_DIR / f"voiceover_{timestamp}.mp3"
    combined.export(str(output_path), format="mp3", bitrate="128k")
    logger.info(f"✅ VOICEVOX音声生成完了: {output_path} ({len(combined)/1000:.1f}秒)")
    return str(output_path)


def _try_gtts_fast(lines: list) -> str:
    """gTTS フォールバック（速度調整 + ポーズ挿入）"""
    try:
        from gtts import gTTS
        from pydub import AudioSegment
    except ImportError:
        logger.warning("⚠️ gTTS/pydub が未インストール")
        return ""

    try:
        full_text = "。\n".join(lines)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        raw_path = TEMP_DIR / f"voiceover_raw_{timestamp}.mp3"

        tts = gTTS(text=full_text, lang='ja', slow=False)
        tts.save(str(raw_path))

        # 速度1.25x に調整（pydub speedup）
        audio = AudioSegment.from_mp3(str(raw_path))
        faster = audio.speedup(playback_speed=1.25)

        output_path = TEMP_DIR / f"voiceover_{timestamp}.mp3"
        faster.export(str(output_path), format="mp3", bitrate="128k")
        logger.info(f"✅ gTTS音声生成完了(1.25x): {output_path}")
        return str(output_path)

    except Exception as e:
        logger.warning(f"⚠️ gTTS処理エラー: {e}")
        return ""
```

### 技術制約確認
- VOICEVOX: Docker起動が必要（EC2にまだ未セットアップ → Phase 2で導入）
- gTTS速度調整: pydubのspeedup()で即実装可能
- メモリ: 20分音声 ≈ 30MB（4GB RAM内で十分）

## 改善2: 映像（FB2対応）— `edit_video()` L475-554

### 方針
風景動画のループ再生を廃止。**テロップ付き単色背景＋図解スライド**で構成。

### 変更内容

```python
# === edit_video() の主要変更 ===

def edit_video(footage: list, voiceover_path: str, script: str,
               output_path: str, timestamp: str) -> str:
    """moviepy で素材を結合 — テロップ自動合成版"""
    from moviepy.editor import (
        VideoFileClip, ImageClip, AudioFileClip, TextClip,
        concatenate_videoclips, CompositeVideoClip, ColorClip
    )

    # 音声尺を基準にする（音声がない場合は VIDEO_DURATION_MIN * 60）
    if voiceover_path and Path(voiceover_path).exists():
        audio = AudioFileClip(voiceover_path)
        target_duration = max(audio.duration, 60 * VIDEO_DURATION_MIN)
    else:
        audio = None
        target_duration = 60 * VIDEO_DURATION_MIN

    # 台本をセンテンスに分割
    sentences = [l.strip() for l in script.split('\n')
                 if l.strip() and not l.startswith('[') and len(l.strip()) > 2]

    # 各センテンスの表示時間を算出
    sentence_duration = target_duration / max(len(sentences), 1)

    clips = []
    for i, sentence in enumerate(sentences):
        # 背景: 濃いグレーのグラデーション風単色
        bg = ColorClip(size=(1280, 720), color=(25, 25, 35), duration=sentence_duration)

        # テロップ: 画面下部にゴシック体テキスト
        try:
            txt = TextClip(
                sentence[:40],  # 最大40文字
                fontsize=42,
                font="Noto-Sans-CJK-JP-Bold",
                color='white',
                stroke_color='black',
                stroke_width=2,
                size=(1200, None),
                method='caption'
            ).set_duration(sentence_duration).set_position(('center', 520))

            clip = CompositeVideoClip([bg, txt])
        except Exception:
            clip = bg

        clips.append(clip)

    # 図解スライドを3-5枚挿入（infographics）
    infographic_clips = generate_infographics_enhanced(theme_data, len(sentences))
    # 均等に挿入
    insert_interval = max(len(clips) // (len(infographic_clips) + 1), 1)
    for idx, info_clip in enumerate(infographic_clips):
        pos = min((idx + 1) * insert_interval, len(clips))
        clips.insert(pos, info_clip)

    video = concatenate_videoclips(clips, method="compose")
    video = video.subclip(0, min(target_duration, video.duration))

    if audio:
        if audio.duration > video.duration:
            audio = audio.subclip(0, video.duration)
        video = video.set_audio(audio)

    # 出力
    video.write_videofile(output_path, fps=30, codec='libx264',
                          audio_codec='aac', logger=None)
    return output_path
```

### 新関数: `generate_infographics_enhanced()`

```python
def generate_infographics_enhanced(theme: dict, total_sentences: int) -> list:
    """強化版インフォグラフィック — ポイント図解・比較表・データグラフ"""
    from PIL import Image, ImageDraw, ImageFont
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    slides = []
    keywords = theme.get("keywords", ["ポイント1", "ポイント2", "ポイント3"])

    # スライド1: タイトルカード（黄色帯＋テーマ名）
    img1 = _create_title_slide(theme.get("theme", ""), keywords)
    path1 = str(TEMP_DIR / f"infographic_title_{int(time.time())}.png")
    img1.save(path1)
    slides.append({"path": path1, "duration": 8.0, "type": "image"})

    # スライド2: 3ポイント比較（カラーボックス）
    img2 = _create_points_slide(keywords[:3])
    path2 = str(TEMP_DIR / f"infographic_points_{int(time.time())}.png")
    img2.save(path2)
    slides.append({"path": path2, "duration": 10.0, "type": "image"})

    # スライド3: まとめスライド
    img3 = _create_summary_slide(theme.get("theme", ""))
    path3 = str(TEMP_DIR / f"infographic_summary_{int(time.time())}.png")
    img3.save(path3)
    slides.append({"path": path3, "duration": 8.0, "type": "image"})

    return slides


def _create_title_slide(title: str, keywords: list) -> Image:
    """タイトルスライド: 濃色背景 + 黄色帯 + 白テキスト"""
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new("RGB", (1280, 720), color=(20, 20, 40))
    draw = ImageDraw.Draw(img)

    # 黄色帯
    draw.rectangle([0, 280, 1280, 440], fill=(255, 215, 0))

    # フォント取得
    font = _get_font(60)
    font_sm = _get_font(36)

    # タイトル（帯内に黒文字）
    draw.text((640, 360), title[:20], font=font, fill=(10, 10, 10), anchor="mm")

    # キーワード（下部に白文字）
    kw_text = "  |  ".join([f"#{k}" for k in keywords[:4]])
    draw.text((640, 550), kw_text, font=font_sm, fill=(200, 200, 200), anchor="mm")

    return img


def _create_points_slide(points: list) -> Image:
    """3ポイント比較スライド: カラーボックス3つ"""
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new("RGB", (1280, 720), color=(20, 20, 40))
    draw = ImageDraw.Draw(img)

    colors = [(255, 215, 0), (100, 200, 255), (255, 130, 100)]
    font = _get_font(36)
    font_num = _get_font(72)

    for i, (point, color) in enumerate(zip(points[:3], colors)):
        x = 80 + i * 400
        # カラーボックス
        draw.rectangle([x, 150, x + 360, 570], fill=color, outline=None)
        # 番号
        draw.text((x + 180, 250), str(i + 1), font=font_num, fill=(10, 10, 10), anchor="mm")
        # テキスト
        draw.text((x + 180, 400), str(point)[:10], font=font, fill=(10, 10, 10), anchor="mm")

    return img
```

## 改善3: 動画尺20分以上統一（FB3対応）

### 環境変数変更

```diff
# .env
- VIDEO_DURATION_MIN=15
- VIDEO_DURATION_MAX=20
+ VIDEO_DURATION_MIN=20
+ VIDEO_DURATION_MAX=25
```

### generate_theme() 変更 (L134-151)

```diff
 prompt = f"""あなたはYouTubeチャンネルのプロデューサーです。
-  - 15〜20分の長尺動画を前提とすること
+  - 20〜25分の長尺動画を前提とすること
+  - 5セクション構成（導入3分＋本題4セクション各4分＋まとめ2分）
```

### generate_script() 変更 (L183-310)

```diff
# セクション構成を4→5に拡張
- # --- セクション1: フック + 導入（0:00〜3:00） ---
- # --- セクション2: 前半（3:00〜8:00） ---
- # --- セクション3: 後半（8:00〜13:00） ---
- # --- セクション4: まとめ + CTA ---
+ # --- セクション1: フック + 導入（0:00〜3:00） ---
+ # --- セクション2: ポイント1-2（3:00〜8:00） ---
+ # --- セクション3: ポイント3-4（8:00〜13:00） ---
+ # --- セクション4: ポイント5 + 実例/ケーススタディ（13:00〜20:00） ---
+ # --- セクション5: まとめ + CTA（20:00〜22:00） ---
```

各セクションのプロンプトに「文字数: 1000-1200文字（読み上げ約4-5分相当）」を指定し、合計5000-6000文字の台本で20-25分動画を生成。

## 改善4: サムネイル（FB4対応）— `generate_thumbnail()` L589-686

### 方針
フォントサイズ拡大、配色統一（黄×黒）、テキスト8-10文字、縁取り強化。

### 変更内容

```python
# === 変更後 generate_thumbnail() ===

def generate_thumbnail(theme: dict, output_path: str) -> str:
    """PILサムネイル生成 — ブランド統一版（黄帯+大文字+キーワード）"""
    from PIL import Image, ImageDraw, ImageFont

    width, height = 1280, 720
    # 濃い紫〜黒のグラデーション風背景
    img = Image.new("RGB", (width, height), color=(15, 10, 30))
    draw = ImageDraw.Draw(img)

    # ブランドカラー定義
    BRAND_YELLOW = (255, 204, 0)    # #FFCC00
    BRAND_PURPLE = (100, 50, 180)   # サブカラー
    WHITE = (255, 255, 255)
    BLACK = (10, 10, 10)

    # 上部: 黄色帯（フック文用）
    draw.rectangle([0, 0, width, 120], fill=BRAND_YELLOW)

    # 下部: 紫帯（キーワード用）
    draw.rectangle([0, height - 80, width, height], fill=BRAND_PURPLE)

    # フォント取得（大きめ）
    font_xl = _get_font(96)     # メインタイトル
    font_lg = _get_font(48)     # フック文
    font_md = _get_font(36)     # キーワード

    # フック文（黄色帯内 — 黒文字）
    hook = theme.get("hook", "")
    if hook:
        hook_short = hook[:20]
        draw.text((640, 60), hook_short, font=font_lg, fill=BLACK, anchor="mm")

    # メインタイトル（中央 — 白文字+黒縁取り — 最大10文字×2行）
    title = theme.get("theme", "動画タイトル")
    # 8-10文字に短縮（パワーワード抽出）
    title_short = title[:20]
    if len(title_short) > 10:
        line1 = title_short[:10]
        line2 = title_short[10:20]
        lines = [line1, line2]
    else:
        lines = [title_short]

    y_start = 300 if len(lines) == 1 else 260
    for line in lines:
        # 太い縁取り（5px）
        for dx in range(-5, 6):
            for dy in range(-5, 6):
                draw.text((640 + dx, y_start + dy), line,
                          font=font_xl, fill=BLACK, anchor="mm")
        draw.text((640, y_start), line, font=font_xl, fill=WHITE, anchor="mm")
        y_start += 120

    # キーワードタグ（紫帯内 — 白文字）
    keywords = theme.get("keywords", [])[:3]
    kw_text = "  ".join([f"#{k}" for k in keywords])
    draw.text((640, height - 40), kw_text, font=font_md, fill=WHITE, anchor="mm")

    # 右下: チャンネルロゴ枠（将来のロゴ配置用）
    draw.rectangle([width - 120, height - 200, width - 20, height - 100],
                   outline=BRAND_YELLOW, width=2)
    draw.text((width - 70, height - 150), "CH", font=font_md,
              fill=BRAND_YELLOW, anchor="mm")

    img.save(output_path, "PNG", quality=95)
    logger.info(f"✅ サムネイル生成完了: {output_path}")
    return output_path
```

### 共通フォントヘルパー（新規追加）

```python
def _get_font(size: int):
    """日本語フォント取得ヘルパー"""
    from PIL import ImageFont
    font_paths = [
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/google-noto-cjk/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    for fp in font_paths:
        try:
            return ImageFont.truetype(fp, size)
        except Exception:
            continue
    return ImageFont.load_default()
```

## 技術制約チェック

| 制約 | 確認結果 |
|-----|---------|
| EC2 t4g.medium 4GB RAM | ✅ テロップ生成は1フレームずつ → メモリ2GB以下 |
| ARM/Graviton互換 | ✅ moviepy/PIL/matplotlib 全てARM対応 |
| Python 3.9 | ✅ 新規コード全てPython 3.9互換 |
| 無料API | ✅ VOICEVOX=無料、gTTS=無料、Pexels=無料 |
| ElevenLabs不使用 | ✅ VOICEVOX + gTTSのみ（ElevenLabsは将来的オプション） |

## 実装スケジュール

| Phase | 内容 | 期間 | 効果 |
|-------|------|------|------|
| **A (即実装)** | gTTS速度1.25x + .env尺変更 + サムネイル改修 | 1日 | 音声改善・尺統一・サムネ |
| **B (1-2日)** | テロップ自動合成 + 図解強化 + スクリプト5セクション化 | 2日 | 映像品質大幅向上 |
| **C (将来)** | VOICEVOX Docker導入 + キャラクター合成 | 1-2週 | 音声品質さらに向上 |

---

# 成果物3：チャンネルブランディング提案

## 対応FB: FB5（アイコン初期値）、FB6（チャンネル名デフォルト）

## チャンネル名候補

| # | 候補名 | パターン | 理由 | 検索性 |
|---|--------|---------|------|--------|
| 1 | **マネーAI大学** | 教育系（～大学） | 両学長パターン踏襲。「マネー」「AI」で検索ヒット。教育的信頼感 | 高 |
| 2 | **AI投資ラボ** | 専門系（～ラボ） | 「投資」「AI」の組合せ。研究的・先進的イメージ | 高 |
| 3 | **サラリーマンのお金チャンネル** | ターゲット明示型 | ターゲット層が名前で分かる。検索「サラリーマン 投資」にヒット | 高 |
| 4 | **ロボ先生のお金の教室** | キャラクター型 | キャラ名を冠に。親近感＋教育性。ゆっくり解説パターン | 中-高 |
| 5 | **フィナンスAIチャンネル** | 英語+日本語ミックス | 「フィナンス」で専門性、「AI」でテック感。グローバル感 | 中 |

**推奨**: **案1「マネーAI大学」** or **案4「ロボ先生のお金の教室」**
- 案1: シンプルで検索性最高。初期チャンネルに最適
- 案4: キャラクター展開しやすい。長期ブランド構築向き

## アイコン方針

### パターンA: AIロボットキャラクター（推奨）
- **デザイン**: かわいいロボット + メガネ + 教科書
- **配色**: 背景=紫グラデ(#6633CC→#3311AA) + キャラ=黄色(#FFCC00)
- **サイズ**: 800×800px（YouTube推奨）
- **効果**: 親近感＋AI感＋教育感
- **制作ツール**: Canva（無料テンプレ活用）or Midjourney/DALL-E

### パターンB: テキストロゴ
- **デザイン**: チャンネル名の頭文字 + グラフ矢印
- **配色**: 背景=黒 + テキスト=黄色
- **効果**: シンプル＋プロフェッショナル
- **制作ツール**: Figma（無料）

### パターンC: コイン＋グラフアイコン
- **デザイン**: コインのシルエット + 上昇グラフ
- **配色**: 背景=紫 + アイコン=黄＋白
- **効果**: 金融感が強い

## バナー方針

**推奨**: パターンA（キャラクター＋テキスト型）
- **サイズ**: 2560×1440px
- **セーフエリア**: 1546×423px にテキスト配置
- **レイアウト**: 左=キャラクター(40%) + 中央=チャンネル名＋説明文(40%) + 右=装飾(20%)
- **配色**: 背景=濃い紫→黒グラデーション、テキスト=黄色、キャラ=カラフル
- **説明文**: 「サラリーマンのためのAI×投資・節約チャンネル」

## ブランドカラーパレット

| 用途 | カラー | コード | 効果 |
|------|--------|--------|------|
| **プライマリー** | 黄色 | #FFCC00 | 目立つ、クリック誘導 |
| **セカンダリー** | 紫 | #6633CC | 信頼感、差別化 |
| **アクセント** | オレンジ | #FF9900 | 暖かみ、CTA強調 |
| **背景** | 黒〜濃いグレー | #1a1a2e | モダン、コントラスト |
| **テキスト** | 白 | #FFFFFF | 可読性 |

## 実装手順
1. チャンネル名をユーザーが最終決定
2. Canva（無料）でアイコン＋バナーを作成
3. YouTubeチャンネル設定で反映
4. サムネイルテンプレのカラーコードをパイプラインに反映（成果物2参照）

---

# 成果物4：最初の3本の動画テーマ案

## テーマ選定基準
1. **検索ボリューム**: 月1万〜10万のキーワード
2. **パイプライン検証**: 新機能（テロップ・図解・サムネイル・音声改善）をテストできるテーマ
3. **ターゲット**: 日本のサラリーマン向け投資/AI/節約
4. **実践性**: 視聴者が「今日からできる」と感じる内容

## 動画1:「ChatGPT×家計簿で月5万円節約する完全ガイド」

- **タイトル案**: 「【知らないと損】ChatGPT×家計簿で月5万円節約！AI活用5つの方法」
- **KW**: ChatGPT 節約 / AI 家計管理 / 月5万円節約
- **検索ボリューム**: 月5千〜1万
- **想定再生数**: 5千〜3万回（新規チャンネル）

### チャプター構成（20分）

| 時間 | チャプター | 尺 | 内容 |
|------|----------|------|------|
| 0:00 | フック | 1分 | 「月5万円節約、ChatGPTで本当にできます」 |
| 1:00 | 導入 | 2分 | 従来の家計管理の限界とAIの可能性 |
| 3:00 | 方法1: ChatGPT設定 | 3.5分 | 具体的な設定手順と最適なプロンプト |
| 6:30 | 方法2: 支出分析 | 3.5分 | AIによる支出パターン分析と削減提案 |
| 10:00 | 方法3: 自動振り分け | 3.5分 | 貯金・投資の自動振り分けの仕組み |
| 13:30 | 方法4: 目標プラン | 3.5分 | AI対話で月5万円節約プランを作成 |
| 17:00 | 方法5: ケーススタディ | 2分 | 実例（仮想データ）による効果検証 |
| 19:00 | まとめ＋CTA | 1分 | 5つの振り返り + 登録・コメント促進 |

### 映像・音声仕様
- **音声**: gTTS 1.25x（Phase A） / VOICEVOX（Phase C）
- **映像**: 濃色背景 + テロップ + 図解スライド3枚 + ChatGPTスクリーンショット風
- **サムネイル**: 「月5万円節約」（黄色帯・96pt） + ChatGPTアイコン風 + ブランドカラー

## 動画2:「月3万円から始める米国高配当株投資【2026年版】」

- **タイトル案**: 「【初心者向け】月3万円から始める米国高配当株5ステップ完全ガイド」
- **KW**: 米国高配当株 / 初心者 / 月3万円 / NISA
- **検索ボリューム**: 月1万〜3万
- **想定再生数**: 1万〜5万回

### チャプター構成（22分）

| 時間 | チャプター | 尺 | 内容 |
|------|----------|------|------|
| 0:00 | フック | 0.5分 | 「米国株で月5千円の配当を受け取る人が急増」 |
| 0:30 | 導入 | 2.5分 | なぜ米国高配当株か（日米比較データ） |
| 3:00 | Step1: 証券口座 | 4分 | 楽天・SBI・マネックス比較と開設手順 |
| 7:00 | Step2: NISA活用 | 4分 | NISA制度の仕組みと節税メリット |
| 11:00 | Step3: 銘柄選定 | 4分 | 配当利回り4-6%の銘柄5つと選び方 |
| 15:00 | Step4: 購入手順 | 3分 | 実際の画面で購入プロセス解説 |
| 18:00 | Step5: 管理・再投資 | 2.5分 | 配当金再投資と複利効果 |
| 20:30 | まとめ＋CTA | 1.5分 | 5ステップ振り返り + 次回予告 |

### 映像・音声仕様
- **音声**: 落ち着いた専門家トーン（VOICEVOX speaker_id調整 or gTTS 1.2x）
- **映像**: チャート図解 + 証券口座スクリーンショット風 + 比較表テロップ
- **サムネイル**: 「月3万円→月5千円配当」（黄色帯）+ 上昇グラフ矢印

## 動画3:「2026年サラリーマンが知らないと損する金融トレンド3つ」

- **タイトル案**: 「【2026年版】サラリーマンが知らないと損する金融トレンド3つ」
- **KW**: 2026年 金融トレンド / サラリーマン / 新NISA / AI投資
- **検索ボリューム**: 月5千〜1.5万
- **想定再生数**: 5千〜10万回

### チャプター構成（20分）

| 時間 | チャプター | 尺 | 内容 |
|------|----------|------|------|
| 0:00 | フック | 1分 | 「2026年、サラリーマンの9割が知らないトレンド」 |
| 1:00 | 導入 | 2分 | 2025年振り返りと2026年の変化要因 |
| 3:00 | トレンド1: 新金融制度 | 4分 | NISA改正、確定拠出年金の変更点 |
| 7:00 | トレンド2: AI×投資 | 4分 | AIアドバイザー・ロボアドの最新動向 |
| 11:00 | トレンド3: 暗号資産 | 4分 | 機関投資家参入と規制動向 |
| 15:00 | 準備ステップ | 2.5分 | 各トレンドに対する具体的行動 |
| 17:30 | リスク注意点 | 1.5分 | 詐欺リスク・損失可能性の警告 |
| 19:00 | まとめ＋CTA | 1分 | 3トレンド総括 + コメント促進 |

### 映像・音声仕様
- **音声**: テンポやや速め（1.3x）でニュース解説風
- **映像**: トレンド別の図解 + データグラフ + ニュースヘッドライン風テロップ
- **サムネイル**: 「2026年」「3つのトレンド」（黄色帯）+ 矢印アイコン

## 制作スケジュール

| 週 | 作業 | 成果物 |
|----|------|--------|
| **Day 1** | Phase A実装（gTTS速度調整 + .env + サムネイル改修） | 改善パイプラインv3 |
| **Day 2-3** | Phase B実装（テロップ + 図解 + スクリプト5セクション化） | テスト動画1本 |
| **Day 4** | 動画1「ChatGPT×節約」制作＋アップロード | 動画1本目 |
| **Day 5** | 動画2「米国高配当株」制作＋アップロード | 動画2本目 |
| **Day 6** | 動画3「金融トレンド」制作＋アップロード | 動画3本目 |
| **Day 7+** | KPI測定（再生数/CTR/維持率）＋ブランディング反映 | 分析レポート |

## 品質ゲート
- 各動画制作後、YouTube Data APIで48時間後の再生数・CTR・視聴維持率を測定
- 改善前（v2）との定量比較
- 動画2→3への改善フィードバック反映

---

# フィードバック対応マトリクス（全成果物横断）

| FB# | フィードバック | 成果物1 | 成果物2 | 成果物3 | 成果物4 |
|-----|------------|---------|---------|---------|---------|
| 1 | 音声遅い・AI臭い | 音声分析 | VOICEVOX+gTTS改善 | — | 各動画音声仕様 |
| 2 | 映像マッチしない | 映像構成分析 | テロップ+図解実装 | — | 映像仕様記載 |
| 3 | 尺20分以上統一 | 尺分析 | .env+スクリプト変更 | — | 全動画20分以上 |
| 4 | サムネ不良 | サムネ分析 | PIL全面改修 | カラーパレット | サムネ案記載 |
| 5 | アイコン初期値 | ブランド分析 | — | アイコン3案 | — |
| 6 | 名前デフォルト | 命名分析 | — | 名前5案 | — |
