# Agent Factory — TODO

## Phase 0: 基盤構築 ✅
- [x] フォルダ構造作成（sources/digest/system/pipeline/）
- [x] CLAUDE.md（PJルール・タグ規約・パイプライン定義）
- [x] pipeline/section_writer.md（執筆プロンプト）
- [x] pipeline/fact_checker.md（検証プロンプト）
- [x] pipeline/run_pipeline.md（実行手順）
- [x] pipeline/generator_prompt.md（ジェネレーターテンプレート）
- [x] 4ドキュメント（PLAN/SPEC/TODO/KNOWLEDGE）

## Phase 1: 初回ソース取得 ✅ 2026-03-05完了
- [x] 対象ドキュメントの選定（Claude Code公式 + 自環境ソース）
- [x] WebFetch で主要10ページ + 全59ページインデックスを取得
- [x] sources/ に14ファイル格納（001〜099の命名規則適用）
  - 001_overview.md / 002_how_it_works.md / 003_memory_claudemd.md
  - 004_settings.md / 005_permissions.md / 006_hooks.md
  - 007_mcp.md / 008_sub_agents.md / 009_skills.md
  - 010_common_workflows.md / 091_self_claudemd.md / 092_self_playbook.md
  - 099_full_page_index.md / 000_index.md

## Phase 2: 設計ガイド生成 ✅ 2026-03-05完了（Phase 3と統合）
- [x] sources/ 全ファイルをもとに11セクション分の知識を抽出
- [x] writer/checker パターンでタグ付け（✅検証済/⚠️公式未記載）

## Phase 3: 知識圧縮 ✅ 2026-03-05完了
- [x] digest/compressed_knowledge.md を生成（11章構成）
  - アーキテクチャ / メモリ / 設定 / 権限 / フック
  - MCP / サブエージェント / スキル / 自環境 / コンテキスト / 生成パターン
- [x] タグ規約適用（✅/⚠️）

## Phase 4: ジェネレーター稼働 ✅ 2026-03-05完了（テスト待ち）
- [x] compressed_knowledge を generator_prompt.md に埋め込み完了
- [x] Phase A-D 全構成を実装（ヒアリング→設計→構築→ガイド）
- [x] 生成後チェックリスト付与
- [ ] テストドメインで実際に試行（次のステップ）
- [ ] 出力レビュー・改善
