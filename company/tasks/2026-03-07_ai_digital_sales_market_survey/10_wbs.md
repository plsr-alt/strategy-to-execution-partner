# WBS分解

## execution_mode: hybrid

### フェーズ1: 外部調査（CrewAI）
- `worker-researcher` の代わりに CrewAI + Groq で Web検索・調査
- 出力：`20_worker_outputs/01_research_crewai.json`

### フェーズ2-5: 内部処理（ワーカー）
- structurer：調査結果の構造化・フレームワーク整理
- drafter：初稿作成
- critic：品質レビュー・根拠確認
- editor：最終版仕上げ・フォーマット統一

## 成果物依存関係
```
01_research_crewai.json（外部）
    ↓
02_structure.md（structurer）
    ↓
03_draft.md（drafter）
    ↓
04_review.md（critic）
    ↓
05_final.md（editor）
    ↓
80_manager_output.md（部長統合）
```

## 外部委譲指示書
`15_external_instructions/crewai_command.sh` を参照
