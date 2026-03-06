# AI会社スターターキット

Claude Codeの Agents + Skills だけで動く「AI会社」。外部APIなし。

## 思想
- **CEO（opus）**: ルーティング・複雑度判定・品質ゲート・差し戻しのみ。作業禁止。
- **部長5名（sonnet）**: WBS分解と統合のみ。作業禁止。
- **社員6名（haiku）**: 汎用ロール。固定フォーマット出力。部門知識は部長の指示で注入。
- **会話ログに依存しない**: `company/` 配下の共有ファイルが組織のDNA・品質基準・テンプレ。
- **トークン自動調整**: CEOが依頼の複雑度を判定し、ワーカー数を自動で3〜6個に調整。

## 複雑度自動調整（complexity）

| complexity | ワーカー数 | パターン | CEOレビュー |
|-----------|----------|---------|------------|
| **light** | 3 | researcher → drafter → editor | スキップ |
| **standard** | 4〜5 | researcher → structurer → drafter → critic → editor | あり |
| **heavy** | 6 | researcher → extractor → structurer → drafter → critic → editor | あり |

CEOが依頼内容から自動判定。SNS投稿 → light、提案書 → standard、戦略策定 → heavy。

## コマンド一覧

| コマンド | 説明 | 例 |
|---------|------|---|
| `/work <依頼>` | フルフロー（CEO→部長→社員→統合→レビュー） | `/work 新規顧客への提案書作成` |
| `/dna <修正>` | 会社DNA（価値観）に追記 | `/dna 顧客第一主義を追加` |
| `/sales <依頼>` | 営業部に直接依頼（CEOスキップ） | `/sales 商談準備資料を作って` |
| `/content <依頼>` | コンテンツ部に直接依頼 | `/content Xで告知投稿を作成` |
| `/backoffice <依頼>` | バックオフィス部に直接依頼 | `/backoffice 議事録テンプレ作成` |
| `/strategy <依頼>` | 戦略部に直接依頼 | `/strategy SaaS市場を調査` |
| `/dev <依頼>` | 開発部に直接依頼 | `/dev 自動化スクリプト作成` |

## ディレクトリ構成

```
task/
├── .claude/
│   ├── agents/              # エージェント定義（12ファイル）
│   │   ├── ceo.md           # CEO（opus）
│   │   ├── *-manager.md     # 部長5名（sonnet）
│   │   └── worker-*.md      # 汎用社員6名（haiku）
│   └── skills/              # コマンド定義（7ディレクトリ）
│       ├── work/SKILL.md
│       ├── dna/SKILL.md
│       └── {dept}/SKILL.md  # sales, content, backoffice, strategy, dev
├── company/
│   ├── DNA.md               # 会社のミッション・価値観
│   ├── routing_rules.md     # 部門ルーティングルール
│   ├── quality_bars.md      # 品質基準
│   ├── templates/           # 成果物テンプレート
│   └── tasks/               # 案件フォルダ（自動生成）
└── README_AI_COMPANY.md     # このファイル
```

## 組織図

| 階層 | モデル | 人数 | 責務 |
|------|--------|------|------|
| CEO | opus | 1 | ルーティング・複雑度判定・品質ゲート |
| 部長 | sonnet | 5 | WBS分解・部門文脈注入・統合 |
| 社員 | haiku | 6（汎用） | 実作業（固定フォーマット） |

### 汎用ワーカー（6ロール）
| ロール | エージェント名 | 責務 |
|--------|--------------|------|
| researcher | worker-researcher | 情報収集・調査 |
| extractor | worker-extractor | データ抽出・構造化 |
| structurer | worker-structurer | フレームワーク整理 |
| drafter | worker-drafter | 初稿作成 |
| critic | worker-critic | 品質レビュー |
| editor | worker-editor | 最終版仕上げ |

部門の専門知識は**部長がinstructionsで注入**する（営業視点、技術視点など）。

## カスタマイズ方法

### 会社の方針を変える
```
/dna 品質よりスピードを重視する方針に変更
```

### 品質基準を調整
`company/quality_bars.md` を直接編集。

### ルーティングルールを変更
`company/routing_rules.md` のキーワードマッピングを編集。

## トラブルシュート

| 症状 | 対策 |
|------|------|
| 重い・遅い | `/sales` 等の部門直接コマンドを使う（CEO省略） |
| まだ重い | `company/DNA.md` に「complexity: lightをデフォルトにする」と追記 |
| 成果物がブレる | `/dna` で方針追記 or `quality_bars.md` を厳しくする |
| 差し戻したい | `/work` FAIL時はCEOが指示。手動なら部門コマンド再実行 |
