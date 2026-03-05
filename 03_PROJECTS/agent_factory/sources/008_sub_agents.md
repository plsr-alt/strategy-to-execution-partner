# Claude Code Subagents
Source: https://code.claude.com/docs/en/sub-agents

## What are Subagents
Specialized AI assistants with:
- Own context window
- Custom system prompt
- Specific tool access
- Independent permissions
Claude delegates matching tasks automatically.

## Built-in Subagents
| Agent | Model | Tools | Purpose |
|-------|-------|-------|---------|
| Explore | Haiku (fast) | Read-only | File discovery, code search, codebase exploration |
| Plan | Inherits | Read-only | Codebase research for planning (plan mode) |
| general-purpose | Inherits | All | Complex research + modification |
| Bash | Inherits | Terminal | Running commands in separate context |
| statusline-setup | Sonnet | — | /statusline configuration |
| Claude Code Guide | Haiku | — | Claude Code feature questions |

## Subagent File Format
Markdown files with YAML frontmatter, stored:
- User: ~/.claude/agents/ (all projects)
- Project: .claude/agents/ (team-shared, version control)
- CLI: --agents flag (session only)
- Plugin: agents/ directory

Priority: CLI > Project > User > Plugin

## Frontmatter Fields
| Field | Required | Description |
|-------|----------|-------------|
| name | Yes | Lowercase letters, hyphens |
| description | Yes | When Claude should delegate |
| tools | No | Allowed tools (inherits all if omitted) |
| disallowedTools | No | Tools to deny |
| model | No | sonnet/opus/haiku/inherit (default: inherit) |
| permissionMode | No | default/acceptEdits/dontAsk/bypassPermissions/plan |
| maxTurns | No | Max agentic turns |
| skills | No | Skills preloaded into context at startup |
| mcpServers | No | MCP servers available to subagent |
| hooks | No | Lifecycle hooks scoped to this subagent |
| memory | No | user/project/local (persistent memory) |
| background | No | true = always run as background task |
| isolation | No | "worktree" = isolated git worktree |

## Example Subagent File
```markdown
---
name: code-reviewer
description: Expert code review. Use proactively after code changes.
tools: Read, Grep, Glob, Bash
model: inherit
---

You are a senior code reviewer...
```

## Key Patterns

### Foreground vs Background
- Foreground: blocks main conversation, permission prompts pass through
- Background: concurrent, permissions pre-approved, auto-denies non-approved
- Ctrl+B: background a running task

### Persistent Memory (memory field)
| Scope | Location |
|-------|----------|
| user | ~/.claude/agent-memory/<name>/ |
| project | .claude/agent-memory/<name>/ |
| local | .claude/agent-memory-local/<name>/ |
First 200 lines of MEMORY.md loaded at session start.

### Skills in Subagents
- skills field: full skill content injected at startup (not just descriptions)
- Subagents DON'T inherit skills from parent conversation

### Preload Skills Example
```yaml
---
name: api-developer
description: Implement API endpoints following team conventions
skills:
  - api-conventions
  - error-handling-patterns
---
```

### Restrict Spawnable Subagents
```yaml
tools: Agent(worker, researcher), Read, Bash  # allowlist
```

### Disable Specific Subagents
```json
{"permissions": {"deny": ["Agent(Explore)", "Agent(my-custom)"]}}
```

### Subagent Lifecycle Hooks
In frontmatter: fire during subagent's lifecycle
In settings.json: SubagentStart/SubagentStop events

### Auto-compaction
Triggers at ~95% context capacity (same logic as main conversation)
Override: CLAUDE_AUTOCOMPACT_PCT_OVERRIDE

### Subagents CANNOT spawn other subagents
If nested delegation needed → use Skills or chain from main conversation

## Resume Subagents
Each invocation = fresh context; ask Claude to "continue" previous work
Transcripts: ~/.claude/projects/{project}/{sessionId}/subagents/agent-{agentId}.jsonl
Retained for cleanupPeriodDays (default: 30 days)
