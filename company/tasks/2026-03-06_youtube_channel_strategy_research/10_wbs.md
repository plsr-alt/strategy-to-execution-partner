# WBS: YouTube自動化チャンネル戦略調査

## タスク情報
- 作成日: 2026-03-06
- 担当マネージャー: strategy-manager
- Complexity: high（6ワーカーフル）
- 参照リクエスト: 00_request.md

---

## WBSフロー

```
researcher-01 → extractor-01 → structurer-01 → drafter-01 → critic-01 → editor-01
```

### ワーカー1: strategy-researcher-01
- **担当**: トレンド分析・ジャンル候補の網羅的収集・形式比較・収益性・リスクの一次情報収集
- **入力**: 00_request.md
- **出力**: 20_worker_outputs/01_research.md

### ワーカー2: strategy-extractor-01
- **担当**: リサーチ結果からキーインサイト抽出（CPM相場・BAN事例・自動化成功パターン）
- **入力**: 00_request.md, 20_worker_outputs/01_research.md
- **出力**: 20_worker_outputs/02_insights.md

### ワーカー3: strategy-structurer-01
- **担当**: ジャンル×形式の全組み合わせをフレームワーク（スコアリングマトリクス）で構造化
- **入力**: 20_worker_outputs/01_research.md, 20_worker_outputs/02_insights.md
- **出力**: 20_worker_outputs/03_structured.md

### ワーカー4: strategy-drafter-01
- **担当**: 7章構成レポート初稿作成（第1-7章すべて）
- **入力**: 20_worker_outputs/01_research.md, 20_worker_outputs/02_insights.md, 20_worker_outputs/03_structured.md
- **出力**: 20_worker_outputs/04_draft.md

### ワーカー5: strategy-critic-01
- **担当**: 初稿レビュー（根拠の明示、優先順位の明確さ、BANリスク保守評価の確認）
- **入力**: 00_request.md, 20_worker_outputs/04_draft.md
- **出力**: 20_worker_outputs/05_review.md

### ワーカー6: strategy-editor-01
- **担当**: レビュー反映・最終版完成（80_manager_output.md生成）
- **入力**: 20_worker_outputs/04_draft.md, 20_worker_outputs/05_review.md
- **出力**: 20_worker_outputs/06_final.md

---

## マージ計画
1. editor-01 の 06_final.md を 80_manager_output.md としてコピー
2. エグゼクティブサマリーを冒頭に追加
3. 「70点の成果物」+「残り30点の改善ポイント」セクションを末尾に追加

## 最終出力ファイル
`company/tasks/2026-03-06_youtube_channel_strategy_research/80_manager_output.md`
