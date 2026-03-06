# WBS: YouTube自動化パイプライン 全面品質改善

## メタ情報
- **task_dir**: `company/tasks/2026-03-07_youtube_pipeline_quality_improvement/`
- **complexity**: heavy
- **execution_mode**: hybrid
- **作成日**: 2026-03-07
- **担当部長**: strategy-manager

---

## 対応するユーザーフィードバック（全6項目 — 全worker共通文脈）

| # | フィードバック | 対応worker |
|---|--------------|-----------|
| 1 | 音声が遅い・AI臭い（gTTS） | researcher / extractor / drafter / critic |
| 2 | 映像と内容がマッチしていない | researcher / extractor / drafter / critic |
| 3 | 動画の長さがまちまち（最低20分以上に統一） | drafter / critic |
| 4 | サムネイルが機能していない（PIL生成） | researcher / extractor / drafter / critic |
| 5 | チャンネルアイコンが初期値 | drafter / critic |
| 6 | チャンネル名がデフォルト | drafter / critic |

---

## 技術的制約（全worker共通）
- EC2 t4g.medium: ARM/Graviton, 2vCPU, 4GB RAM
- Python 3.9 / moviepy / PIL / Groq API / Pexels API / gTTS
- 予算: 無料〜低コストAPIのみ（ElevenLabs未取得）
- YouTube Data API v3

---

## WBSフロー（heavy: 6ワーカー）

```
[外部] worker-researcher (CrewAI)
        ↓ 01_research_raw.json / 01_competitor_analysis.md
[内部] worker-extractor
        ↓ 02_extracted_elements.md
[内部] worker-structurer
        ↓ 03_structure_plan.md
[内部] worker-drafter
        ↓ 04_draft_all.md（4成果物ドラフト）
[内部] worker-critic
        ↓ 05_review.md
[内部] worker-editor
        ↓ 06_final.md + 4成果物ファイル（個別）
[部長統合]
        ↓ 80_manager_output.md
```

---

## employee_jobs

