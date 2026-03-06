# WBS: EA（自動売買）企画〜設計・検証・実装計画

## メタ情報
- 作成日: 2026-03-06
- 担当マネージャー: strategy-manager
- complexity: heavy（6ワーカー構成）
- task_dir: company/tasks/2026-03-06_ea_trading_design/
- 最終成果物: company/tasks/2026-03-06_ea_trading_design/80_manager_output.md
- 納品成果物: 03_PROJECTS/ea_trading/ 配下の PLAN.md / SPEC.md / TODO.md / KNOWLEDGE.md
- **統合完了日**: 2026-03-06
- **ステータス**: 完了

---

## ワーカー構成・依存関係

```
researcher → extractor → structurer → drafter → critic → editor → [manager統合 完了]
```

---

## employee_jobs

```json
{
  "employee_jobs": [
    {
      "worker_agent": "worker-researcher",
      "task": "FXアルゴリズム取引の市場実態・MT4/MT5主要戦略パターン・バックテスト統計・代表的EAの公開実績データ調査",
      "input_files": [
        "company/tasks/2026-03-06_ea_trading_design/00_request.md"
      ],
      "output_file": "company/tasks/2026-03-06_ea_trading_design/20_worker_outputs/01_research.md",
      "instructions": "【戦略部の文脈】本調査は「国内ブローカー環境（スプレッド1-2pips・レバ25倍）でVPS稼働させる、月次3-5%・最大DD20%以内のFX自動売買EA」を企画するための根拠データ収集が目的。以下4領域を調査し、数値・事例名・出典を必ず明記すること。確認できない情報は【推測】タグを付けること。\n\n【調査領域】\n\n1. **FX EA市場実態（MT4/MT5）**\n   - MT4/MT5の国内普及率・主要ブローカー対応状況\n   - 国内FXブローカー標準スペック（スプレッド・スワップ・約定速度・VPS推奨スペック）\n   - EA配布・販売市場の概況（MQL5 Market・国内EA販売サイト）\n   - 個人開発EAの成功率・寿命（公開データがあれば）\n\n2. **主要戦略パターンの特性比較**\n   - トレンドフォロー系（MA/EMA クロス・ADX・ブレイクアウト）: 特性・得意相場・不得意相場\n   - レンジ系（RSI・ボリバン・平均回帰）: 特性・得意相場・不得意相場\n   - モメンタム系（MACD・ストキャスティクス）: 特性・得意相場・不得意相場\n   - ハイブリッド（複数インジ合成）: 開発難度と過剰最適化リスク\n   - 各戦略の推奨通貨ペア・時間足の定説\n\n3. **バックテスト統計・公開EAの実績データ**\n   - 「現実的に達成可能な」PF・MaxDD・勝率・シャープレシオの分布（MQL5 Market等の公開データ）\n   - 聖杯（過剰最適化）EAの特徴パターン（PF3以上・勝率80%以上等の危険シグナル）\n   - フォワードテストでの崩壊率・典型的崩壊パターン\n   - 現実的なGO/NO-GO基準として引用できる数値レンジ\n\n4. **MT4/MT5開発の既知の罠・バグパターン**\n   - MQL4/MQL5の仕様上のハマりポイント（バー数制限・OnTick vs OnBar・History の扱い等）\n   - バックテスト≠リアルになる典型的原因（スプレッド・スリッページ・リクオート・時刻ずれ）\n   - ナンピン禁止の具体的な代替リスク管理手法（ストップロス設計・ポジションサイジング理論）\n   - VPS稼働時の注意点（接続断・時刻同期・ブローカーサーバーとの距離）"
    },
    {
      "worker_agent": "worker-extractor",
      "task": "researcher成果物からEAコンセプト3案の素材を抽出・MVP/V1仕様の論点整理・GO/NO-GO基準の数値根拠を抽出",
      "input_files": [
        "company/tasks/2026-03-06_ea_trading_design/00_request.md",
        "company/tasks/2026-03-06_ea_trading_design/20_worker_outputs/01_research.md"
      ],
      "output_file": "company/tasks/2026-03-06_ea_trading_design/20_worker_outputs/02_extraction.md",
      "instructions": "【戦略部の文脈】researcherの調査結果を入力として、以下4つの抽出・分類作業を行うこと。全て数値根拠付きで、「詳細は別途検討」の逃げは禁止。\n\n【抽出・分類作業】\n\n1. **EAコンセプト候補の素材抽出**\n   - researcher調査から「月次3-5%・MaxDD20%以内・ナンピンNG」の制約に合致する戦略パターンを3つ選定\n   - 各戦略の選定理由を数値根拠で説明（例: 「EMA+ADXトレンドフォローは公開EA中上位20%がPF1.5以上を記録（出典: MQL5 Market統計）」）\n   - 各戦略の「強み/弱み/リスク/開発難度」を4象限で整理\n\n2. **MVP仕様の論点整理**\n   - MVP（最小検証単位）として必要な最低限のロジック要素を定義\n   - 「1戦略・1通貨ペア」の制約下で、検証に必要な最小パラメータセットを抽出\n   - バックテストで意味ある結果を得るために必要なデータ期間・tick品質の根拠を数値で抽出\n\n3. **V1仕様の論点整理**\n   - MVPからV1へのスケールアップに必要な追加要素のリストアップ\n   - モジュール分割（OrderManager/SignalEngine/RiskManager等）の必要性根拠\n   - 複数通貨ペア展開・パラメータ最適化の判断基準\n\n4. **GO/NO-GO基準の数値根拠抽出**\n   - researcher調査の公開EA実績データから「現実的な閾値」を抽出\n   - PF・MaxDD・勝率・シャープレシオ・プロフィットファクター分布の中央値・上位25%値を整理\n   - 「聖杯シグナル」（過剰最適化を示す危険な数値パターン）を抽出・警告文草案を作成\n\n【出力形式】Markdownの表形式を基本とする。数値引用元はresearcherの出力から明示すること。"
    },
    {
      "worker_agent": "worker-structurer",
      "task": "4ドキュメント（PLAN/SPEC/TODO/KNOWLEDGE）の完全な骨格設計と執筆論点リストの構造化",
      "input_files": [
        "company/tasks/2026-03-06_ea_trading_design/00_request.md",
        "company/tasks/2026-03-06_ea_trading_design/20_worker_outputs/01_research.md",
        "company/tasks/2026-03-06_ea_trading_design/20_worker_outputs/02_extraction.md"
      ],
      "output_file": "company/tasks/2026-03-06_ea_trading_design/20_worker_outputs/03_structure.md",
      "instructions": "【戦略部の文脈】extractorが整理した論点を基に、4ドキュメント（PLAN.md/SPEC.md/TODO.md/KNOWLEDGE.md）それぞれの完全な骨格（目次＋各セクションの執筆論点）を設計すること。本文は書かない。構造と論点のみ。drafterが迷わず執筆できる粒度にすること。\n\n【設計すべき骨格】\n\n1. **PLAN.md 骨格**\n   - 企画概要セクション（背景・目的・スコープ・制約条件の論点）\n   - EAコンセプト3案比較表のヘッダ設計（比較軸: 戦略タイプ/対象通貨ペア/推奨時間足/期待PF/期待MaxDD/開発難度/過剰最適化リスク/適した相場環境 の8軸以上）\n   - 推奨案セクション（選定理由・判断基準・リスクの論点）\n   - 前提条件整理セクション（ブローカー条件・MT4仕様・VPS要件の論点）\n\n2. **SPEC.md 骨格**\n   - MVP仕様セクション: エントリーロジック・エグジットロジック・フィルター条件・RiskManager仕様をパラメータ表形式で設計（パラメータ名/型/デフォルト値/許容範囲/説明 の5列）\n   - V1仕様セクション: MVPとの差分定義・追加パラメータ表・複数通貨ペア対応要件\n   - SL/TP設計セクション（ATR基準・固定pips基準の比較論点）\n   - ロット計算式セクション（証拠金ベース計算式・1回損失2%制約の数式）\n\n3. **TODO.md 骨格**\n   - モジュール分割設計（SignalEngine/OrderManager/RiskManager/BacktestHelper/Utilsの責務定義）\n   - フェーズ別実装順序（Phase 1: MVP/Phase 2: バックテスト/Phase 3: フォワードテスト/Phase 4: V1の論点）\n   - チェックボックス形式タスクリストの階層設計（大タスク→サブタスク→テスト確認の3層）\n   - 工数見積もり基準（MT4/MQL4開発の標準工数目安の論点）\n   - テスト計画設計（単体テスト/結合テスト/バックテスト/フォワードテストの各条件論点）\n\n4. **KNOWLEDGE.md 骨格**\n   - バックテスト条件仕様セクション（通貨ペア・期間・スプレッド・スリッページ・tick品質の具体数値論点）\n   - GO/NO-GO判定表のヘッダ設計（指標名/GO閾値/NO-GO閾値/判定根拠 の4列）\n   - 過剰最適化警告セクション（聖杯シグナルのパターン・対策論点）\n   - MT4/MQL4バグ予防策セクション（既知の罠カテゴリ分類論点）\n   - VPS運用セクション（稼働チェックリスト・障害対応フロー論点）\n\n【フレームワーク適用】\n- MVP設計: MoSCoW法（Must/Should/Could/Won't）でSPECの機能を分類する軸を設計すること\n- タスク管理: WBS（Work Breakdown Structure）の3層設計をTODOに適用すること\n- リスク管理: ケリー基準・固定比率ポジションサイジング理論をSPECのロット計算に適用する論点を整理すること"
    },
    {
      "worker_agent": "worker-drafter",
      "task": "4ドキュメント（PLAN.md/SPEC.md/TODO.md/KNOWLEDGE.md）の全本文を執筆",
      "input_files": [
        "company/tasks/2026-03-06_ea_trading_design/00_request.md",
        "company/tasks/2026-03-06_ea_trading_design/20_worker_outputs/01_research.md",
        "company/tasks/2026-03-06_ea_trading_design/20_worker_outputs/02_extraction.md",
        "company/tasks/2026-03-06_ea_trading_design/20_worker_outputs/03_structure.md"
      ],
      "output_file": "company/tasks/2026-03-06_ea_trading_design/20_worker_outputs/04_draft.md",
      "instructions": "（省略 - 10_wbs.md初版と同一）"
    },
    {
      "worker_agent": "worker-critic",
      "task": "4ドキュメント草稿のDefinition of Done照合・数値定義の完全性チェック・論理整合性・過剰最適化警告の妥当性確認",
      "input_files": [
        "company/tasks/2026-03-06_ea_trading_design/00_request.md",
        "company/tasks/2026-03-06_ea_trading_design/20_worker_outputs/04_draft.md"
      ],
      "output_file": "company/tasks/2026-03-06_ea_trading_design/20_worker_outputs/05_critique.md",
      "instructions": "（省略 - 10_wbs.md初版と同一）"
    },
    {
      "worker_agent": "worker-editor",
      "task": "criticの指摘を反映した最終校正・4ドキュメントをそれぞれ独立したMarkdownとして完成・フォーマット統一",
      "input_files": [
        "company/tasks/2026-03-06_ea_trading_design/00_request.md",
        "company/tasks/2026-03-06_ea_trading_design/20_worker_outputs/04_draft.md",
        "company/tasks/2026-03-06_ea_trading_design/20_worker_outputs/05_critique.md"
      ],
      "output_file": "company/tasks/2026-03-06_ea_trading_design/20_worker_outputs/06_edited.md",
      "instructions": "（省略 - 10_wbs.md初版と同一）"
    }
  ],
  "merge_plan": "worker-editorの出力（06_edited.md）をベースに、strategy-managerが以下の統合作業を実施する。\n1. 06_edited.mdを4ドキュメントに分割し、03_PROJECTS/ea_trading/ 配下に PLAN.md/SPEC.md/TODO.md/KNOWLEDGE.md として保存\n2. エグゼクティブサマリーを冒頭に配置した 80_manager_output.md を作成（400字以内・結論ファースト）\n3. データソース整合性の最終確認（researcher調査との数値整合）\n4. 「70点の成果物」評価と「残り30点の改善ポイント」の明示\n5. 実行可能な提言の優先順位付け（Next Action TOP3を明示）\n6. 80_manager_output.md として保存",
  "final_output_file": "company/tasks/2026-03-06_ea_trading_design/80_manager_output.md"
}
```

