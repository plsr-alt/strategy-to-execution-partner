# Agent Factory — 圧縮知識（Claude Code + 自環境）
> Sources: sources/001〜099 / 生成: 2026-03-05
> タグ: ✅検証済 = sources照合済み / ⚠️公式未記載 = 推測 / ⚠️矛盾あり = 両記述を併記

---

## 1. Claude Code アーキテクチャ全体像

### 1.1 アジェンティックループ ✅
```
prompt → gather context → take action → verify results → repeat until done
```
- ユーザーはいつでも割り込み可能（Esc/Enter）
- 複雑さに応じてループ数は自動調整
- エンジン: models（推論）+ tools（実行）の2コンポーネント

### 1.2 ツール5カテゴリ ✅
| カテゴリ | できること |
|---------|-----------|
| File operations | Read/Edit/Write/Rename |
| Search | Glob（ファイル名）/ Grep（内容正規表現） |
| Execution | Bash（任意コマンド・git・テスト） |
| Web | WebFetch/WebSearch |
| Code intelligence | 型エラー・定義ジャンプ（プラグイン必要） |

### 1.3 プロジェクトへのアクセス範囲 ✅
起動ディレクトリ配下のファイル・端末コマンド・git状態・CLAUDE.md・Auto Memory（MEMORY.md先頭200行）・設定した拡張機能

---

## 2. メモリ・指示管理

### 2.1 2種のメモリ ✅
| | CLAUDE.md | Auto Memory |
|--|--|--|
| 書き手 | 人間 | Claude |
| 内容 | ルール・指示 | 学習・パターン |
| 読込 | 毎セッション全体 | MEMORY.md先頭200行 |
| 用途 | 標準・ワークフロー | ビルドコマンド・好みの蓄積 |

### 2.2 CLAUDE.md配置（優先度: より具体的 > 広域） ✅
```
/Library/Application Support/ClaudeCode/CLAUDE.md  ← 組織Managed（除外不可）
./CLAUDE.md または ./.claude/CLAUDE.md              ← プロジェクト（git管理）
~/.claude/CLAUDE.md                                 ← ユーザー個人（全プロジェクト）
./CLAUDE.local.md                                   ← 個人・プロジェクト限定（gitignore）
```

### 2.3 効果的なCLAUDE.md ✅
- **200行以内**を目標（超えると遵守率低下）
- 具体的・検証可能な指示（「2スペースインデント」>「きれいにフォーマット」）
- `@path/to/file` でファイルをimport（最大5ホップ再帰）
- `.claude/rules/` でトピック別に分割可能
- `paths` frontmatterでファイルパス条件付きルール化可能

### 2.4 Auto Memory ✅
- 保存先: `~/.claude/projects/<project>/memory/`
- MEMORY.md = インデックス（先頭200行のみ毎回読込）
- トピックファイル（debugging.md等）= オンデマンド読込
- 無効化: `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`

---

## 3. 設定システム

### 3.1 スコープと優先度 ✅
```
Managed（最高・上書き不可） > CLIフラグ > Local > Project > User（最低）
```

### 3.2 ファイル場所 ✅
```
~/.claude/settings.json          ← User（個人・全プロジェクト）
.claude/settings.json            ← Project（git管理・チーム共有）
.claude/settings.local.json      ← Local（gitignore・個人上書き）
managed-settings.json            ← Managed（システムディレクトリ・IT配布）
  macOS: /Library/Application Support/ClaudeCode/
  Linux: /etc/claude-code/
  Windows: C:\Program Files\ClaudeCode\
```

### 3.3 配列設定は結合（置換でない） ✅
同一配列設定が複数スコープ → **連結・重複除去**（例: permissions.allow）

### 3.4 重要な環境変数 ✅
| 変数 | 用途 |
|-----|------|
| ANTHROPIC_API_KEY | APIキー |
| CLAUDE_CODE_EFFORT_LEVEL | low/medium/high（Opus4.6・Sonnet4.6） |
| CLAUDE_CODE_DISABLE_AUTO_MEMORY | 1でAuto Memory無効 |
| CLAUDE_CODE_DISABLE_BACKGROUND_TASKS | 1でバックグラウンドタスク無効 |
| BASH_DEFAULT_TIMEOUT_MS | Bash タイムアウト |
| CLAUDE_AUTOCOMPACT_PCT_OVERRIDE | 自動コンパクト閾値（%） |

