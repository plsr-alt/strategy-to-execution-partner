# WBS: YouTube自動動画生成パイプライン ブラッシュアップ戦略

## メタ情報
- 作成日: 2026-03-06
- 担当マネージャー: strategy-manager
- complexity: heavy（6ワーカー構成）
- task_dir: company/tasks/2026-03-06_youtube_pipeline_improvement/
- 最終成果物: 80_manager_output.md

---

## ワーカー構成・依存関係

```
researcher → extractor → structurer → drafter → critic → editor
```

---

## employee_jobs

```json
{
  "employee_jobs": [
    {
      "worker_agent": "worker-researcher",
      "task": "YouTube 100万再生チャンネルの成功パターン・日本市場自動生成チャンネル事例・SEO最新トレンド・競合分析の調査",
      "input_files": [
        "company/tasks/2026-03-06_youtube_pipeline_improvement/00_request.md"
      ],
      "output_file": "company/tasks/2026-03-06_youtube_pipeline_improvement/20_worker_outputs/01_research.md",
      "instructions": "【戦略部の文脈】本調査は「日本のサラリーマン向け自動生成YouTubeチャンネル」が100万再生を達成するための根拠データ収集が目的。以下4領域を調査し、データ根拠（数値・事例名・出典）を必ず明記すること。\n\n【調査領域】\n1. **YouTube 100万再生成功パターン**: 日本語チャンネルで100万再生を達成した動画の共通構造（冒頭フック、尺、サムネイル要素、タイトル文字数・構成）。特にAI/自動生成系チャンネルに絞ること。\n2. **日本市場の自動生成チャンネル事例**: 自動生成（ずんだもん系・解説系・VOICEVOX系等）で伸びているチャンネルの月間投稿本数・平均再生数・収益化状況・ジャンル別成功率。\n3. **YouTube SEO最新トレンド（2024-2025）**: タイトル・説明文・タグ・チャプター・サムネイルABテストに関するアルゴリズム変更情報。Shorts vs 長尺の推奨戦略。\n4. **競合チャンネル比較**: 金融・投資・節約 / テック・AI解説 / ビジネス・自己啓発の各ジャンルで上位3チャンネルずつ（計9チャンネル）の登録者数・平均再生数・投稿頻度・差別化ポイントを比較表形式で整理。\n\n【制約】無料/低コスト路線との整合性を念頭に置いた事例を優先すること。"
    },
    {
      "worker_agent": "worker-extractor",
      "task": "researcher成果物から、現行パイプライン（Groq/gTTS/Pexels/moviepy/PIL）に直接適用可能な改善ポイントを抽出・分類",
      "input_files": [
        "company/tasks/2026-03-06_youtube_pipeline_improvement/00_request.md",
        "company/tasks/2026-03-06_youtube_pipeline_improvement/20_worker_outputs/01_research.md"
      ],
      "output_file": "company/tasks/2026-03-06_youtube_pipeline_improvement/20_worker_outputs/02_extraction.md",
      "instructions": "【戦略部の文脈】前工程（researcher）の調査結果を入力として、現行スタック（Python, moviepy, PIL, Groq API, gTTS, Pexels API）に直接適用できる改善ポイントのみを抽出・分類すること。「できること」と「できないこと」を明確に分けることが最重要。\n\n【抽出・分類作業】\n1. **課題×改善策マッピング**: 現状5課題（音声品質/映像マッチング/サムネイルCTR/動画構成単調/SEO不足）それぞれに対して、researcherの調査結果から具体的改善策を紐付ける。\n2. **実装可能性フィルタリング**: 各改善策を「現行スタックで即実装可能」「軽微な追加コストで実装可能（ROI試算必要）」「スタック変更が必要（本プロジェクト対象外）」の3段階に分類。\n3. **効果試算**: 各改善策の期待効果を定量的に見積もる（例: 「gTTS → VOICEVOX変更で視聴維持率+15%推定、根拠: 事例チャンネルX」）。\n4. **適用優先度スコアリング**: 「効果の大きさ × 実装の容易さ」でスコアリングし、上位10施策を優先度順にリスト化。\n\n【出力形式】マークダウンの表形式で整理。データ根拠は researcher の出力から引用元を明記すること。"
    },
    {
      "worker_agent": "worker-structurer",
      "task": "改善ロードマップの骨格設計（Phase 1/2/3）と優先度×難易度マトリクスの構造化",
      "input_files": [
        "company/tasks/2026-03-06_youtube_pipeline_improvement/00_request.md",
        "company/tasks/2026-03-06_youtube_pipeline_improvement/20_worker_outputs/01_research.md",
        "company/tasks/2026-03-06_youtube_pipeline_improvement/20_worker_outputs/02_extraction.md"
      ],
      "output_file": "company/tasks/2026-03-06_youtube_pipeline_improvement/20_worker_outputs/03_structure.md",
      "instructions": "【戦略部の文脈】extractorが整理した改善ポイントを基に、「100万再生到達」という単一ゴールに向けたロードマップ骨格を設計する。以下の成果物フォーマットに沿って骨格（目次＋各セクションの論点リスト）を構造化すること。本文は書かない。構造のみ。\n\n【設計すべき骨格】\n1. **Phase 1/2/3 ロードマップ**: 各Phaseの期間目安・主要施策・KPI（再生数/CTR/視聴維持率の目標値）・依存関係を設計。「1本バズシナリオ」と「累計100万シナリオ」の両方の到達経路を描くこと。\n2. **優先度×難易度マトリクス**: extractorのスコアリングを基に2×2マトリクスを設計（Quick Win / 重点投資 / 低優先 / 要再検討）。各象限に施策を配置する骨格を作成。\n3. **成果物フォーマット設計**: drafter が執筆しやすいよう、最終成果物（80_manager_output.md）の完全な目次と各セクションの「書くべき内容の論点リスト」を作成すること。\n4. **SWOT分析フレーム**: 現行パイプラインのS/W/O/T各象限に入るべき論点を箇条書きで整理。\n5. **競合比較表テンプレ**: drafter が埋めやすいよう、比較軸（登録者数/平均再生数/投稿頻度/音声品質/サムネイル戦略/差別化ポイント）を定義した表のヘッダを作成。\n\n【フレームワーク適用必須】: McKinseyの優先度フレームワーク（Impact×Effort）、Jobs-to-be-Done（ターゲットのニーズ分解）の観点を適用すること。"
    },
    {
      "worker_agent": "worker-drafter",
      "task": "全8セクションの本文執筆（エグゼクティブサマリー・SWOT・ロードマップ・マトリクス・技術実装ガイド・SEO戦略・コンテンツ戦略・リスク対策）",
      "input_files": [
        "company/tasks/2026-03-06_youtube_pipeline_improvement/00_request.md",
        "company/tasks/2026-03-06_youtube_pipeline_improvement/20_worker_outputs/01_research.md",
        "company/tasks/2026-03-06_youtube_pipeline_improvement/20_worker_outputs/02_extraction.md",
        "company/tasks/2026-03-06_youtube_pipeline_improvement/20_worker_outputs/03_structure.md"
      ],
      "output_file": "company/tasks/2026-03-06_youtube_pipeline_improvement/20_worker_outputs/04_draft.md",
      "instructions": "【戦略部の文脈】structurerが設計した骨格に沿って、全セクションの本文を執筆する。以下8セクションをすべて記述すること。\n\n【執筆必須セクション】\n1. **エグゼクティブサマリー**（400字以内）: 現状・最重要改善3点・100万再生到達の最短経路。結論ファーストで書く。\n2. **現状分析**: SWOT分析（2×2表）＋競合チャンネル比較表（9チャンネル、比較軸6項目以上）。\n3. **改善ロードマップ**: Phase 1（0-3ヶ月）/ Phase 2（3-6ヶ月）/ Phase 3（6-12ヶ月）。各Phaseに施策・KPI・期待再生数を記載。「1本バズシナリオ」と「累計100万シナリオ」の両経路を明記。\n4. **改善項目一覧**: 優先度×難易度マトリクス（Quick Win/重点投資/低優先/要再検討の4象限）。表形式で施策名・期待効果・実装難易度・ROI試算を記載。\n5. **技術実装ガイド**: 以下5領域でそれぞれPythonコードスニペット（動作する具体的なコード）を含めること。\n   - 音声品質改善（gTTS代替またはgTTS後処理でのピッチ/速度調整）\n   - 映像マッチング改善（Pexels APIクエリ最適化またはキーワード抽出ロジック）\n   - サムネイル生成改善（PIL/Pillowでのデザイン強化）\n   - 動画構成改善（moviepyでの構成パターン多様化）\n   - SEOメタデータ最適化（Groq APIプロンプト改善）\n6. **YouTube SEO・アルゴリズム攻略**: タイトル設計・説明文・タグ・チャプター・投稿タイミング・Shorts戦略。具体的なテンプレートを含めること。\n7. **コンテンツ戦略**: バズりやすいテーマ選定（ジャンル別ランキング）・動画構成パターン3種・月次投稿カレンダーテンプレート。\n8. **リスクと対策**: 上位5リスク（著作権/API制限/アルゴリズム変更等）とそれぞれの対策・代替手段。\n\n【制約】有料ツール提案時は必ずROI試算（月額コスト÷期待増収）を付けること。推測・未確認情報には【推測】タグを付与すること。コードは現行スタック（Python 3.x, moviepy, PIL, Groq API）で動作するものを書くこと。"
    },
    {
      "worker_agent": "worker-critic",
      "task": "成果物のDefinition of Done照合・論理的整合性・実現可能性チェック・改善指示",
      "input_files": [
        "company/tasks/2026-03-06_youtube_pipeline_improvement/00_request.md",
        "company/tasks/2026-03-06_youtube_pipeline_improvement/20_worker_outputs/04_draft.md"
      ],
      "output_file": "company/tasks/2026-03-06_youtube_pipeline_improvement/20_worker_outputs/05_critique.md",
      "instructions": "【戦略部の文脈】drafterの成果物を以下のDoD（Definition of Done）チェックリストと照合し、NGポイントを指摘・改善指示を出すこと。editorへの明確な修正指示を出力する。\n\n【DoDチェックリスト】\n- [ ] 全8セクションが存在するか\n- [ ] エグゼクティブサマリーが400字以内か\n- [ ] SWOT分析が4象限すべて埋まっているか\n- [ ] 競合チャンネル比較表が9チャンネル・6項目以上あるか\n- [ ] Phase 1/2/3それぞれにKPIが設定されているか\n- [ ] 「1本バズシナリオ」と「累計100万シナリオ」の両方が記述されているか\n- [ ] 優先度×難易度マトリクスに施策が4象限に分類されているか\n- [ ] 技術実装ガイドに5領域すべてでコードスニペットがあるか\n- [ ] コードスニペットが現行スタックで動作するレベルか（importが適切か）\n- [ ] 有料ツール提案時にROI試算が付いているか\n- [ ] 推測情報に【推測】タグが付いているか\n- [ ] SEO攻略にタイトルテンプレートが含まれているか\n- [ ] 投稿カレンダーテンプレートが含まれているか\n- [ ] 上位5リスクとそれぞれの対策が記載されているか\n\n【論理整合性チェック】\n- Phase間の施策に矛盾や抜け漏れがないか\n- KPI目標値が現実的か（根拠データとの整合）\n- コードスニペットの技術的整合性（APIの使い方が正しいか）\n\n【出力形式】\n- OK項目: 箇条書き\n- NG/要改善項目: 表形式（項目名・問題内容・改善指示・優先度High/Mid/Low）\n- editorへの総合改善指示: 箇条書き"
    },
    {
      "worker_agent": "worker-editor",
      "task": "criticの指摘を反映した最終校正・フォーマット統一・推測タグ確認・最終成果物の完成",
      "input_files": [
        "company/tasks/2026-03-06_youtube_pipeline_improvement/00_request.md",
        "company/tasks/2026-03-06_youtube_pipeline_improvement/20_worker_outputs/04_draft.md",
        "company/tasks/2026-03-06_youtube_pipeline_improvement/20_worker_outputs/05_critique.md"
      ],
      "output_file": "company/tasks/2026-03-06_youtube_pipeline_improvement/20_worker_outputs/06_edited.md",
      "instructions": "【戦略部の文脈】criticの指摘事項をすべて反映し、最終成果物として完成度の高いドキュメントに仕上げること。\n\n【校正・修正タスク】\n1. **criticのNG項目を全件修正**: criticの出力にあるNG/要改善項目をdraftに反映。High優先度から順に対応。\n2. **フォーマット統一**: 見出しレベル統一（H1/H2/H3の階層が崩れていないか）、表の列幅・記法の統一、コードブロックの言語タグ付与（```python）。\n3. **推測タグ確認**: 根拠のない記述に【推測】が付いているか最終確認。逆に根拠があるのに【推測】タグが付いている箇所は外す。\n4. **エグゼクティブサマリー最終調整**: 400字制約の再確認と文章の磨き上げ。\n5. **読みやすさ向上**: 長段落の箇条書き化、重要数値の**太字**化、セクション間の論理的繋がりの確認。\n\n【品質基準】\n- エグゼクティブサマリー冒頭: 最重要インサイトが3行以内で伝わること\n- データソース整合性: 数値引用元がresearcher調査に紐づいていること\n- 実行可能性: 読んだ翌日から着手できる粒度の指示があること\n\n【出力】完成した最終ドキュメント全文をそのまま出力すること（criticへのコメントや説明文は不要）。"
    }
  ],
  "merge_plan": "worker-editorの出力（06_edited.md）をベースに、strategy-managerが以下の統合作業を実施する。\n1. エグゼクティブサマリーを冒頭に配置（400字以内・結論ファースト）\n2. データソース整合性の最終確認（researcher調査との数値整合）\n3. 「70点の成果物」評価と「残り30点の改善ポイント」の明示\n4. 実行可能な提言の優先順位付け（Next Action TOP3を明示）\n5. 80_manager_output.md として保存",
  "final_output_file": "company/tasks/2026-03-06_youtube_pipeline_improvement/80_manager_output.md"
}
```

---

## WBS詳細

### Step 1: worker-researcher
| 項目 | 内容 |
|------|------|
| インプット | 00_request.md |
| アウトプット | 20_worker_outputs/01_research.md |
| 調査領域 | ①100万再生成功パターン ②日本自動生成チャンネル事例 ③SEO最新トレンド ④競合9チャンネル比較 |
| 依存 | なし（先頭ステップ） |

### Step 2: worker-extractor
| 項目 | 内容 |
|------|------|
| インプット | 00_request.md + 01_research.md |
| アウトプット | 20_worker_outputs/02_extraction.md |
| 作業内容 | 現行スタック適用可能施策の抽出・3段階分類・効果試算・優先度スコアリング |
| 依存 | Step 1完了後 |

### Step 3: worker-structurer
| 項目 | 内容 |
|------|------|
| インプット | 00_request.md + 01_research.md + 02_extraction.md |
| アウトプット | 20_worker_outputs/03_structure.md |
| 作業内容 | Phase 1/2/3骨格・マトリクス設計・成果物目次・SWOT/競合表テンプレ作成 |
| 依存 | Step 2完了後 |

### Step 4: worker-drafter
| 項目 | 内容 |
|------|------|
| インプット | 00_request.md + 01~03_research/extraction/structure.md |
| アウトプット | 20_worker_outputs/04_draft.md |
| 作業内容 | 全8セクション執筆・5領域コードスニペット・ROI試算・推測タグ付与 |
| 依存 | Step 3完了後 |

### Step 5: worker-critic
| 項目 | 内容 |
|------|------|
| インプット | 00_request.md + 04_draft.md |
| アウトプット | 20_worker_outputs/05_critique.md |
| 作業内容 | DoD 14項目チェック・論理整合性・技術的整合性・editor向け改善指示 |
| 依存 | Step 4完了後 |

### Step 6: worker-editor
| 項目 | 内容 |
|------|------|
| インプット | 00_request.md + 04_draft.md + 05_critique.md |
| アウトプット | 20_worker_outputs/06_edited.md |
| 作業内容 | NG項目全件修正・フォーマット統一・推測タグ最終確認・品質仕上げ |
| 依存 | Step 5完了後 |

### Final: strategy-manager 統合
| 項目 | 内容 |
|------|------|
| インプット | 06_edited.md |
| アウトプット | 80_manager_output.md |
| 作業内容 | エグゼクティブサマリー冒頭配置・70点評価＋30点改善ポイント・Next Action TOP3 |
| 依存 | Step 6完了後 |
