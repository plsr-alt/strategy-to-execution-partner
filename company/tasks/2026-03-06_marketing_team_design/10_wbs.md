# WBS — 恋愛改善設計士 マーケティングチーム設計
**作成日**: 2026-03-06
**担当部長**: 戦略部長（Claude Sonnet）
**complexity**: heavy（6ワーカー体制）
**execution_mode**: hybrid

---

## タスク概要

「恋愛改善設計士」ブランドの専用マーケティングチームを設計する。
背景資料9ファイルを全て読み込み、1人運営・週5-7時間・月予算0円という制約下で
持続可能かつ収益化可能なマーケティング組織設計を行う。

---

## 戦略部の判断メモ

### 読み込み済み背景資料サマリー
- **ブランド軸**: 「構造」×「改善」×「煽らない」の希少ポジション。恋愛市場の感情煽りが嫌いな30-40代男性に直撃する
- **ファネル設計済み**: X→note→診断→DM→セッションの導線が既に整備されている
- **KPI基準明確**: note3本=勝ち。撤退基準も数値化済み
- **ツール強み**: CrewAI/Groq/xrs等のAI自動化アセットが既にある。YouTube自動化パイプラインも稼働中
- **弱点**: ゼロフォロワー・顔出し不可・限られた時間。実績なしからの信頼構築が最大課題

### execution_mode = hybrid の理由
- researcher（外部）: 競合分析・市場調査・参考事例収集はWeb検索を伴うため CrewAI へ委譲
- extractor〜editor（内部）: 上記資料9本の既知情報 + researcher出力を組み合わせて内部ワーカーで仕上げる

---

## ワーカー構成（6名体制）

| Order | Worker | Execution | タスク概要 |
|-------|--------|-----------|-----------|
| 1 | worker-researcher | **external (CrewAI)** | 恋愛コンサル市場の競合分析・参考事例・インサイト調査 |
| 2 | worker-extractor | internal | 背景資料9本から重要情報を抽出・整理 |
| 3 | worker-structurer | internal | 抽出情報と調査結果を7セクション構造に整理 |
| 4 | worker-drafter | internal | 7セクション全文ドラフト生成（Groq委譲） |
| 5 | worker-critic | internal | ドラフトの批評・欠落チェック・制約適合性検証 |
| 6 | worker-editor | internal | 最終品質チェック・文体統一・最終成果物生成 |

---

## WBSフロー

```
[外部] worker-researcher (CrewAI)
    → 競合・市場・参考事例・インサイト調査
    → 出力: 01_research.md

[内部] worker-extractor
    → 背景資料9本 + research結果から情報抽出
    → 出力: 02_extract.md

[内部] worker-structurer
    → 7セクション構造への整理・マッピング
    → 出力: 03_structure.md

[内部] worker-drafter
    → 7セクション完全ドラフト（3000字超 → Groq委譲）
    → 出力: 04_draft.md

[内部] worker-critic
    → 批評・欠落・矛盾・制約適合性チェック
    → 出力: 05_critic.md

[内部] worker-editor
    → 最終編集・品質確保・成果物生成
    → 出力: 06_final.md
    → 最終コピー先: 03_PROJECTS/love_improvement_designer/12_marketing_team_design.md
```

---

## 各ワーカー詳細指示

### Order 1: worker-researcher（external / CrewAI）

**タスク**: 恋愛コンサル・恋愛改善市場の競合分析・参考人物・インサイト調査

**調査テーマ**:
1. X（旧Twitter）での恋愛アドバイス系アカウントの代表的存在（煽り系・非煽り系それぞれ）
2. note恋愛記事の市場規模感・購買動向
3. 30-40代男性向け恋愛改善系コンテンツの市場ポジショニング
4. 参考にすべき個人・企業（ブランディング・マーケ手法が優れているもの）
5. 「構造的・論理的アプローチ」で恋愛コンテンツを出している類似事例

**外部委譲先**: CrewAI + Groq
**外部指示書**: `company/tasks/2026-03-06_marketing_team_design/15_external_instructions/crewai_command.sh`
**出力**: `company/tasks/2026-03-06_marketing_team_design/20_worker_outputs/01_research.md`

---

### Order 2: worker-extractor（internal）

**タスク**: 背景資料9本からマーケティングチーム設計に必要な情報を構造的に抽出

**抽出対象**:
- ブランド定義（タグライン・バイオ・差別化軸・トーン）
- ターゲットペルソナの詳細（心理・行動・痛点）
- ファネルの各ステップと役割
- KPI・撤退基準・改善レバー
- 既存コンテンツ資産（X投稿10本・固定ポスト・noteコンテンツ）
- ローンチ週間で実証されたオペレーション知見
- 使用ツール・自動化アセット
- 制約条件の整理（時間・予算・顔出し不可）

