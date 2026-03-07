#!/bin/bash

# CrewAI 市場調査実行スクリプト
# マルチチャネルSNS自動展開システムの市場調査

cd /mnt/c/Users/tshibasaki/Desktop/etc/work/task/04_RESEARCH/agents/market_research_crewai

# venv 有効化
source /home/crewai/.venv/bin/activate

# CrewAI 実行（Groq無料枠）
python run.py \
    --topic "マルチチャネルSNS自動展開システムの市場調査" \
    --outdir "/mnt/c/Users/tshibasaki/Desktop/etc/work/task/company/tasks/2026-03-08_marketing_multi_channel_sns/20_worker_outputs" \
    --provider groq \
    --model "llama-3.3-70b-versatile" \
    --max-iterations 10

# 実行結果確認
echo "=== CrewAI 実行完了 ==="
ls -la /mnt/c/Users/tshibasaki/Desktop/etc/work/task/company/tasks/2026-03-08_marketing_multi_channel_sns/20_worker_outputs/

# report.json を確認
if [ -f "/mnt/c/Users/tshibasaki/Desktop/etc/work/task/company/tasks/2026-03-08_marketing_multi_channel_sns/20_worker_outputs/report.json" ]; then
    echo "=== report.json found ==="
    head -50 "/mnt/c/Users/tshibasaki/Desktop/etc/work/task/company/tasks/2026-03-08_marketing_multi_channel_sns/20_worker_outputs/report.json"
else
    echo "=== raw_output.txt を確認 ==="
    cat "/mnt/c/Users/tshibasaki/Desktop/etc/work/task/company/tasks/2026-03-08_marketing_multi_channel_sns/20_worker_outputs/raw_output.txt"
fi