---

## 4. 権限システム

### 4.1 ツール種別と承認 ✅
| ツール種別 | 承認 | 持続 |
|-----------|------|------|
| 読取専用（Read/Grep） | 不要 | N/A |
| Bashコマンド | 必要 | プロジェクト×コマンドで恒久 |
| ファイル編集（Edit/Write） | 必要 | セッション終了まで |

### 4.2 権限モード ✅
| モード | 動作 |
|--------|------|
| default | 初回使用ごとにプロンプト |
| acceptEdits | ファイル編集を自動承認 |
| plan | 読取専用のみ（計画作成） |
| dontAsk | 事前承認以外を自動拒否 |
| bypassPermissions | 全チェックをスキップ（隔離環境のみ） |

### 4.3 ルール構文 ✅
```
評価順: deny → ask → allow（最初にマッチしたルールが勝つ）

Bash(npm run test *)    ← プレフィックスワイルドカード
Read(./.env)            ← 特定ファイル
WebFetch(domain:x.com)  ← ドメイン制限
mcp__servername__tool   ← MCP特定ツール
Agent(Explore)          ← サブエージェント制御
```

### 4.4 パスルール ✅
```
//path  ← 絶対パス（/から）
~/path  ← ホームディレクトリ相対
/path   ← プロジェクトルート相対（注: /Users/alice はプロジェクトルート相対）
path    ← カレントディレクトリ相対
```

---

## 5. フックシステム

### 5.1 18のフックイベント ✅
**セッション系**: SessionStart / SessionEnd
**ツール系**: PreToolUse / PostToolUse / PostToolUseFailure / PermissionRequest
**エージェント系**: SubagentStart / SubagentStop / TeammateIdle
**その他**: UserPromptSubmit / Stop / Notification / TaskCompleted / InstructionsLoaded / ConfigChange / WorktreeCreate / WorktreeRemove / PreCompact

### 5.2 設定構造 ✅
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{"type": "command", "command": "./script.sh"}]
      }
    ]
  }
}
```
matcher = regex（省略/"*" → 全マッチ）

### 5.3 終了コードと動作 ✅
| 終了コード | 意味 |
|-----------|------|
| 0 | 許可（出力不要） |
| 2 | ブロック（stderrをClaudeに返す） |
| その他 | エラー（無視、ツール続行） |

### 5.4 フック場所 ✅
~/.claude/settings.json（全プロジェクト）/ .claude/settings.json（プロジェクト）/ スキル・エージェントfrontmatter（そのコンポーネント有効中のみ）

---

## 6. MCP（Model Context Protocol）

### 6.1 概要 ✅
外部ツール・DB・APIをClaude Codeに接続するオープン標準

### 6.2 追加方法 ✅
```bash
# HTTPサーバー（推奨）
claude mcp add --transport http <name> <url>

# stdioサーバー（ローカルプロセス）
# ※全オプションはサーバー名の前に；-- でコマンドと分離
claude mcp add --transport stdio --env KEY=VAL <name> -- npx -y package

# SSE（非推奨・HTTP使用を推奨）
claude mcp add --transport sse <name> <url>
```

### 6.3 スコープ ✅
| スコープ | 保存先 | 用途 |
|---------|--------|------|
| local（デフォルト） | ~/.claude.json | 個人・現プロジェクトのみ |
| project | .mcp.json（git管理） | チーム共有 |
| user | ~/.claude.json | 個人・全プロジェクト |

### 6.4 環境変数展開 ✅
.mcp.json内で `${VAR}` と `${VAR:-default}` が使用可能（command/args/env/url/headers内）

### 6.5 MCP Tool Search ✅
- MCP定義がコンテキスト10%超 → 自動有効化（デフォルト: auto）
- ENABLE_TOOL_SEARCH=auto/true/false で制御
- 対応モデル: Sonnet 4以降, Opus 4以降

---

## 7. サブエージェント

### 7.1 組み込みサブエージェント ✅
| エージェント | モデル | ツール | 用途 |
|------------|-------|-------|------|
| Explore | Haiku | 読取専用 | コードベース探索 |
| Plan | 継承 | 読取専用 | プランモード用調査 |
| general-purpose | 継承 | 全て | 複雑な研究・変更 |

### 7.2 ファイル形式 ✅
```markdown
---
name: agent-name
description: When Claude should delegate (⚠️ write precisely for auto-delegation)
tools: Read, Grep, Glob, Bash
model: sonnet  # sonnet/opus/haiku/inherit
permissionMode: default  # default/acceptEdits/dontAsk/bypassPermissions/plan
maxTurns: 10
skills:
  - skill-name  # full content injected at startup
