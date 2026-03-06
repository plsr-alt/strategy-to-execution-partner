# パイプライン実行手順

## 前提
- WSL + Groq (or Ollama) を使用（Claudeトークン節約）
- Claude Code は指示・レビュー・最終判断に集中

---

## Step 1: ソース取得（fetch）

### Claude Code の作業
1. 対象ドキュメントのURL一覧を決定
2. 以下のいずれかで取得:
   - `curl` / `wget` で直接取得
   - Webスクレイピングスクリプトで取得
3. `sources/` に保存（1ファイル = 1ページ）

### 命名規則
```
sources/
├── 001_overview.md
├── 002_configuration.md
├── 003_tools.md
└── ...
```

---

## Step 2: 執筆＋検証ループ（WSL+Groq）

### 実行方法
```bash
# WSLで実行
cd /mnt/c/Users/tshibasaki/Desktop/etc/work/task/03_PROJECTS/agent_factory

# セクションごとにwriter→checker
# ※ 具体的なスクリプトは pipeline/scripts/ に配置
python pipeline/scripts/write_and_verify.py \
    --sources sources/ \
    --section 1 \
    --output digest/guide_draft.md \
    --provider groq
```

### 手動実行の場合（Groq Playground等）
1. `section_writer.md` のプロンプトにsources/の内容を貼り付け
2. 出力を取得
3. `fact_checker.md` のプロンプトに出力 + sources/ を貼り付け
4. PASS → 次セクション / FAIL → 修正して再投入（上限3回）
5. 上限超え → `⚠️検証未通過` タグを付けて先に進む

---

## Step 3: 統合＋圧縮

### 設計ガイド統合
```
digest/guide_draft.md → digest/guide_final.md
```

### 知識圧縮（6,600行 → 数百行）
```
digest/guide_final.md → digest/compressed_knowledge.md
```

圧縮ルール:
- 構造（章立て）は維持
- 各節を1-3行のエッセンスに凝縮
- タグ付き箇所はタグごと残す
- コード例は最も代表的な1つだけ残す

---

## Step 4: ジェネレーター実行

1. `pipeline/generator_prompt.md` に圧縮知識を埋め込む
2. ドメイン要件を入力
3. Phase A→D を実行
4. 出力を `system/<domain>/` に保存

---

## 品質ゲート

| ステップ | ゲート | 担当 |
|---------|-------|------|
| Step 2 | fact-checker PASS | WSL+Groq |
| Step 3 | Claude Code が圧縮結果をスポットチェック | Claude Code |
| Step 4 | Claude Code が生成物をレビュー | Claude Code |

---

## トラブルシューティング

| 症状 | 対処 |
|------|------|
| fact-checker が3回連続FAIL | `⚠️検証未通過` タグで先に進む。後でユーザー判断 |
| sources/ が不足 | 追加ドキュメントをfetch → sources/ に追加 |
| 圧縮で情報が落ちすぎ | 圧縮率を下げる（1節3行→5行） |
| 生成物の品質が低い | digest の圧縮知識を見直し → 再生成 |
