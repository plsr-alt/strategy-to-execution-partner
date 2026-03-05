# 自環境 CLAUDE.md ポイント（agent_factory 生成用）
Source: C:\Users\tshibasaki\Desktop\etc\work\task\CLAUDE.md

## 環境概要
- taskフォルダ: C:/Users/tshibasaki/Desktop/etc/work/task/
- OS: Windows (WSL利用可能)

## ディレクトリ構造
- 00_INBOX/ — 一時置き
- 01_MANUAL/ — 運用手順
- 02_STRATEGY/ — 経営戦略
- 03_PROJECTS/ — 案件管理（4ドキュメント方式）
- 04_RESEARCH/ — 調査
- 05_CONTENT/ — コンテンツ
- 06_OPERATIONS/ — 日常運用(DAILY/WEEKLY)
- 07_FINANCE/ — KPI・財務
- 08_PEOPLE/ — 人材
- 09_TEMPLATES/ — 雛形
- 10_SKILLS/ — 学習
- 99_ARCHIVE/ — 完了退避

## 分業ルール（重要）
- Claude Code: 考える・判断する・指示・レビュー・軽い修正
- WSL+Groq: コード実装・長文生成・市場調査・重い処理
- 重い処理は必ずWSL+Groqへ委譲（Claude Code のトークン節約）

## 4ドキュメント方式（案件管理）
PLAN.md → SPEC.md → TODO.md → KNOWLEDGE.md

## トリガー語
- おはよう/今日の予定 → DAILY.md読み→ゴール提示
- 覚えておいて → 適切なファイルに永続保存
- 記事にして → content_backlog.md + 05_CONTENT/下書き
- 納品物確認 → delivery_rules.md に従い監査

## ファイル操作ルール（重要）
- taskフォルダ外の既存ファイルには直接アクセスしない
- 操作手順: ユーザー確認 → コピーを00_INBOX/に → コピーで作業 → ユーザーが手動で配置
- WSL経由: 必ずWSLパス形式（/mnt/c/...）を使用

## 外部連携
Google Calendar → GitHub Issues → Google Sheets → Notion
フォールバック: DAILY.md / 03_PROJECTS/ / KPI.md / 00_INBOX/
