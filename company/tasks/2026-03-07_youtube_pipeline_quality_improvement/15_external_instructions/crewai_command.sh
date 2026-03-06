#!/bin/bash
# ============================================================
# CrewAI 外部実行指示書
# タスク: YouTube競合チャンネル・動画 大規模Web調査
# 対象ジャンル: 金融・投資・節約（日本語YouTube）
# 出力先: company/tasks/2026-03-07_youtube_pipeline_quality_improvement/20_worker_outputs/
# 作成者: strategy-manager (WBS Step 1 / execution: external)
# 作成日: 2026-03-07
# ============================================================

# ============================================================
# 事前確認
# ============================================================
# 1. WSLを起動していること
# 2. CrewAI仮想環境が存在すること（04_RESEARCH/agents/market_research_crewai）
# 3. GROQ_API_KEY が .env に設定されていること
# 4. 出力先ディレクトリが存在すること

OUTPUT_DIR="/mnt/c/Users/tshibasaki/Desktop/etc/work/task/company/tasks/2026-03-07_youtube_pipeline_quality_improvement/20_worker_outputs"
CREWAI_DIR="/mnt/c/Users/tshibasaki/Desktop/etc/work/task/04_RESEARCH/agents/market_research_crewai"

# 出力先ディレクトリ作成
mkdir -p "$OUTPUT_DIR"

# ============================================================
# 実行コマンド
# ============================================================

cd "$CREWAI_DIR"
source /home/crewai/.venv/bin/activate

# --- 調査1: 「お金 投資 サラリーマン」系チャンネル分析 ---
python run.py \
    --topic "YouTube日本語チャンネル「お金 投資 サラリーマン」ジャンル競合分析。100K再生以上の動画を持つチャンネルの音声スピード・トーン・映像構成（テロップ/図解/アニメーション）・サムネイルデザイン（文字数/配色/レイアウト）・チャンネルブランディング（名前/アイコン/バナー）・動画尺パターンを詳細分析すること。具体的なチャンネル名・動画URLを含めること。確認できないものは[推測]タグを付与すること。" \
    --outdir "$OUTPUT_DIR/crewai_research_01" \
    --provider groq

# --- 調査2: 「節約 貯金 資産運用」系チャンネル分析 ---
python run.py \
    --topic "YouTube日本語チャンネル「節約 貯金 資産運用」ジャンル競合分析。100K再生以上の動画を持つチャンネルの音声品質（gTTSとの違い）・映像構成（図解の使い方）・サムネイルデザイン・チャンネルブランディング・動画長（20分以上の構成パターン）を詳細分析すること。具体的なチャンネル名・動画URLを含めること。確認できないものは[推測]タグを付与すること。" \
    --outdir "$OUTPUT_DIR/crewai_research_02" \
    --provider groq

# ============================================================
# 出力後処理: report.json を Markdown に変換
# ============================================================
# CrewAI実行後、以下のPythonスクリプトでMarkdownに変換する

python3 - <<'PYTHON_EOF'
import json
import os

output_dir = "/mnt/c/Users/tshibasaki/Desktop/etc/work/task/company/tasks/2026-03-07_youtube_pipeline_quality_improvement/20_worker_outputs"
output_md = os.path.join(output_dir, "01_competitor_analysis.md")

# 2つのreport.jsonを読み込んで結合
reports = []
for subdir in ["crewai_research_01", "crewai_research_02"]:
    report_path = os.path.join(output_dir, subdir, "report.json")
    raw_path = os.path.join(output_dir, subdir, "raw_output.txt")

    if os.path.exists(report_path):
        with open(report_path, "r", encoding="utf-8") as f:
            reports.append(json.load(f))
    elif os.path.exists(raw_path):
        # JSONが見つからない場合はraw_outputをそのまま使用
        with open(raw_path, "r", encoding="utf-8") as f:
            reports.append({"raw_output": f.read(), "source": subdir})

# Markdownに変換
md_lines = [
    "# YouTube競合分析レポート（CrewAI調査結果）",
    "",
    "**調査日**: 2026-03-07",
    "**調査方法**: CrewAI + Groq Web調査",
    "**対象ジャンル**: 金融・投資・節約（日本語YouTube、100K再生以上）",
    "**注意**: 実在確認できないチャンネル名・URLには [推測] タグを付与",
    "",
    "---",
    "",
]

for i, report in enumerate(reports, 1):
    md_lines.append(f"## 調査{i}: {['お金・投資・サラリーマン', '節約・貯金・資産運用'][i-1]}ジャンル")
    md_lines.append("")

    if "raw_output" in report:
        md_lines.append(report["raw_output"])
    else:
        # report.jsonスキーマに沿って変換
        if "market_definition" in report:
            md_lines.append(f"### 市場定義\n{report.get('market_definition', '')}\n")

        if "players" in report:
            md_lines.append("### 主要チャンネル・プレイヤー")
            for p in report.get("players", []):
                tier = p.get("tier", "")
                name = p.get("name", "")
                desc = p.get("description", "")
                src  = p.get("source", "")
                md_lines.append(f"- **[{tier}] {name}**: {desc}")
                if src:
                    md_lines.append(f"  - 参照: {src}")
            md_lines.append("")

        if "trends" in report:
            md_lines.append("### トレンド・特徴")
            for t in report.get("trends", []):
                md_lines.append(f"- **{t.get('trend', '')}**: {t.get('impact', '')}")
                if t.get("source"):
                    md_lines.append(f"  - 参照: {t.get('source', '')}")
            md_lines.append("")

        if "implications" in report:
            md_lines.append("### ビジネス示唆")
            for imp in report.get("implications", []):
                priority = imp.get("priority", "")
                message  = imp.get("message", "")
                md_lines.append(f"- [{priority}] {message}")
            md_lines.append("")

        if "sources" in report:
            md_lines.append("### 参照ソース")
            for src in report.get("sources", []):
                md_lines.append(f"- {src}")
            md_lines.append("")

    md_lines.append("---")
    md_lines.append("")

# 保存
with open(output_md, "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines))

print(f"[完了] 競合分析レポートを保存しました: {output_md}")
PYTHON_EOF

echo ""
echo "============================================================"
echo "[CrewAI 実行完了]"
echo "出力ファイル: $OUTPUT_DIR/01_competitor_analysis.md"
echo "次のステップ: worker-extractor が 01_competitor_analysis.md を読み込み、"
echo "              02_extracted_elements.md を生成する（内部ワーカー実行）"
echo "============================================================"
