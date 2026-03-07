# WBS：AIインフルエンサー市場調査

## タスク分解（複雑度：heavy）

### フロー
`researcher` (external via CrewAI) → `extractor` → `structurer` → `drafter` → `critic` → `editor`

---

## 1. **外部調査フェーズ（CrewAI）**
**実行者**: CrewAI + Groq
**タスク**: Web検索を伴う大規模市場調査（海外TOP10・日本事例・トレンド全体）
**出力**: `report.json` + `raw_output.txt`

### 実行指示書
ファイル: `15_external_instructions/crewai_command.sh`

---

## 2. **データ抽出フェーズ**（worker-extractor）
**タスク**: CrewAIからの `report.json` を解析し、構造化データに抽出
**入力**: CrewAI出力（report.json）
**出力**: `20_worker_outputs/01_extracted_data.md`
**指示**:
- report.json の players / trends / implications を抽出
- テーブル形式で整理（フォロワー数・収益モデル等）
- 信頼度を [高/中/低] で付与
- 出典URL を必ず記載

---

## 3. **構造化フェーズ**（worker-structurer）
**タスク**: 抽出データを4つのコンセプト分析 + ジャンル分析に構造化
**入力**: `20_worker_outputs/01_extracted_data.md`
**出力**: `20_worker_outputs/02_structured_analysis.md`
**指示**:
- 海外事例を SWOT / 3C 分析で整理
- 日本市場との差分を明示
- 「金融×AI」「テック×ライフスタイル」「旅行×AI」の市場性マトリックス作成
- ブルーオーシャン機会の抽出

---

## 4. **初稿作成フェーズ**（worker-drafter）
**タスク**: 構造化データから最終レポート初稿を執筆
**入力**: `20_worker_outputs/02_structured_analysis.md`
**出力**: `20_worker_outputs/03_draft.md`
**指示**:
- セクション構成：調査テーマ → 発見事項 → 要点 → 未確認事項
- テーブル形式で海外TOP10・日本事例を並べる
- 月収実例を [金額] [フォロワー数] [プラットフォーム] 形式で記載
- 推測は [推測] タグで明示
- 最後に「新規事業への示唆」セクションを追加

---

## 5. **品質レビューフェーズ**（worker-critic）
**タスク**: definition_of_done と quality_bar に照らしてレビュー
**入力**: `20_worker_outputs/03_draft.md`
**出力**: `20_worker_outputs/04_review_comments.md`
**指示**:
- 7つの完了条件をすべて満たしているか確認
- 出典なしの数値がないか確認
- 推測に [推測] タグが付いているか確認
- 実行可能な提言が含まれているか確認
- NG項目があれば指摘（修正指示）

---

## 6. **最終版仕上げフェーズ**（worker-editor）
**タスク**: 品質レビューを反映し、最終版を完成
**入力**: `20_worker_outputs/03_draft.md` + `20_worker_outputs/04_review_comments.md`
**出力**: `80_manager_output.md`
**指示**:
- critic の指摘をすべて反映
- 表記ゆれを統一（「インフルエンサー」vs「influencer」等）
- 誤字脱字チェック
- 最終確認：全7つの完了条件を再度確認
- 出力ファイルを `04_RESEARCH/2026-03-07_ai_influencer_market_survey.md` にも複製

---

## 統合手順（部長）

`80_manager_output.md` に統合する際のチェックリスト：
- [ ] 海外TOP10がフォロワー数・コンセプト・成功要因と共に記載されている
- [ ] 日本事例が5件以上まとめられている
- [ ] 規制動向・技術トレンド・ジャンル分析がある
- [ ] 4コンセプトの市場性評価がある
- [ ] フォロワー数別収入目安が示されている
- [ ] 実際の月収事例（複数件）が記載されている
- [ ] ブルーオーシャンの提案がある
- [ ] すべての推測に [推測] タグが付いている
- [ ] 出典がURLで記載されている

---

## 外部委譲実行指示書

**ファイル**: `15_external_instructions/crewai_command.sh`
**ツール**: CrewAI + Groq
**テーマ**: AI virtual influencer market research 2025-2026
