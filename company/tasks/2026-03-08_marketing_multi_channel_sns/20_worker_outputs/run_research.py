#!/usr/bin/env python3
"""
Groq API を使用したマルチチャネルSNS自動展開システムの市場調査
"""

import json
import os
from datetime import datetime
from pathlib import Path

# Groq API
try:
    from groq import Groq
except ImportError:
    print("[ERROR] groq ライブラリがありません。pip install groq を実行してください")
    exit(1)

# API キーセット
API_KEY = os.environ.get("GROQ_API_KEY")
if not API_KEY:
    print("[ERROR] GROQ_API_KEY が設定されていません")
    exit(1)

client = Groq(api_key=API_KEY)

# 調査プロンプト
RESEARCH_PROMPT = """
あなたは業界専門の市場リサーチャーです。以下の7項目についてマルチチャネルSNS自動展開システムの市場調査を実施してください。

背景：YouTube月産15本の動画をInstagram / X / Pinterest / TikTokへ自動展開し、総露出を4-5倍化するシステムを構築する。Instagram Graph API + Pinterest API で直接投稿。月額¥0運用。コンテンツはAI×生活技術（家計管理・自動化・節約）。

=== 調査項目 ===

1. SNSマルチチャネル展開ツール・競合マップ
   - 主要ツール（Buffer, Hootsuite, Later, IFTTT, Zapier等）の特徴・料金・事例
   - YouTube→他SNS自動展開の成功事例（2-3件）

2. Instagram/Pinterest/X教育系コンテンツ市場動向
   - 2024-2026年の市場トレンド
   - 教育系・AI×金融ジャンルのエンゲージメント率
   - プラットフォーム別アルゴリズムのポイント

3. YouTube→多チャネル横展開で成功した具体的事例
   - 人物名・企業名が必須
   - フォロワー数・成長率
   - 使用ツール・投資額

4. ターゲット層インサイト（25-45歳、IT高リテラシー、金融・自動化興味）
   - 主要SNS利用率・時間帯
   - コンテンツ形式への好み
   - 信頼できるコンテンツソース

5. プラットフォーム別最適コンテンツ戦略
   - Instagram Reels vs ストーリーズ vs 投稿
   - Pinterest SEO＋オーガニック戦略
   - X リアルタイム性の活用

6. ¥0予算・API統合成功事例
   - 無料ツール・DIY自動化の実例
   - 技術スタック（Python/Node.js等）
   - メリット・デメリット

7. 時差投稿戦略の効果データ
   - 複数時間帯での投稿効果（%数値化）
   - グローバル対応戦略
   - スケジューリングツール精度

=== 出力要件 ===
- 各項目ごとに最低2-3つの具体的な事実を提示
- 推測は必ず [推測] と明記
- 信頼度を高/中/低で記載
- 可能な限りデータ・数値を含める

=== 形式 ===
JSON形式で以下の構造で出力してください：
{
  "findings": [
    {
      "category": "カテゴリ番号と名前",
      "item_number": 1,
      "fact": "具体的な事実",
      "details": "詳細情報",
      "source_hint": "情報源（記事名・企業名等）",
      "confidence": "高/中/低",
      "is_guess": false または [推測] と記載した内容の場合 true
    }
  ],
  "success_cases": [
    {
      "name": "人物・企業名",
      "description": "概要",
      "channels": ["YouTube", "Instagram", "Pinterest"],
      "key_metrics": {"followers": "フォロワー数", "growth_rate": "成長率"},
      "tools_used": ["ツール1", "ツール2"],
      "investment": "投資額（¥0含む）",
      "key_success_factors": ["要因1", "要因2"]
    }
  ],
  "platform_strategies": {
    "instagram": {...},
    "pinterest": {...},
    "x": {...}
  },
  "key_insights": [
    "重要な洞察1",
    "重要な洞察2",
    "[推測] 今後の予想"
  ]
}
"""

def run_research():
    print("=" * 70)
    print("  マルチチャネルSNS自動展開 — 市場調査実行")
    print("  実行: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("=" * 70)
    print()

    print("[1/2] Groq API に市場調査リクエスト中...")

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "あなたは業界専門の市場リサーチャー兼ビジネスアナリストです。最新の市場情報・トレンド・成功事例に精通しており、具体的で信頼性の高い分析を提供します。数値・統計・実例に基づいた回答を心がけます。"
                },
                {
                    "role": "user",
                    "content": RESEARCH_PROMPT
                }
            ],
            temperature=0.7,
            max_tokens=8000,
        )

        result_text = response.choices[0].message.content
        print("[✓] Groq API レスポンス取得")
        print()

    except Exception as e:
        print(f"[✗] Groq API エラー: {e}")
        return False

    # JSON パース試行
    print("[2/2] JSON パース中...")
    try:
        # JSON ブロック抽出
        json_start = result_text.find('{')
        json_end = result_text.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            json_str = result_text[json_start:json_end]
            data = json.loads(json_str)
            print("[✓] JSON パース成功")
        else:
            print("[!] JSON ブロックが見つかりません。raw_output として保存します")
            data = {"raw_content": result_text}
    except json.JSONDecodeError as e:
        print(f"[!] JSON パースエラー: {e}。raw_output として保存します")
        data = {"raw_content": result_text, "parse_error": str(e)}

    # メタデータ追加
    data["_meta"] = {
        "topic": "マルチチャネルSNS自動展開システムの市場調査",
        "provider": "groq",
        "model": "llama-3.3-70b-versatile",
        "generated": datetime.now().isoformat(),
        "generator": "market_research_direct"
    }

    # 出力
    output_dir = Path(__file__).parent

    # report.json
    report_path = output_dir / "report.json"
    report_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[✓] report.json 保存 → {report_path}")

    # raw_output.txt
    raw_path = output_dir / "raw_output.txt"
    raw_path.write_text(result_text, encoding="utf-8")
    print(f"[✓] raw_output.txt 保存 → {raw_path}")

    print()
    print("=" * 70)
    print("  完了！")
    print("=" * 70)
    return True

if __name__ == "__main__":
    success = run_research()
    exit(0 if success else 1)
