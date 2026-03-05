# 自環境 PLAYBOOK.md ポイント（agent_factory 生成用）
Source: C:\Users\tshibasaki\Desktop\etc\work\task\.claude\PLAYBOOK.md

## 市場調査パイプライン（CrewAI）
場所: 04_RESEARCH/agents/market_research_crewai/

## 実行フロー
run.sh → Researcher（Web検索） → Analyst（市場分析） → Writer（JSON生成） → Claude Code（PPT/MD生成）

## コマンド（WSL）
```bash
source /home/crewai/.venv/bin/activate
python run.py --topic "テーマ" --outdir "/mnt/c/.../output" --provider groq
```

## プロバイダー
- Groq: 無料枠（推奨）
- Ollama: 完全無料ローカル
- OpenAI: 有料・高精度

## インフラ
- venv: /home/crewai/.venv（Linuxネイティブ側）
- 出力: report.json → Claude Codeが読んでPPT/MD生成
