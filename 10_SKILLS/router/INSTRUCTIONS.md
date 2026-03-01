# Skill: router

## 目的
入力を **Main** / **Runbook** に振り分ける。CLAUDE.md Section 4 に判定ロジック統合済み。

## 判定（CLAUDE.md参照）
- Runbookキーワード該当 → `[MODE: Runbook]`
- それ以外 → `[MODE: Main]`（デフォルト）
- 明示指定（`MODE:Main` / `MODE:Runbook`）があればそれに従う

## 補足
- 詳細ロジック・トリガー語・分業ルールはすべて **CLAUDE.md** に集約
- 本ファイルの単独参照は不要（CLAUDE.md で完結）
