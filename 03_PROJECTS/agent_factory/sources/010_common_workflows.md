# Claude Code Common Workflows
Source: https://code.claude.com/docs/en/common-workflows

## Key Workflows

### Plan Mode (Shift+Tab twice, or --permission-mode plan)
- Read-only analysis before changes
- Claude uses AskUserQuestion to gather requirements
- Best for: multi-step implementation, code exploration, iteration
- Ctrl+G: open plan in text editor
- Configure as default: {"permissions": {"defaultMode": "plan"}}

### Git Worktrees (parallel sessions)
```bash
claude --worktree feature-name  # Creates .claude/worktrees/<name>/ with new branch
claude --worktree bugfix-123
claude --worktree  # auto-generates name
```
- Branches from default remote branch
- Auto-cleanup on exit (no changes → removed; changes → prompt)
- Add .claude/worktrees/ to .gitignore

### Extended Thinking (enabled by default)
- Visible in verbose mode (Ctrl+O)
- "ultrathink" keyword: sets effort to high for that turn
- Effort levels (Opus 4.6, Sonnet 4.6): low/medium/high via CLAUDE_CODE_EFFORT_LEVEL
- Toggle: /config or Option+T (macOS) / Alt+T (Windows/Linux)
- Phrases like "think hard" are regular instructions (don't allocate thinking tokens)

### Session Management
- claude --continue: resume most recent session
- claude --resume: session picker
- /rename: name current session
- /resume auth-refactor: resume by name
- Picker shortcuts: navigate, P preview, R rename, / search, A toggle all projects

### Notifications (when Claude needs attention)
Set up via /hooks → Notification event:
- macOS: `osascript -e 'display notification "..." with title "Claude Code"'`
- Linux: `notify-send 'Claude Code' '...'`
- Windows: powershell MessageBox

### Reference Files with @
- @file.js: include full file content
- @directory: directory listing
- @server:resource: MCP resource

### Unix-style Usage
```bash
cat error.txt | claude -p 'explain this error'
claude -p 'lint check' --output-format json > analysis.json
```
Output formats: text (default), json, stream-json

### Create PRs
- "create a pr for my changes" → direct PR creation
- Session auto-linked to PR; resume with: claude --from-pr <number>

### Images in Conversation
- Drag/drop, ctrl+v paste, or provide path
- Works with diagrams, screenshots, mockups, UI designs
