# Agent Factory — KNOWLEDGE

## 設計判断の記録

### 2026-03-05: 初期構築
- **判断**: フォルダは `sources/` `digest/` `system/` `pipeline/` の4つに分離
  - `digest/` は Layer 1（ガイド）と Layer 2（圧縮）の両方を格納
  - `system/` は `<domain>/` サブフォルダでドメインごとに分離
- **判断**: パイプラインテンプレートはMarkdownで定義（コード化は Phase 1 以降）
  - 最初は手動実行（Groq Playground等）でも回せる設計にした
  - 自動化スクリプトは必要になってから作る（YAGNI）
- **判断**: 既存のWSL+Groq/CrewAI基盤（PLAYBOOK.md）と統合可能な設計
  - 市場調査パイプライン（04_RESEARCH/agents/）と同じインフラを共有

## ハマりポイント
（運用しながら追記）

## Tips
- fact-checker が3回連続FAILしたら無理に通さず `⚠️検証未通過` で先に進む
- 矛盾は消さない。消すと後で判断できなくなる
- 圧縮は「構造を残してディテールを削る」。章立ては必ず維持
