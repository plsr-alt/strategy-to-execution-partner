# Routing Rules

## キーワード → 部門マッピング

| Keywords | Department | Manager Agent |
|---------|-----------|---------------|
| 提案, 見積, 商談, 営業, クライアント, 価格, 契約, proposal, quote, deal | sales | sales-manager |
| 記事, 投稿, ブログ, SNS, X, Twitter, コンテンツ, コピー, ライティング, post, content | content | content-manager |
| 議事録, 報告書, 請求, 会議, 社内, コンプライアンス, 業務改善, minutes, report | backoffice | backoffice-manager |
| 市場, 調査, 競合, 分析, 戦略, リサーチ, トレンド, research, strategy, market | strategy | strategy-manager |
| コード, スクリプト, 自動化, API, ビルド, デプロイ, 開発, 実装, code, dev, build | dev | dev-manager |

## 曖昧時のルール
1. 複数部門にマッチ → キーワードヒット数が最多の部門
2. 同数 → strategy（戦略部が再ルーティング可能）
3. どこにもマッチしない → ユーザーに確認を求める

## 複合案件
- 「市場調査して提案書を作る」→ strategy（調査）→ sales（提案書）の2段階
- CEOが `rerun_policy` で2段階目を指示する

---

## 外部委譲ルール

重い処理は外部LLM（CrewAI / Groq / Ollama）に委譲する。
詳細は `company/external_tools.md` を参照。

### 外部委譲キーワード
| Keywords | 外部ツール | execution_mode |
|---------|-----------|---------------|
| 市場調査, 競合調査, 大規模リサーチ | CrewAI + Groq | external |
| 長文, 3000字, 記事作成, 大量生成, バッチ | Groq API | external |
| コード実装, スクリプト, 50行, 複数ファイル, リファクタ | Groq / WSL | external |
| 調査して→まとめる, 調査して→提案書 | CrewAI（調査）+ 内部（仕上げ） | hybrid |

### 判定フロー
1. CEOがルーティング時に `execution_mode` を判定
2. `external` / `hybrid` の場合、部長が `company/external_tools.md` の手順に従い外部実行指示書を出力
3. 外部処理の結果を受け取った後、内部ワーカーで品質仕上げ（hybrid時）
