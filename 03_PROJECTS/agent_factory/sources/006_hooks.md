# Claude Code Hooks
Source: https://code.claude.com/docs/en/hooks

## What are Hooks
User-defined shell commands, HTTP endpoints, or LLM prompts that execute automatically at lifecycle points.
Input arrives on stdin (command hooks) or POST body (HTTP hooks).

## Hook Events
| Event | When it fires |
|-------|--------------|
| SessionStart | Session begins or resumes |
| UserPromptSubmit | Prompt submitted, before Claude processes |
| PreToolUse | Before tool call executes (can BLOCK) |
| PermissionRequest | When permission dialog appears |
| PostToolUse | After tool call succeeds |
| PostToolUseFailure | After tool call fails |
| Notification | When Claude Code sends notification |
| SubagentStart | When subagent spawned |
| SubagentStop | When subagent finishes |
| Stop | When Claude finishes responding |
| TeammateIdle | Agent team teammate about to go idle |
| TaskCompleted | Task being marked complete |
| InstructionsLoaded | CLAUDE.md or rules file loaded |
| ConfigChange | Config file changes during session |
| WorktreeCreate | Worktree being created |
| WorktreeRemove | Worktree being removed |
| PreCompact | Before context compaction |
| SessionEnd | Session terminates |

## Hook Locations
| Location | Scope | Shareable |
|----------|-------|-----------|
| ~/.claude/settings.json | All projects | No |
| .claude/settings.json | Single project | Yes (commit) |
| .claude/settings.local.json | Single project | No (gitignored) |
| Managed policy | Organization | Yes (admin) |
| Plugin hooks/hooks.json | Plugin enabled | Yes (plugin) |
| Skill/agent frontmatter | While active | Yes (component file) |

## Matcher Patterns
- Regex string filtering when hooks fire
- "*", "", or omit matcher → match all
| Event | Matcher filters |
|-------|----------------|
| PreToolUse/PostToolUse | tool name (e.g., "Bash", "Edit|Write", "mcp__.*") |
| SessionStart | how started ("startup", "resume", "clear", "compact") |
| SessionEnd | why ended ("clear", "logout", etc.) |
| SubagentStart/Stop | agent type name |

## Configuration Structure
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {"type": "command", "command": ".claude/hooks/validate.sh"}
        ]
      }
    ]
  }
}
```

## Exit Code Behavior
| Exit code | Meaning |
|-----------|---------|
| 0 | Allow (no output needed) |
| 2 | Block tool call (stderr shown to Claude as reason) |
| Other | Error (ignored, tool proceeds) |

## Output to Claude (stdout JSON)
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Reason shown to Claude"
  }
}
```

## PreToolUse Input (stdin)
```json
{"tool_name": "Bash", "tool_input": {"command": "rm -rf /tmp/build"}, ...}
```

## Key Use Cases
- Block destructive commands (PreToolUse + exit 2)
- Auto-format after file edits (PostToolUse + Edit|Write matcher)
- Notifications when Claude needs attention (Notification event)
- Validate read-only queries (PreToolUse + Bash matcher)