memory: user  # user/project/local
background: false
isolation: worktree  # isolated git worktree
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: ./validate.sh
---

System prompt here...
```

### 7.3 保存場所と優先度 ✅
CLIフラグ > .claude/agents/ > ~/.claude/agents/ > Plugin

### 7.4 重要な制限 ✅
- **サブエージェントは他のサブエージェントをスポーンできない**
- ネスト委譲が必要な場合 → Skillsを使うかメイン会話からチェーン

### 7.5 永続メモリ ✅
| スコープ | 場所 |
|---------|------|
| user | ~/.claude/agent-memory/<name>/ |
| project | .claude/agent-memory/<name>/ |
| local | .claude/agent-memory-local/<name>/ |
有効時: MEMORY.md先頭200行をセッション開始時にロード

### 7.6 フォアグラウンド vs バックグラウンド ✅
- フォアグラウンド: メイン会話をブロック、権限プロンプトが通過
- バックグラウンド: 並行実行、権限を事前承認・それ以外は自動拒否
- Ctrl+B: 実行中タスクをバックグラウンド化

---

## 8. スキル（Skills）

### 8.1 概要 ✅
Claude の能力を拡張するMarkdownファイル。自動呼び出し or `/skill-name` で起動。

### 8.2 保存場所 ✅
```
~/.claude/skills/<name>/SKILL.md   ← 個人（全プロジェクト）
.claude/skills/<name>/SKILL.md     ← プロジェクト
Plugin/skills/<name>/SKILL.md      ← プラグイン（名前空間で衝突なし）
```

### 8.3 SKILL.md frontmatter ✅
```yaml
---
name: skill-name
description: 用途の説明（Claude自動選択のための情報）
disable-model-invocation: true  # Claude自動起動を防ぐ（手動のみ）
user-invocable: false           # /メニューから非表示（Claude自動のみ）
allowed-tools: Read, Grep       # 許可ツール（承認不要）
model: sonnet
context: fork                   # 分離サブエージェントで実行
agent: Explore                  # context:fork時のエージェント種別
---
```

### 8.4 呼び出し制御 ✅
| 設定 | 人間が呼べる | Claudeが呼べる | コンテキスト |
|------|-----------|--------------|------------|
| デフォルト | ✅ | ✅ | 説明常時あり・本文は呼出時 |
| disable-model-invocation: true | ✅ | ❌ | コンテキストなし |
| user-invocable: false | ❌ | ✅ | 説明常時あり・本文は呼出時 |

### 8.5 引数 ✅
```
$ARGUMENTS        ← 全引数
$ARGUMENTS[0]/$0  ← 0ベースインデックス
```

### 8.6 動的コンテキスト注入 ✅
```yaml
PR diff: !`gh pr diff`   ← Claude実行前にシェルコマンドを実行し結果を挿入
```
※前処理（Claudeは最終結果のみ受け取る）

### 8.7 context: fork ✅
- Skill内容が分離サブエージェントへのプロンプトになる
- 会話履歴にはアクセス不可
- agent フィールド: 使用するサブエージェント種別

### 8.8 組み込みスキル ✅
| スキル | 説明 |
|-------|------|
| /simplify | 変更ファイルのコード品質改善（並列エージェント） |
| /batch | 大規模並列コードベース変更（5-30単位・worktree分離） |
| /debug | 現セッションのデバッグ |
| /claude-api | Claude APIリファレンス読込 |

---

## 9. 自環境固有ルール

### 9.1 分業ルール ⚠️公式未記載（自環境設定）
- **Claude Code**: 思考・判断・指示・レビュー・軽い修正
- **WSL+Groq**: コード実装・長文生成・市場調査・重い処理
- 実装タスク前に必ずGroq委譲可否を確認

### 9.2 ファイル操作ルール ⚠️公式未記載（自環境設定）
- taskフォルダ外の既存ファイルには直接アクセス禁止
- 手順: ユーザー確認 → 00_INBOX/にコピー → コピーで作業 → ユーザーが手動配置
- WSL経由ファイル生成: 必ずWSLパス形式（/mnt/c/...）を使用

### 9.3 ディレクトリ構造 ⚠️公式未記載（自環境設定）
```
task/
├── 00_INBOX/   03_PROJECTS/  06_OPERATIONS/  09_TEMPLATES/
├── 01_MANUAL/  04_RESEARCH/  07_FINANCE/     10_SKILLS/
├── 02_STRATEGY/ 05_CONTENT/  08_PEOPLE/      99_ARCHIVE/
└── .claude/ (PLAYBOOK.md, rules/, CLAUDE.md)
```

### 9.4 4ドキュメント方式 ⚠️公式未記載（自環境設定）
PLAN.md（ダンプ）→ SPEC.md（仕様確定）→ TODO.md（タスク化）→ KNOWLEDGE.md（ハマり蓄積）

### 9.5 市場調査パイプライン ⚠️公式未記載（自環境設定）
場所: 04_RESEARCH/agents/market_research_crewai/
```bash
source /home/crewai/.venv/bin/activate
python run.py --topic "テーマ" --outdir "/mnt/c/.../output" --provider groq
```
フロー: Researcher → Analyst → Writer(report.json) → Claude Code(PPT/MD)

---

## 10. コンテキスト管理

### 10.1 コンテキストウィンドウ構成 ✅
会話履歴 + ファイル内容 + コマンド出力 + CLAUDE.md + ロード済みスキル + システム指示

### 10.2 Auto Compact ✅
- ~95%で自動コンパクト（古いツール出力から削除）
- 後半の指示が失われる → 永続ルールはCLAUDE.mdへ
- `/compact focus on API changes` で焦点指定可
- CLAUDE.mdはコンパクト後に再読込（生き残る）

### 10.3 コンテキスト節約策 ✅
- Skills: 説明のみ常時ロード・本文はオンデマンド
- Subagents: 独立コンテキスト（詳細は戻ってこない）
- disable-model-invocation: true でスキル説明もコンテキストから除去
- MCP Tool Search: 自動で未使用ツール定義を遅延ロード

---

## 11. エージェント生成パターン（工場の知識）

### 11.1 典型的なエージェント構成パターン
```
読取専用エージェント: tools: Read, Grep, Glob
コードレビュアー: tools: Read, Grep, Glob, Bash / model: inherit
実装者: tools: Read, Edit, Write, Bash / permissionMode: acceptEdits
DBアナリスト: tools: Bash + PreToolUse hookで書込みブロック
調整エージェント: tools: Agent(worker, researcher), Read
```

### 11.2 サブエージェントに自動委譲させるには ✅
descriptionフィールドに「Use proactively」「Use when...」を明記

### 11.3 スキル vs サブエージェント vs CLAUDE.md の使い分け ✅
| | スキル | サブエージェント | CLAUDE.md |
|-|-------|----------------|-----------|
| 実行 | メイン会話/fork | 分離コンテキスト | 毎セッション読込 |
| 用途 | 繰り返しワークフロー | 独立タスク | 永続ルール・知識 |
| 起動 | /name or 自動 | Claude自動判断 | 常時 |
| コンテキスト | 本文はオンデマンド | 独立（サマリーのみ返る） | 常時全体 |

### 11.4 ドメイン特化エージェント生成の型
```
Phase A: ヒアリング（7ラウンド）→ reviewer が漏れ・矛盾を検証
Phase B: system-architect が設計 → reviewer が検証
Phase C: agent-builder が構築（agents/ + skills/ + rules/ + config.md）
Phase D: guide-writer が利用ガイド・クイックスタート生成
出力先: system/<domain>/
```