**入力ファイル**: 背景資料9本 + 01_research.md
**出力**: `company/tasks/2026-03-06_marketing_team_design/20_worker_outputs/02_extract.md`

---

### Order 3: worker-structurer（internal）

**タスク**: 抽出情報を7セクション構造にマッピング・骨格設計

**構造化対象**:
1. 全体設計（思想・勝ち筋・避けるべき戦い方）の論点整理
2. 組織図の役割リスト・依存関係・兼務可能性の設計
3. 各担当詳細の項目テーブル設計（必須要件11項目との対応付け）
4. メディア別戦略のフレームワーク（X・note・将来的YouTube等）
5. コンテンツ変換フローの図解設計（テキスト→他メディア変換ルート）
6. 30日・90日実行計画のタイムライン設計
7. レビュー体制の設計（週次・月次チェックポイント）

**入力ファイル**: 02_extract.md
**出力**: `company/tasks/2026-03-06_marketing_team_design/20_worker_outputs/03_structure.md`

---

### Order 4: worker-drafter（internal / Groq委譲）

**タスク**: 構造骨格を基に7セクション全文ドラフト生成（3000字超）

**ドラフト要件**:
- 必須要件11項目を全てカバー
- 7セクション全て記述
- 各担当ロールは「役職名・目的・主な責任・KPI・連携・週次業務・成果物」形式
- 1人運営・週5-7時間制約を前提とした現実的な設計
- 参考にしたい個人・企業名を具体的に記載
- 「全否定部隊」（デビルズアドボケート役）の役割を明確化

**入力ファイル**: 03_structure.md（＋ 02_extract.md 参照可）
**出力**: `company/tasks/2026-03-06_marketing_team_design/20_worker_outputs/04_draft.md`

---

### Order 5: worker-critic（internal）

**タスク**: ドラフトの批評・欠落チェック・制約適合性検証

**批評観点**:
1. 7セクション全て記述されているか
2. 必須要件11項目が全てカバーされているか
3. 1人運営・週5-7時間の制約に対して実行可能か（負荷過多でないか）
4. KPIが測定可能か・撤退基準と整合しているか
5. 「煽らない・女性否定しない」というブランドポリシーに反する表現がないか
6. 月予算0円制約に反する施策が含まれていないか
7. 「全否定部隊」が機能する設計になっているか
8. コンテンツ変換フローの現実性

**入力ファイル**: 04_draft.md
**出力**: `company/tasks/2026-03-06_marketing_team_design/20_worker_outputs/05_critic.md`

---

### Order 6: worker-editor（internal）

**タスク**: 批評を反映した最終編集・品質確保・最終成果物生成

**編集基準**:
- criticの指摘を全て反映
- 文体統一（ですます調、専門的だが読みやすく）
- 表・組織図はMarkdownテーブル形式
- 冒頭にエグゼクティブサマリー（全体像を3段落で）
- 「70点の成果物」+「改善ポイント記載」で完成
- 最終アウトプットは `03_PROJECTS/love_improvement_designer/12_marketing_team_design.md` にも保存指示を記載

**入力ファイル**: 04_draft.md + 05_critic.md
**出力**: `company/tasks/2026-03-06_marketing_team_design/20_worker_outputs/06_final.md`
**最終コピー先**: `03_PROJECTS/love_improvement_designer/12_marketing_team_design.md`

---

## 統合計画（merge_plan）

1. `01_research.md`（CrewAI出力）+ `02_extract.md`（既存資料抽出）= 情報基盤
2. `03_structure.md` = 設計骨格
3. `04_draft.md` = 第一草稿（3000字超）
4. `05_critic.md` = 批評・改善点
5. `06_final.md` = 完成版（7セクション・必須要件11項目完全カバー）
6. `06_final.md` の内容を `03_PROJECTS/love_improvement_designer/12_marketing_team_design.md` に配置

戦略部統合時のチェック項目:
- エグゼクティブサマリー存在確認
- 7セクション全記述確認
- 必須要件11項目のカバレッジ確認
- 制約条件（時間・予算・顔出し）との整合性確認
- KPI・撤退基準との接続確認

---

## ファイル構成

```
company/tasks/2026-03-06_marketing_team_design/
├── 00_request.md
├── 10_wbs.md                    ← このファイル
├── 15_external_instructions/
│   └── crewai_command.sh        ← CrewAI実行指示書
├── 20_worker_outputs/
│   ├── 01_research.md           ← worker-researcher (CrewAI出力)
│   ├── 02_extract.md            ← worker-extractor
│   ├── 03_structure.md          ← worker-structurer
│   ├── 04_draft.md              ← worker-drafter
│   ├── 05_critic.md             ← worker-critic
│   └── 06_final.md              ← worker-editor（完成版）
└── 80_manager_output.md         ← 戦略部長 統合アウトプット（モード2で生成）
```

---

## 最終成果物

`03_PROJECTS/love_improvement_designer/12_marketing_team_design.md`
