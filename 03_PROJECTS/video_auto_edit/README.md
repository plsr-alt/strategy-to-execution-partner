# 動画自動編集パイプライン

入力動画から **無音カット → テンポ調整（ハイパースキップ） → 字幕生成 → 焼き込み** までを全自動で処理します。

## セットアップ

### 1. 前提条件

- **Python 3.10+**
- **ffmpeg**（PATH に通っていること）

### 2. ffmpeg インストール

```bash
# Windows
winget install ffmpeg
# or: choco install ffmpeg / scoop install ffmpeg

# Mac
brew install ffmpeg

# Ubuntu / Debian
sudo apt update && sudo apt install ffmpeg
```

### 3. Python 依存インストール

```bash
pip install -r requirements.txt
```

依存パッケージ:
- `faster-whisper` — 音声認識（文字起こし）
- `pyyaml` — 設定ファイル読み込み

## 使い方

### 基本

1. `./in/` に動画ファイルを置く（mp4, mov, avi, mkv, webm 対応）
2. 実行:

```bash
# Linux / Mac
chmod +x run.sh
./run.sh

# Windows
.\run.ps1

# 直接実行
python main.py
```

3. `./out/` に出力される:
   - `<名前>_final.mp4` — 字幕焼き込み済み動画
   - `<名前>_final.srt` — 字幕ファイル
   - `<名前>_transcript.txt` — 全文テキスト
   - `<名前>_edit_log.json` — 編集ログ（カット区間・速度変更・処理時間）

### オプション

```bash
# 設定ファイル指定
python main.py --config my_config.yaml

# 単一ファイル指定
python main.py --input path/to/video.mp4

# 一時ファイルを残す（デバッグ用）
python main.py --keep-temp
```

## パラメータ調整（config.yaml）

### 無音カット

| パラメータ | 初期値 | 説明 |
|-----------|--------|------|
| `silence.noise_threshold_db` | -35 | この dB 以下を無音とする。上げるとカット増加 |
| `silence.min_silence_duration` | 0.35 | この秒数以上の無音をカット。下げるとカット増加 |
| `silence.padding_before` | 0.08 | カット前に残す余白（秒） |
| `silence.padding_after` | 0.05 | カット後に残す余白（秒） |

### テンポ調整

| パラメータ | 初期値 | 説明 |
|-----------|--------|------|
| `tempo.enabled` | true | テンポ調整の ON/OFF |
| `tempo.speedup_factor` | 1.25 | 冗長区間の速度倍率 |
| `tempo.max_speed` | 1.35 | 速度変更の上限 |
| `tempo.low_density_threshold` | 1.5 | 単語密度がこれ以下で「冗長」判定 |
| `tempo.fast_speech_threshold` | 4.5 | この密度以上は「早口」として速度変更しない |

### 字幕

| パラメータ | 初期値 | 説明 |
|-----------|--------|------|
| `subtitle.max_chars_per_line` | 22 | 1行の最大文字数 |
| `subtitle.max_lines` | 2 | 最大行数 |
| `subtitle.min_display_sec` | 0.8 | 最短表示時間 |
| `subtitle.max_display_sec` | 4.0 | 最長表示時間 |
| `subtitle.style.font_name` | Noto Sans CJK JP | フォント |
| `subtitle.style.font_size` | 24 | フォントサイズ |

### 文字起こし

| パラメータ | 初期値 | 説明 |
|-----------|--------|------|
| `transcription.model_size` | base | Whisper モデルサイズ (tiny/base/small/medium/large-v2) |
| `transcription.language` | ja | 言語 |
| `transcription.device` | cpu | cpu / cuda |

### 音声

| パラメータ | 初期値 | 説明 |
|-----------|--------|------|
| `audio.target_lufs` | -16 | 目標ラウドネス |

## 固有名詞辞書

`./dict/terms.csv` で表記揺れを統一できます:

```csv
before,after
ユーチューブ,YouTube
チャットGPT,ChatGPT
```

## トラブルシュート

### ffmpeg が見つからない
```
ERROR: ffmpeg not found
```
→ ffmpeg をインストールして PATH に通してください。

### Whisper モデルのダウンロードが遅い
初回実行時にモデルをダウンロードします（base: 約 150MB）。
`transcription.model_size` を `tiny` にすると軽量化できます。

### 字幕のフォントが反映されない
- ffmpeg に libass サポートが必要です（ほとんどのビルドで含まれています）
- フォント名が正確であることを確認してください
- Windows: フォント名は正式名称（例: `Noto Sans CJK JP` → `Noto Sans CJK JP Regular`）

### メモリ不足
- `transcription.model_size` を `tiny` か `base` に変更
- `transcription.device` を `cpu` に変更

### 出力が再生できない
- `output.pixel_format` が `yuv420p` であることを確認
- `output.video_codec` を `libx264` にする（互換性最高）

## ディレクトリ構成

```
video_auto_edit/
├── main.py              # パイプライン本体
├── config.yaml          # 設定
├── requirements.txt     # Python 依存
├── run.sh / run.ps1     # ワンコマンド実行
├── dict/terms.csv       # 固有名詞辞書
├── modules/
│   ├── silence_detector.py   # 無音検出
│   ├── transcriber.py        # 文字起こし
│   ├── subtitle_builder.py   # 字幕生成
│   ├── tempo_adjuster.py     # テンポ調整
│   ├── assembler.py          # 動画組み立て
│   └── utils.py              # 共通ユーティリティ
├── in/                  # 入力動画
├── out/                 # 出力
└── assets/              # BGM / intro / outro
```

## 改善ポイント（TODO）

- [ ] GPU 対応（CUDA + NVENC）で大幅高速化
- [ ] auto-editor 連携でより精密なカット判定
- [ ] 話者分離（Speaker Diarization）対応
- [ ] 9:16 自動クロップ（Shorts / TikTok 向け）
- [ ] バッチ処理の並列化
- [ ] Web UI（Gradio / Streamlit）
- [ ] LLM による字幕校正（Groq API 連携）
