#!/bin/bash
# CrewAI 実行指示書 — AI デジタル販売市場調査
# Date: 2026-03-07
# Task: BOOTH/pixivFANBOX/DLsite での AI画像販売トレンド調査

set -e

# === 環境設定 ===
WSL_CREWAI_DIR="/mnt/c/Users/tshibasaki/Desktop/etc/work/task/04_RESEARCH/agents/market_research_crewai"
OUTDIR="/mnt/c/Users/tshibasaki/Desktop/etc/work/task/company/tasks/2026-03-07_ai_digital_sales_market_survey/20_worker_outputs"

# 出力ディレクトリ作成
mkdir -p "$OUTDIR"

cd "$WSL_CREWAI_DIR"
source /home/crewai/.venv/bin/activate

# === 第1調査: BOOTH の AI画像販売 ===
echo "=== CrewAI Task 1: BOOTH AI画像販売 ==="
python run.py \
    --topic "BOOTH AI画像販売 2025 2026年 売上ランキング クリエイター事例 売上 価格帯 ジャンル TOP5 規約 ガイドライン" \
    --outdir "$OUTDIR/booth_research" \
    --provider groq

# === 第2調査: pixivFANBOX AI画像支援 ===
echo "=== CrewAI Task 2: pixivFANBOX AI画像支援 ==="
python run.py \
    --topic "pixivFANBOX AI画像クリエイター 2025 2026 支援者数 月額 価格帯 プラン構成 人気 事例 規約" \
    --outdir "$OUTDIR/fanbox_research" \
    --provider groq

# === 第3調査: DLsite AI専用ブース ===
echo "=== CrewAI Task 3: DLsite AI画像販売 ==="
python run.py \
    --topic "DLsite AI画像販売 AI専用ブース 2025 2026 売上規模 売上ランキング ジャンル 人気 販売戦略 事例" \
    --outdir "$OUTDIR/dlsite_research" \
    --provider groq

# === 第4調査: AI画像販売トレンド総括 ===
echo "=== CrewAI Task 4: AI画像販売トレンド 2025-2026 ==="
python run.py \
    --topic "AI生成画像デジタル販売 2025 2026 トレンド 売れるコンセプト 差別化 規制リスク 著作権 規約変更 イラスト 壁紙 キャラクター 3Dモデル" \
    --outdir "$OUTDIR/trends_research" \
    --provider groq

echo "=== All CrewAI tasks completed ==="
echo "Results saved to: $OUTDIR"
