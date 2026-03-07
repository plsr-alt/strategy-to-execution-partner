# WBS — マルチチャネルSNS市場調査

## タスク分解

### Phase 1: 外部委譲（CrewAI + Groq）
**スコープ**: 大規模Web検索・市場分析・事例抽出

- Task 1.1: YouTube→SNS自動展開ツール競合調査
  - 対象: Buffer, Hootsuite, Later, IFTTT, Zapier等の事例
  - 検索キーワード: "YouTube to Instagram Pinterest X reposting", "social media automation tools 2026", "cross-platform posting"

- Task 1.2: 教育系・金融系コンテンツの市場トレンド調査
  - 対象: Instagram, Pinterest, X での教育系・AI×金融ジャンルのトレンド
  - 検索キーワード: "financial education content Instagram 2026", "personal finance Pinterest strategy", "AI finance creators"

- Task 1.3: 成功事例人物・企業の特定
  - 対象: YouTube→多チャネル展開で成功した具体的クリエイター・ブランド
  - 検索キーワード: "YouTuber multi-channel growth case study", "content repurposing success stories", "financial creator strategy"

- Task 1.4: ターゲット層インサイト調査
  - 対象: 25-45歳, IT高リテラシー層, 金融・自動化興味層の行動
  - 検索キーワード: "financial education audience demographics", "personal finance content consumption", "automation enthusiasts"

- Task 1.5: プラットフォーム別最適コンテンツ戦略
  - 対象: Instagram vs Pinterest vs X の独自アルゴリズム・ベストプラクティス
  - 検索キーワード: "Instagram Reels algorithm 2026", "Pinterest SEO strategy", "X/Twitter content strategy 2026"

- Task 1.6: ¥0予算・API統合成功事例
  - 対象: 無料ツール・DIY自動化の実践例
  - 検索キーワード: "free social media automation API", "DIY cross-posting Python", "no-code automation examples"

- Task 1.7: 時差投稿効果データ
  - 対象: 複数時間帯・時間差での投稿効果に関する数値データ
  - 検索キーワード: "social media scheduling time zone effectiveness", "posting time analysis 2026"

### Phase 2: 内部ワーカー（構造化・品質チェック）
**スコープ**: CrewAI出力の構造化・整理・レビュー

- Task 2.1: 外部出力の品質確認 (worker-critic)
- Task 2.2: 表形式で発見事項を構造化 (worker-structurer)
- Task 2.3: 信頼度・推測タグの付与 (worker-editor)
- Task 2.4: 最終レポート生成 (worker-drafter)

### Phase 3: 統合・レビュー
- Task 3.1: マネージャー統合
- Task 3.2: CEO最終レビュー

## execution_mode
**external** — CrewAI + Groq で全面委譲

## スケジュール
- 2026-03-08 09:00 — CrewAI実行
- 2026-03-08 10:00 — 内部処理（構造化・品質チェック）
- 2026-03-08 11:00 — CEO レビュー
- 2026-03-08 12:00 — 納品
