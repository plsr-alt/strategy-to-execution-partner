# Agent Factory — SPEC

## レイヤー構造（確定）
| Layer | 内容 | 行数目安 | 格納先 |
|-------|------|---------|--------|
| 0 | 公式ドキュメント原文 | 原文のまま | `sources/` |
| 1 | 設計ガイド（矛盾併記・タグ付） | ~6,600行 | `digest/guide_*.md` |
| 2 | 圧縮知識（digest） | ~数百行 | `digest/compressed_*.md` |
| 3 | ドメイン特化エージェント | 可変 | `system/<domain>/` |

## タグ仕様（確定）
- `⚠️公式未記載` — sources/に根拠なし
- `⚠️検証未通過` — fact-checker 上限3回FAIL
- `⚠️矛盾あり` — ソース間矛盾（両方併記必須）
- `✅検証済` — fact-checker PASS

## パイプライン仕様（確定）
- fetch → write → check(loop max 3) → integrate → compress → generate
- writer と checker は必ず別コンテキスト
- WSL+Groq で実行（Claude Code はレビューのみ）

## 生成プロセス仕様（確定）
- Phase A: ヒアリング 7ラウンド（最終ラウンドはreviewer検証）
- Phase B: system-architect設計 + reviewer検証
- Phase C: agent-builder 構築
- Phase D: guide-writer ガイド生成

## 未決事項
- [ ] 最初に取り込む公式ドキュメントの対象（Claude Code? 別ドメイン?）
- [ ] WSL+Groq のスクリプト自動化の範囲
- [ ] compressed_knowledge の目標行数