```json
[
  {
    "step": 1,
    "worker_agent": "worker-researcher",
    "execution": "external",
    "external_tool": "crewai",
    "task": "YouTube競合チャンネル・動画の大規模Web調査（金融・投資・節約ジャンル）",
    "external_instructions_file": "company/tasks/2026-03-07_youtube_pipeline_quality_improvement/15_external_instructions/crewai_command.sh",
    "output_file": "company/tasks/2026-03-07_youtube_pipeline_quality_improvement/20_worker_outputs/01_competitor_analysis.md",
    "instructions": "YouTube「お金 投資 サラリーマン」「節約 貯金」「資産運用」系の100K再生以上の日本語チャンネル・動画を調査。音声スピード・トーン・映像構成（テロップ/図解）・サムネイルデザイン（文字数/配色）・チャンネルブランディング・動画尺パターンを分析。実在確認できないチャンネル名には[推測]タグ付与。"
  },
  {
    "step": 2,
    "worker_agent": "worker-extractor",
    "execution": "internal",
    "task": "競合調査結果から音声・映像・サムネ・ブランディング・動画尺の要素を抽出・分類",
    "input_files": [
      "company/tasks/2026-03-07_youtube_pipeline_quality_improvement/20_worker_outputs/01_competitor_analysis.md"
    ],
    "output_file": "company/tasks/2026-03-07_youtube_pipeline_quality_improvement/20_worker_outputs/02_extracted_elements.md",
    "instructions": "競合分析レポートから以下5カテゴリに要素を抽出・分類すること。(A)音声品質パターン（速度/トーン/間隔の数値的特徴）、(B)映像構成パターン（テロップ密度/図解比率/背景の傾向）、(C)サムネイルデザインパターン（文字数/配色/レイアウト構造）、(D)チャンネルブランディングパターン（名前構造/アイコンデザイン/バナー）、(E)動画長・構成パターン（尺/セクション構成/CTA配置）。EC2 t4g.medium（4GB RAM）制約を念頭に置き、技術実現可能性も注記すること。"
  },
  {
    "step": 3,
    "worker_agent": "worker-structurer",
    "execution": "internal",
    "task": "4成果物（競合レポート/改善仕様書/ブランディング提案/動画テーマ案）の構成を設計",
    "input_files": [
      "company/tasks/2026-03-07_youtube_pipeline_quality_improvement/20_worker_outputs/01_competitor_analysis.md",
      "company/tasks/2026-03-07_youtube_pipeline_quality_improvement/20_worker_outputs/02_extracted_elements.md"
    ],
    "output_file": "company/tasks/2026-03-07_youtube_pipeline_quality_improvement/20_worker_outputs/03_structure_plan.md",
    "instructions": "以下4成果物の章立て・骨格を設計すること。(1)競合分析レポート: エグゼクティブサマリー/チャンネル別分析/要素別ベンチマーク/インサイト、(2)pipeline改善仕様書: 現状課題/改善方針/関数別変更仕様（generate_voiceover/collect_footage/generate_thumbnail/generate_theme）/優先順位ロードマップ、(3)ブランディング提案: チャンネル名候補（5案）/アイコンデザイン方針/バナーデザイン方針/一貫性ガイドライン、(4)動画テーマ案: 最初の3本のテーマ/台本構成/SEOキーワード/サムネイル案。フィードバック6項目との対応マトリクスも設計すること。"
  },
  {
    "step": 4,
    "worker_agent": "worker-drafter",
    "execution": "internal",
    "task": "4成果物の全文ドラフト執筆",
    "input_files": [
      "company/tasks/2026-03-07_youtube_pipeline_quality_improvement/20_worker_outputs/01_competitor_analysis.md",
      "company/tasks/2026-03-07_youtube_pipeline_quality_improvement/20_worker_outputs/02_extracted_elements.md",
      "company/tasks/2026-03-07_youtube_pipeline_quality_improvement/20_worker_outputs/03_structure_plan.md"
    ],
    "output_file": "company/tasks/2026-03-07_youtube_pipeline_quality_improvement/20_worker_outputs/04_draft_all.md",
    "instructions": "structurerの骨格に従い4成果物を全文執筆すること。禁則: ElevenLabsを前提とした提案は不可（代替として併記はOK）・月額$50超の有料APIを前提とした提案は不可・実在しないチャンネル名/URLの捏造禁止（[推測]タグ使用）・EC2 t4g.medium 4GB超の処理提案は不可。改善仕様書は具体的なPythonコード変更箇所（関数名・行番号・diff形式）で記述。音声改善はgTTS速度パラメータ調整 + VOICEVOX代替案を含めること。動画尺は最低20分以上に統一する方法を仕様化。サムネイルはPIL実装の具体的修正案を記載。"
  },
  {
    "step": 5,
    "worker_agent": "worker-critic",
    "execution": "internal",
    "task": "ユーザーフィードバック6項目対応チェック＋技術制約整合性レビュー",
    "input_files": [
      "company/tasks/2026-03-07_youtube_pipeline_quality_improvement/00_request.md",
      "company/tasks/2026-03-07_youtube_pipeline_quality_improvement/20_worker_outputs/04_draft_all.md"
    ],
    "output_file": "company/tasks/2026-03-07_youtube_pipeline_quality_improvement/20_worker_outputs/05_review.md",
    "instructions": "以下の観点でドラフトをレビューし、OK/NG/要補強を判定すること。[フィードバック対応チェック] FB1音声改善・FB2映像改善・FB3動画尺20分以上・FB4サムネイルPIL修正・FB5アイコン方針・FB6チャンネル名提案 — 各項目に具体的な対応策が記載されているか。[技術制約チェック] ElevenLabs不使用・月額$50超API不使用・4GB RAM制約遵守・ARM/Graviton互換・Python3.9互換。[品質チェック] 実行可能な仕様か（曖昧な指示がないか）・競合分析の根拠がデータで示されているか。NG項目には修正指示を付与すること。"
  },
  {
    "step": 6,
    "worker_agent": "worker-editor",
    "execution": "internal",
    "task": "最終仕上げ・4成果物を個別ファイルに分割出力",
    "input_files": [
      "company/tasks/2026-03-07_youtube_pipeline_quality_improvement/20_worker_outputs/04_draft_all.md",
      "company/tasks/2026-03-07_youtube_pipeline_quality_improvement/20_worker_outputs/05_review.md"
    ],
    "output_files": [
      "company/tasks/2026-03-07_youtube_pipeline_quality_improvement/20_worker_outputs/06_final.md",
      "company/tasks/2026-03-07_youtube_pipeline_quality_improvement/20_worker_outputs/01_competitor_analysis.md（最終版）",
      "company/tasks/2026-03-07_youtube_pipeline_quality_improvement/20_worker_outputs/02_pipeline_improvement_spec.md",
      "company/tasks/2026-03-07_youtube_pipeline_quality_improvement/20_worker_outputs/03_branding_proposal.md",
      "company/tasks/2026-03-07_youtube_pipeline_quality_improvement/20_worker_outputs/04_video_themes.md"
    ],
    "instructions": "criticのレビュー指摘を全て反映した上で、4成果物を個別Markdownファイルに分割して保存すること。各ファイル冒頭に「対応フィードバック: FB#番号」を明示。表記統一（サーバ/サーバー等）・誤字脱字チェック・見出し構造の統一を実施。06_final.mdには全4成果物のエグゼクティブサマリー（各1段落）と次アクション一覧（優先順位付き）を記載すること。"
  }
]
```

---

## merge_plan（モード2統合手順）

1. `20_worker_outputs/06_final.md` をベースに統合
2. 各成果物ファイル（01〜04）の最終版を参照し一貫性確認
3. `05_review.md` のOK/NG最終判定を確認（全NGが解消されているか）
4. エグゼクティブサマリーをレポート冒頭に配置
5. フィードバック6項目の対応マトリクスを表形式で整理
6. 「70点の成果物」として出力 + 「残り30点の改善ポイント」セクション追加

---

## final_output_file

```
company/tasks/2026-03-07_youtube_pipeline_quality_improvement/80_manager_output.md
```

---

## ディレクトリ構成

```
company/tasks/2026-03-07_youtube_pipeline_quality_improvement/
├── 00_request.md
├── 10_wbs.md                          ← 本ファイル
├── 15_external_instructions/
│   └── crewai_command.sh              ← CrewAI実行指示書（外部委譲）
├── 20_worker_outputs/
│   ├── 01_competitor_analysis.md      ← researcher(CrewAI)出力
│   ├── 02_extracted_elements.md       ← extractor出力
│   ├── 02_pipeline_improvement_spec.md ← editor最終出力
│   ├── 03_branding_proposal.md        ← editor最終出力
│   ├── 03_structure_plan.md           ← structurer出力
│   ├── 04_draft_all.md                ← drafter出力
│   ├── 04_video_themes.md             ← editor最終出力
│   ├── 05_review.md                   ← critic出力
│   └── 06_final.md                    ← editor統合出力
└── 80_manager_output.md               ← 部長統合
```
