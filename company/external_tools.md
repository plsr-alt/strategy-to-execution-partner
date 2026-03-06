# 外部実行リソース（External Tools）

## 概要

仮想AI企業の一部として、**重い処理**は外部LLM（CrewAI / Groq / Ollama）に委譲する。
部長（Manager）が WBS 分解時に「このタスクは外部委譲すべき」と判定し、
内部ワーカー（Haiku）の代わりに **外部実行指示書** を出力する。

---

## 外部委譲の判定基準

| 条件 | 外部委譲する | 内部ワーカーで実行 |
|------|------------|------------------|
| 大規模な市場調査（Web検索＋分析＋構造化） | ✅ CrewAI | |
| 長文コンテンツ生成（3000字超） | ✅ Groq | |
| コード実装（50行超 or 複数ファイル） | ✅ Groq/WSL | |
| バッチ処理・大量生成（10件超） | ✅ Groq/WSL | |
| 短い調査・要約・レビュー | | ✅ worker-researcher |
| テンプレート埋め・軽い編集 | | ✅ worker-drafter/editor |
| 品質チェック・構造化 | | ✅ worker-critic/structurer |

---

## 外部ツール一覧

### 1. CrewAI（市場調査特化）

**用途**: Web検索を伴う大規模な市場調査・競合分析
**実行環境**: WSL

```bash
cd /mnt/c/Users/tshibasaki/Desktop/etc/work/task/04_RESEARCH/agents/market_research_crewai
source /home/crewai/.venv/bin/activate

# Groq（無料・推奨）
python run.py \
    --topic "<調査テーマ>" \
    --outdir "/mnt/c/Users/tshibasaki/Desktop/etc/work/task/05_CONTENT/drafts/<slug>" \
    --provider groq

# Ollama（完全無料・ローカル）
python run.py \
    --topic "<調査テーマ>" \
    --outdir "/mnt/c/Users/tshibasaki/Desktop/etc/work/task/05_CONTENT/drafts/<slug>" \
    --provider ollama --model llama3.2

# OpenAI（有料・高精度）
python run.py \
    --topic "<調査テーマ>" \
    --outdir "/mnt/c/Users/tshibasaki/Desktop/etc/work/task/05_CONTENT/drafts/<slug>" \
    --provider openai --model gpt-4o-mini
```

**出力**: `report.json`（構造化調査結果）+ `raw_output.txt`（生ログ）

**report.json スキーマ**:
```json
{
  "market_definition": "市場の定義",
  "market_size": [{ "year": 2023, "value": 123, "unit": "億円", "source": "URL" }],
  "players": [{ "tier": "Tier1", "name": "企業名", "description": "特徴", "source": "URL" }],
  "trends": [{ "trend": "名前", "impact": "事業インパクト", "source": "URL" }],
  "implications": [{ "message": "ビジネス示唆", "priority": "High/Medium/Low" }],
  "sources": ["URL1", "URL2"]
}
```

**後続処理（Claude Code）**:
1. `report.json` を Read
2. python-pptx でスライド自動生成（必要時）
3. Markdown サマリーを `04_RESEARCH/` に保存

---

### 2. Groq API（長文生成・コード実装）

**用途**: 長文コンテンツ生成、コード実装、バッチ処理
**実行環境**: WSL
**モデル**: `llama-3.3-70b-versatile`（無料枠）

```bash
# WSLで直接Groq APIを叩く例
source /home/crewai/.venv/bin/activate
python -c "
from groq import Groq
client = Groq()
response = client.chat.completions.create(
    model='llama-3.3-70b-versatile',
    messages=[{'role': 'user', 'content': '<プロンプト>'}]
)
print(response.choices[0].message.content)
"
```

---

### 3. Ollama（完全ローカル・無料）

**用途**: Groqと同様だが完全オフライン
**実行環境**: WSL or Windows
**モデル**: `llama3.2`

```bash
ollama run llama3.2 "<プロンプト>"
```

---

## コスト目安

| ツール | モデル | コスト |
|--------|--------|--------|
| CrewAI + Groq | llama-3.3-70b-versatile | **$0（無料枠）** |
| CrewAI + Ollama | llama3.2 | **$0（ローカル）** |
| CrewAI + OpenAI | gpt-4o-mini | $0.05〜0.15/回 |
| Groq API 直接 | llama-3.3-70b-versatile | **$0（無料枠）** |

---

## 外部委譲時のファイル配置

外部委譲タスクも `company/tasks/` 配下の同じディレクトリ構成に従う。

```
company/tasks/YYYY-MM-DD_<slug>/
├── 00_request.md              ← CEO/部長が作成
├── 10_wbs.md                  ← 部長が作成（外部委譲フラグ付き）
├── 15_external_instructions/  ← 外部委譲指示書（部長が作成）
│   ├── crewai_command.sh      ← CrewAI実行コマンド
│   └── groq_prompt.md         ← Groq用プロンプト
├── 20_worker_outputs/         ← 内部ワーカー出力 + 外部出力(report.json等)
├── 80_manager_output.md       ← 部長が統合
└── 90_ceo_review.md           ← CEO レビュー（standard/heavy時）
```

---

## トラブルシューティング

| 症状 | 対処 |
|------|------|
| `JSONが見つかりません` | `raw_output.txt` を確認 → Writer に JSON のみ出力するよう再実行 |
| `GROQ_API_KEY not set` | `.env` の API キーを確認 |
| `ModuleNotFoundError: crewai` | `source .venv/bin/activate` を忘れていないか確認 |
| venv が壊れた | `.venv/` 削除 → `python3 -m venv .venv && pip install -r requirements.txt` |
| WSL パス問題 | 必ず `/mnt/c/...` 形式を使う（`C:\...` は不可） |
