"""
crew.py — Market Research CrewAI 定義
Researcher → Analyst → Writer の 3 エージェント順次実行
"""

import json
import os
import re
from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool
from crewai_tools import SerperDevTool

# ── DuckDuckGo カスタムツール（API キー不要） ─────────────────
class DuckDuckGoTool(BaseTool):
    name: str = "web_search"  # スペースなし・小文字（Groq/LLM互換）
    description: str = (
        "Web検索ツール。キーワードを受け取り、関連するWebページの"
        "タイトル・URL・スニペットを返す。英語・日本語どちらも可。"
    )

    def _run(self, query: str) -> str:
        try:
            from ddgs import DDGS
        except ImportError:
            from duckduckgo_search import DDGS
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=8))
            if not results:
                return "検索結果が見つかりませんでした。"
            lines = []
            for r in results:
                lines.append(
                    f"Title: {r.get('title', '')}\n"
                    f"URL:   {r.get('href', '')}\n"
                    f"Snippet: {r.get('body', '')}"
                )
            return "\n\n".join(lines)
        except Exception as e:
            return f"検索エラー: {e}"


# ── ツール選択（SERPER_API_KEY があれば Serper を優先） ────────
def get_search_tool():
    if os.environ.get("SERPER_API_KEY"):
        return SerperDevTool()
    return DuckDuckGoTool()

search_tool = get_search_tool()

# ── 出力 JSON スキーマ（Writer に渡す仕様書）───────────────
OUTPUT_SCHEMA = """
{
  "market_definition": "市場の定義（1〜2文）",
  "market_size": [
    {
      "year": 2023,
      "value": 123,
      "unit": "億円",
      "assumption": "推定方法・前提",
      "source": "https://..."
    }
  ],
  "players": [
    {
      "tier": "Tier1",
      "name": "企業名",
      "description": "特徴（50字以内）",
      "source": "https://..."
    }
  ],
  "trends": [
    {
      "trend": "トレンド名",
      "impact": "事業への影響・示唆",
      "source": "https://..."
    }
  ],
  "implications": [
    {
      "message": "ビジネス示唆・アクション",
      "priority": "High"
    }
  ],
  "sources": ["https://url1", "https://url2"]
}
"""


def build_crew(topic: str, llm=None) -> Crew:
    """
    指定テーマの市場調査クルーを組み立てて返す。
    llm: crewai.LLM オブジェクト。None の場合は CrewAI デフォルト（OpenAI）を使用。
    crew.kickoff() で実行する。
    """

    # llm 引数をエージェントに渡すための辞書
    llm_kwargs = {"llm": llm} if llm is not None else {}

    # ── Agents ──────────────────────────────────────────────

    researcher = Agent(
        role="Market Researcher",
        goal=(
            f"「{topic}」について信頼できる一次情報・統計データ・URL を徹底収集する"
        ),
        backstory=(
            "あなたはB2Bコンサルファームのシニアリサーチャーです。"
            "政府統計・業界メディア・企業IR・調査会社レポートなど"
            "多様なソースからデータを収集し、情報の信頼性を評価します。"
            "必ず情報源 URL を記録します。"
        ),
        tools=[search_tool],
        verbose=True,
        allow_delegation=False,
        max_iter=10,
        **llm_kwargs,
    )

    analyst = Agent(
        role="Market Analyst",
        goal=(
            "収集データを構造化し、市場規模・プレイヤー分類・"
            "トレンド抽出・ビジネス示唆を導出する"
        ),
        backstory=(
            "あなたは戦略コンサルタントです。"
            "リサーチ結果をもとに市場規模（TAM/SAM）、"
            "主要プレイヤーの Tier 分類、"
            "マクロトレンドとその事業インパクトを定量・定性両面で分析します。"
            "各分析には根拠と URL を明記します。"
        ),
        verbose=True,
        allow_delegation=False,
        max_iter=5,
        **llm_kwargs,
    )

    writer = Agent(
        role="JSON Report Writer",
        goal="分析結果を後続システムが処理できる厳密な JSON で出力する",
        backstory=(
            "あなたはデータエンジニア兼テクニカルライターです。"
            "分析結果を PPT/Markdown 生成 AI が扱えるよう、"
            "指定スキーマに完全準拠した JSON のみを出力します。"
            "JSON の外に余分なテキストは一切出力しません。"
        ),
        verbose=True,
        allow_delegation=False,
        max_iter=3,
        **llm_kwargs,
    )

    # ── Tasks ───────────────────────────────────────────────

    research_task = Task(
        description=(
            f"「{topic}」について以下を Web 検索で調査・収集せよ。\n"
            "1. 市場の定義・スコープ（何を含み、何を含まないか）\n"
            "2. 市場規模データ（直近年・予測年・単位・出典URL）\n"
            "3. 主要プレイヤー（企業名・特徴・シェア・出典URL）\n"
            "4. 主要トレンド（技術・規制・消費者動向・出典URL）\n\n"
            "各情報には必ず出典 URL を付記すること。"
            "信頼度の低い情報は除外すること。"
        ),
        expected_output=(
            "市場定義、市場規模データ（年度・数値・出典URL）、"
            "主要プレイヤー一覧（企業名・特徴・出典URL）、"
            "主要トレンド一覧（説明・出典URL）を含む詳細レポート文章。"
            "各事実に URL を紐づけること。"
        ),
        agent=researcher,
    )

    analysis_task = Task(
        description=(
            f"Researcher の調査結果を受け取り「{topic}」を分析せよ。\n"
            "1. 市場規模の整理（年度別・CAGR 算出）\n"
            "2. プレイヤーを Tier1/Tier2/Tier3 に分類\n"
            "   （基準: 売上規模・市場シェア・影響力）\n"
            "3. 上位 3〜5 トレンドの抽出と事業インパクト評価\n"
            "4. ビジネス示唆の導出（参入機会・リスク・優先度付き）\n\n"
            "各分析には根拠と URL を明記すること。"
        ),
        expected_output=(
            "市場規模テーブル、Tier 分類済みプレイヤーリスト、"
            "トレンドと事業インパクト、優先度付きビジネス示唆を含む構造化分析結果。"
        ),
        agent=analyst,
        context=[research_task],
    )

    write_task = Task(
        description=(
            "Analyst の分析結果を受け取り、以下の厳密なJSONスキーマで出力せよ。\n"
            "【重要】JSONのみを出力すること。```json などのコードブロック記号も不要。\n\n"
            f"スキーマ:\n{OUTPUT_SCHEMA}"
        ),
        expected_output=(
            "上記スキーマに完全準拠したJSON文字列のみ。"
            "前後に余分なテキスト・コードブロック記号を含まないこと。"
        ),
        agent=writer,
        context=[research_task, analysis_task],
    )

    return Crew(
        agents=[researcher, analyst, writer],
        tasks=[research_task, analysis_task, write_task],
        process=Process.sequential,
        verbose=True,
    )


def parse_result(raw: str) -> dict:
    """CrewAI 出力から JSON を抽出してパース"""
    text = re.sub(r"```(?:json)?\s*", "", raw).strip()
    text = text.rstrip("`").strip()
    start = text.find("{")
    end = text.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError(f"JSONが見つかりません。raw:\n{raw[:500]}")
    return json.loads(text[start:end])
