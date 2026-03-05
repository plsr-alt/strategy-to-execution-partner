#!/bin/bash
# ============================================================
# 動画自動編集パイプライン — ワンコマンド実行スクリプト
# Usage: ./run.sh [config.yaml]
# ============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

CONFIG="${1:-config.yaml}"

echo "============================================"
echo " 動画自動編集パイプライン"
echo "============================================"
echo "Config: $CONFIG"
echo "Working dir: $SCRIPT_DIR"
echo ""

# --- 依存チェック ---
echo "[Check] Python..."
if ! command -v python3 &>/dev/null && ! command -v python &>/dev/null; then
    echo "ERROR: Python not found. Install Python 3.10+"
    exit 1
fi
PYTHON=$(command -v python3 || command -v python)
echo "  -> $($PYTHON --version)"

echo "[Check] ffmpeg..."
if ! command -v ffmpeg &>/dev/null; then
    echo "ERROR: ffmpeg not found."
    echo "Install: brew install ffmpeg (Mac) / sudo apt install ffmpeg (Ubuntu)"
    exit 1
fi
echo "  -> $(ffmpeg -version | head -1)"

echo "[Check] pip packages..."
$PYTHON -m pip install -q -r requirements.txt 2>/dev/null || {
    echo "WARNING: pip install failed. Trying to continue..."
}

# --- ディレクトリ準備 ---
mkdir -p in out tmp dict assets

# --- 入力チェック ---
INPUT_COUNT=$(find in -maxdepth 1 -type f \( -name "*.mp4" -o -name "*.mov" -o -name "*.avi" -o -name "*.mkv" -o -name "*.webm" \) 2>/dev/null | wc -l)
if [ "$INPUT_COUNT" -eq 0 ]; then
    echo ""
    echo "WARNING: No video files found in ./in/"
    echo "Put your video files in the ./in/ directory and run again."
    exit 0
fi
echo ""
echo "Found $INPUT_COUNT video(s) in ./in/"
echo ""

# --- 実行 ---
echo "Starting pipeline..."
echo "--------------------------------------------"
$PYTHON main.py --config "$CONFIG"
EXIT_CODE=$?

echo ""
echo "============================================"
if [ $EXIT_CODE -eq 0 ]; then
    echo " ✓ 完了！ 出力: ./out/"
else
    echo " ✗ エラーが発生しました (exit=$EXIT_CODE)"
    echo "   ログ: ./out/pipeline.log"
fi
echo "============================================"

exit $EXIT_CODE
