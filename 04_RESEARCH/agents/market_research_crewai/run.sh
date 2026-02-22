#!/usr/bin/env bash
# ============================================================
# run.sh — CrewAI Market Research ランナー（WSL bash 用）
#
# 使い方:
#   ./run.sh "調査テーマ" "出力先ディレクトリ(WSLパス)"
#
# 例:
#   ./run.sh "日本のSaaS市場調査 2025" \
#     "/mnt/c/Users/tshibasaki/Desktop/etc/work/task/05_CONTENT/drafts/saas_market"
# ============================================================
set -euo pipefail

TOPIC="${1:-}"
OUTDIR="${2:-}"

# ── 引数チェック ─────────────────────────────────────────────
if [[ -z "$TOPIC" || -z "$OUTDIR" ]]; then
    echo ""
    echo "Usage: ./run.sh <topic> <outdir>"
    echo ""
    echo "Example:"
    echo "  ./run.sh \"日本のSaaS市場調査\" \\"
    echo "    \"/mnt/c/Users/tshibasaki/Desktop/etc/work/task/05_CONTENT/drafts/saas_market\""
    echo ""
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$SCRIPT_DIR/.venv"

# ── venv チェック ────────────────────────────────────────────
if [[ ! -d "$VENV" ]]; then
    echo "[ERROR] venv が見つかりません: $VENV"
    echo ""
    echo "以下を実行してセットアップしてください:"
    echo "  cd \"$SCRIPT_DIR\""
    echo "  python3 -m venv .venv"
    echo "  source .venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# ── venv 有効化 ──────────────────────────────────────────────
source "$VENV/bin/activate"

echo ""
echo "========================================"
echo "  CrewAI Market Research"
echo "  Topic  : $TOPIC"
echo "  Outdir : $OUTDIR"
echo "========================================"
echo ""

python "$SCRIPT_DIR/run.py" --topic "$TOPIC" --outdir "$OUTDIR"