---

## WBS詳細

### Step 1: worker-researcher
| 項目 | 内容 |
|------|------|
| インプット | 00_request.md |
| アウトプット | 20_worker_outputs/01_research.md |
| 調査領域 | ①FX EA市場実態・MT4/MT5普及状況 ②主要戦略パターン特性比較 ③公開EAバックテスト統計・実績データ ④MT4/MQL4既知の罠・バグパターン |
| 依存 | なし（先頭ステップ） |

### Step 2: worker-extractor
| 項目 | 内容 |
|------|------|
| インプット | 00_request.md + 01_research.md |
| アウトプット | 20_worker_outputs/02_extraction.md |
| 作業内容 | EAコンセプト候補素材の抽出・MVP/V1仕様論点整理・GO/NO-GO基準数値根拠の抽出 |
| 依存 | Step 1完了後 |

### Step 3: worker-structurer
| 項目 | 内容 |
|------|------|
| インプット | 00_request.md + 01_research.md + 02_extraction.md |
| アウトプット | 20_worker_outputs/03_structure.md |
| 作業内容 | PLAN/SPEC/TODO/KNOWLEDGE 4ドキュメントの完全骨格設計・執筆論点リスト・パラメータ表ヘッダ設計 |
| 依存 | Step 2完了後 |

