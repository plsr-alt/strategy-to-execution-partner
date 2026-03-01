# 参謀標準手順 — 市場調査 PLAYBOOK

## 概要

市場調査は **CrewAI に完全委譲**する。人間はテーマを渡すだけ。
Claude Code が report.json を受け取り PPT / Markdown を生成する。

---

## 実行フロー

```
1. run.sh を叩く
      ↓
2. CrewAI が順番に実行
   [Researcher] Web 検索で一次情報・URL 収集
      ↓
   [Analyst]  市場規模・プレイヤー・トレンド・示唆を構造化分析
      ↓
   [Writer]   JSON スキーマに従って report.json を生成
      ↓
3. Claude Code が report.json を読んで PPT / Markdown を生成
```

---

## コマンド例（WSL ターミナルで実行）

```bash
cd /mnt/c/Users/tshibasaki/Desktop/etc/work/task/04_RESEARCH/agents/market_research_crewai
source /home/crewai/.venv/bin/activate

# ── Groq で実行（無料・おすすめ） ──
python run.py \
    --topic "日本のSaaS市場調査 2025" \
    --outdir "/mnt/c/Users/tshibasaki/Desktop/etc/work/task/05_CONTENT/drafts/saas_market_2025" \
    --provider groq

# ── OpenAI で実行（有料 / 高精度） ──
python run.py \
    --topic "日本のクラウドストレージ市場" \
    --outdir "/mnt/c/Users/tshibasaki/Desktop/etc/work/task/05_CONTENT/drafts/cloud_storage" \
    --provider openai --model gpt-4o-mini

# ── Ollama で実行（完全無料・ローカル） ──
python run.py \
    --topic "日本のECプラットフォーム市場" \
    --outdir "/mnt/c/Users/tshibasaki/Desktop/etc/work/task/05_CONTENT/drafts/ec_platform" \
    --provider ollama --model llama3.2
```

---

## 出力ファイル

| ファイル | 説明 |
|---------|------|
| `report.json` | 構造化調査結果（Claude Code が読む） |
| `raw_output.txt` | CrewAI の生ログ（JSON パース失敗時のデバッグ用） |

---

## report.json スキーマ

```json
{
  "market_definition": "市場の定義",
  "market_size": [
    { "year": 2023, "value": 123, "unit": "億円", "assumption": "...", "source": "URL" }
  ],
  "players": [
    { "tier": "Tier1", "name": "企業名", "description": "特徴", "source": "URL" }
  ],
  "trends": [
    { "trend": "トレンド名", "impact": "事業インパクト", "source": "URL" }
  ],
  "implications": [
    { "message": "ビジネス示唆", "priority": "High/Medium/Low" }
  ],
  "sources": ["URL1", "URL2"],
  "_meta": { "topic": "...", "generated": "ISO8601", "model": "gpt-4o-mini" }
}
```

---

## Claude Code 側の後続処理（report.json 受け取り後）

```
① Read:  05_CONTENT/drafts/<案件名>/report.json
       ↓
② PPT:  python-pptx で市場調査スライドを自動生成
        - 表紙 / 市場定義 / 市場規模グラフ / プレイヤー一覧 / トレンド / 示唆
       ↓
③ MD:   調査サマリーを Markdown で出力 → 04_RESEARCH/ に保存
```

---

## 初回セットアップ（済み）

```bash
# WSL で実行済み（venvはLinuxネイティブ側に配置＝高速）
python3 -m venv /home/crewai/.venv
source /home/crewai/.venv/bin/activate
pip install crewai crewai-tools python-dotenv
```

## 事前設定（実行前に必ず）

### 【無料・★推奨】Groq を使う場合

1. https://console.groq.com → Sign Up（GitHub/Google 認証でOK）
2. API Keys → Create API Key
3. `.env` に貼り付け:
   ```
   GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
4. 実行: `python run.py --topic "..." --outdir "..." --provider groq`

---

### 【完全無料・ローカル】Ollama を使う場合

1. https://ollama.com → Download for Windows インストール
2. WSL または PowerShell で:
   ```bash
   ollama pull llama3.2   # 初回のみ（約2GB）
   # ollama serve は自動起動される
   ```
3. 実行: `python run.py --topic "..." --outdir "..." --provider ollama`

---

### 【有料】OpenAI を使う場合

`.env` に API キーを設定する:
```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_MODEL_NAME=gpt-4o-mini   # コスト重視
# OPENAI_MODEL_NAME=gpt-4o      # 精度重視
```

---

## コスト目安

| プロバイダ | モデル | 1回の調査コスト目安 |
|----------|--------|------------------|
| Groq | llama-3.3-70b-versatile | **$0（無料枠）** |
| Ollama | llama3.2 | **$0（ローカル）** |
| OpenAI | gpt-4o-mini | $0.05〜0.15 |
| OpenAI | gpt-4o | $0.50〜1.50 |

---

## ファイル配置

```
04_RESEARCH/agents/market_research_crewai/
├── crew.py          ← Agent / Task / Crew 定義
├── run.py           ← CLI エントリーポイント
├── run.sh           ← WSL 実行シェルスクリプト
├── requirements.txt
├── .env             ← API キー（Git 管理外）
├── .venv/           ← Python 仮想環境（WSL）
├── outputs/         ← 一時出力（自動クリア可）
└── prompts/         ← プロンプトカスタマイズ参考
```

---

## トラブルシューティング

| 症状 | 対処 |
|------|------|
| `JSONが見つかりません` | `raw_output.txt` を確認 → Writer に JSON のみ出力するよう再実行 |
| `OPENAI_API_KEY not set` | `.env` の API キーを確認 |
| `ModuleNotFoundError: crewai` | `source .venv/bin/activate` を忘れていないか確認 |
| venv が壊れた | `.venv/` を削除して再度 `python3 -m venv .venv && pip install -r requirements.txt` |
