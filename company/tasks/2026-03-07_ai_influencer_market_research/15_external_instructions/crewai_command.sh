#!/bin/bash

# CrewAI 実行指示書：AIインフルエンサー市場調査
# 実行日：2026-03-07
# 出力先：company/tasks/2026-03-07_ai_influencer_market_research/20_worker_outputs/

cd /mnt/c/Users/tshibasaki/Desktop/etc/work/task/04_RESEARCH/agents/market_research_crewai

source /home/crewai/.venv/bin/activate

# ===== CREWAI 実行コマンド（Groq使用：無料） =====

python run.py \
    --topic "AI virtual influencer market research 2025-2026: Top 10 global AI influencers (Lil Miquela, Aitana López, Maia, など) with followers count, concepts, revenue models, tools used, success factors. Japan domestic AI influencer cases (5+ examples). 2025-2026 trends: AI disclosure regulation (Instagram/TikTok), hot genres (beauty, finance, lifestyle, travel), emerging tools (FLUX, Instanton, video generation). Market feasibility analysis of 4 concepts: 1) Finance+AI beauty female, 2) Tech+Lifestyle, 3) Travel+AI, 4) Other blue ocean niches for Japan market. Monetization reality: earnings per follower by tier, AI disclosure impact on engagement, actual monthly income examples from successful AI influencers." \
    --outdir "/mnt/c/Users/tshibasaki/Desktop/etc/work/task/company/tasks/2026-03-07_ai_influencer_market_research/20_worker_outputs/" \
    --provider groq

# ===== 実行後の処理 =====
# 1. report.json が出力されたか確認
# 2. report.json の JSON スキーマを確認
# 3. Windows側のパスに複製（Windows PowerShellで実行）
# PowerShell: Copy-Item -Path "C:\Users\tshibasaki\Desktop\etc\work\task\company\tasks\2026-03-07_ai_influencer_market_research\20_worker_outputs\report.json" -Destination "C:\Users\tshibasaki\Desktop\etc\work\task\04_RESEARCH\"

echo "CrewAI execution completed. Check 20_worker_outputs/ for report.json"
