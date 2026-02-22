#!/usr/bin/env python3
"""
run.py — CrewAI Market Research エントリーポイント

Usage:
    # OpenAI（有料 / gpt-4o-mini は格安）
    python run.py --topic "日本のSaaS市場" --outdir "/mnt/c/.../drafts/saas"

    # Groq（無料・要APIキー登録 https://console.groq.com）
    python run.py --topic "日本のSaaS市場" --outdir "/mnt/c/.../drafts/saas" \\
                  --provider groq

    # Ollama（完全無料・ローカルLLM・要 ollama pull llama3.2）
    python run.py --topic "日本のSaaS市場" --outdir "/mnt/c/.../drafts/saas" \\
                  --provider ollama --model llama3.2
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# .env を読み込む（スクリプトと同じディレクトリ）
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

from crew import build_crew, parse_result


# プロバイダごとのデフォルトモデル
DEFAULT_MODELS = {
    "openai": "gpt-4o-mini",
    "groq":   "llama-3.3-70b-versatile",   # 無料枠最高性能・日本語OK
    "ollama": "llama3.2",                   # ローカル実行
}


def build_llm(provider: str, model: str):
    """
    プロバイダに応じた CrewAI LLM オブジェクトを返す。
    OpenAI の場合は None を返し、CrewAI のデフォルト動作に任せる。
    """
    if provider == "openai":
        # CrewAI デフォルト（OPENAI_API_KEY + OPENAI_MODEL_NAME 環境変数）
        os.environ.setdefault("OPENAI_MODEL_NAME", model)
        return None

    # CrewAI の LLM クラスを使う（LiteLLM 経由で多プロバイダ対応）
    try:
        from crewai import LLM
    except ImportError:
        print("[ERROR] crewai の LLM クラスが見つかりません。crewai >= 0.80 が必要です。")
        sys.exit(1)

    if provider == "groq":
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            print("[ERROR] GROQ_API_KEY が .env に設定されていません。")
            print("  1. https://console.groq.com でアカウント作成（無料）")
            print("  2. API Keys → Create API Key")
            print("  3. .env の GROQ_API_KEY= に貼り付け")
            sys.exit(1)
        return LLM(
            model=f"groq/{model}",
            api_key=api_key,
            max_retries=8,          # レート制限時に最大8回リトライ
            timeout=120,            # タイムアウト 2分
        )

    elif provider == "ollama":
        base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        print(f"[Ollama] base_url={base_url}  model={model}")
        print("  ※ Ollama が起動していること & モデルが pull 済みであることを確認してください")
        print(f"     ollama pull {model}")
        return LLM(
            model=f"ollama/{model}",
            base_url=base_url,
        )

    else:
        print(f"[ERROR] 不明なプロバイダ: {provider}")
        print("  指定可能: openai / groq / ollama")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="CrewAI Market Research Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
プロバイダ別の起動例:
  # OpenAI（有料 / 1回 $0.05〜0.15 目安）
  python run.py --topic "日本のSaaS市場" --outdir "./outputs/saas"

  # Groq（無料 / https://console.groq.com でAPIキー取得）
  python run.py --topic "日本のSaaS市場" --outdir "./outputs/saas" --provider groq

  # Ollama（完全無料 / ローカルLLM）
  python run.py --topic "日本のSaaS市場" --outdir "./outputs/saas" --provider ollama
        """
    )
    parser.add_argument("--topic",    required=True, help="調査テーマ（日本語可）")
    parser.add_argument("--outdir",   required=True, help="出力先ディレクトリ（report.json を配置）")
    parser.add_argument(
        "--provider",
        default="openai",
        choices=["openai", "groq", "ollama"],
        help="LLMプロバイダ: openai(有料) / groq(無料) / ollama(完全無料ローカル) (default: openai)",
    )
    parser.add_argument(
        "--model",
        default=None,
        help=(
            "使用モデル名。省略時はプロバイダごとのデフォルトを使用。\n"
            "  openai: gpt-4o-mini\n"
            "  groq  : llama-3.3-70b-versatile\n"
            "  ollama: llama3.2"
        ),
    )
    args = parser.parse_args()

    # モデル名のデフォルト解決
    model = args.model or DEFAULT_MODELS.get(args.provider, "gpt-4o-mini")

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"  Market Research CrewAI")
    print(f"  Topic   : {args.topic}")
    print(f"  Outdir  : {outdir}")
    print(f"  Provider: {args.provider}")
    print(f"  Model   : {model}")
    print(f"  Started : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    # LLM オブジェクト構築
    llm = build_llm(args.provider, model)

    # CrewAI 実行
    crew = build_crew(args.topic, llm=llm)
    raw_result = crew.kickoff()

    # raw output を保存（デバッグ用）
    raw_path = outdir / "raw_output.txt"
    raw_path.write_text(str(raw_result), encoding="utf-8")
    print(f"\n[raw output saved] → {raw_path}")

    # JSON パース
    try:
        data = parse_result(str(raw_result))
        print("[JSON parse] SUCCESS")
    except Exception as e:
        print(f"[JSON parse] FAILED: {e}")
        print("  → raw_output.txt を確認してください")
        data = {
            "error": str(e),
            "raw":   str(raw_result)[:3000],
        }

    # メタデータ付与
    data["_meta"] = {
        "topic":     args.topic,
        "provider":  args.provider,
        "model":     model,
        "generated": datetime.now().isoformat(),
        "generator": "market_research_crewai",
    }

    # report.json 保存
    report_path = outdir / "report.json"
    report_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print(f"\n{'='*60}")
    print(f"  完了!")
    print(f"  report.json → {report_path}")
    print(f"  Finished   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