### Step 4: worker-drafter
| 項目 | 内容 |
|------|------|
| インプット | 00_request.md + 01〜03_research/extraction/structure.md |
| アウトプット | 20_worker_outputs/04_draft.md |
| 作業内容 | 4ドキュメント全本文の執筆（コンセプト比較表・パラメータ定義表・チェックボックスタスク・GO/NO-GO表・バグ予防策） |
| 依存 | Step 3完了後 |

### Step 5: worker-critic
| 項目 | 内容 |
|------|------|
| インプット | 00_request.md + 04_draft.md |
| アウトプット | 20_worker_outputs/05_critique.md |
| 作業内容 | DoD 24項目チェック・論理整合性（通貨ペア一貫性・SL/スプレッド整合・工数現実性）・GO/NO-GO基準の妥当性確認・editor向け改善指示 |
| 依存 | Step 4完了後 |

### Step 6: worker-editor
| 項目 | 内容 |
|------|------|
| インプット | 00_request.md + 04_draft.md + 05_critique.md |
| アウトプット | 20_worker_outputs/06_edited.md |
| 作業内容 | NG項目全件修正・4ドキュメント連結形式での完成・フォーマット統一・推測タグ最終確認・曖昧表現排除 |
| 依存 | Step 5完了後 |

### Final: strategy-manager 統合（完了）
| 項目 | 内容 |
|------|------|
| インプット | 06_edited.md |
| アウトプット | 80_manager_output.md + 03_PROJECTS/ea_trading/ 配下の4ドキュメント |
| 作業内容 | 4ドキュメント分割保存・エグゼクティブサマリー冒頭配置・70点評価＋30点改善ポイント・Next Action TOP3 |
| 依存 | Step 6完了後 |
| **完了日** | 2026-03-06 |

---

## 成果物マップ

| ファイル | 担当 | 保存先 | 状態 |
|---------|------|--------|------|
| 01_research.md | worker-researcher | 20_worker_outputs/ | 完了 |
| 02_extraction.md | worker-extractor | 20_worker_outputs/ | 完了 |
| 03_structure.md | worker-structurer | 20_worker_outputs/ | 完了 |
| 04_draft.md | worker-drafter | 20_worker_outputs/ | 完了 |
| 05_critique.md | worker-critic | 20_worker_outputs/ | 完了 |
| 06_edited.md | worker-editor | 20_worker_outputs/ | 完了 |
| 80_manager_output.md | strategy-manager | company/tasks/2026-03-06_ea_trading_design/ | **完了** |
| PLAN.md | strategy-manager（分割保存） | 03_PROJECTS/ea_trading/ | **完了** |
| SPEC.md | strategy-manager（分割保存） | 03_PROJECTS/ea_trading/ | **完了** |
| TODO.md | strategy-manager（分割保存） | 03_PROJECTS/ea_trading/ | **完了** |
| KNOWLEDGE.md | strategy-manager（分割保存） | 03_PROJECTS/ea_trading/ | **完了** |
