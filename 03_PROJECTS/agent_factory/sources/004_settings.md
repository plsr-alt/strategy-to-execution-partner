# Claude Code Settings
Source: https://code.claude.com/docs/en/settings

## Configuration Scopes (precedence: Managed > CLI args > Local > Project > User)
| Scope | Location | Shared? |
|-------|----------|---------|
| Managed | Server/plist/registry/managed-settings.json | Yes (IT-deployed) |
| User | ~/.claude/ | No |
| Project | .claude/ in repo | Yes (committed to git) |
| Local | .claude/*.local.* | No (gitignored) |

## Settings Files
- User: ~/.claude/settings.json
- Project: .claude/settings.json (committed)
- Project local: .claude/settings.local.json (gitignored)
- Managed: multiple delivery mechanisms (same JSON format, highest precedence)
  - macOS: /Library/Application Support/ClaudeCode/managed-settings.json
  - Linux/WSL: /etc/claude-code/managed-settings.json
  - Windows: C:\Program Files\ClaudeCode\managed-settings.json

## Feature Locations by Scope
| Feature | User | Project | Local |
|---------|------|---------|-------|
| Settings | ~/.claude/settings.json | .claude/settings.json | .claude/settings.local.json |
| Subagents | ~/.claude/agents/ | .claude/agents/ | — |
| MCP servers | ~/.claude.json | .mcp.json | ~/.claude.json (per-project) |
| Plugins | ~/.claude/settings.json | .claude/settings.json | — |
| CLAUDE.md | ~/.claude/CLAUDE.md | CLAUDE.md or .claude/CLAUDE.md | CLAUDE.local.md |

## Key Settings (settings.json)
```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": ["Bash(npm run lint)", "Bash(npm run test *)", "Read(~/.zshrc)"],
    "deny": ["Bash(curl *)", "Read(./.env)", "Read(./.env.*)"]
  },
  "env": {"CLAUDE_CODE_ENABLE_TELEMETRY": "1"},
  "model": "claude-sonnet-4-6",
  "language": "japanese",
  "autoUpdatesChannel": "stable"
}
```

## Permission Settings
| Key | Description |
|-----|-------------|
| allow | Array of rules to allow without prompt |
| ask | Array of rules to ask for confirmation |
| deny | Array of rules to deny |
| additionalDirectories | Additional working directories |
| defaultMode | Default permission mode |

## Array Settings Merge
When same array-valued setting in multiple scopes → arrays CONCATENATED and deduplicated (not replaced)

## Important Environment Variables
| Variable | Purpose |
|---------|---------|
| ANTHROPIC_API_KEY | API key |
| CLAUDE_CODE_EFFORT_LEVEL | low/medium/high (Opus 4.6, Sonnet 4.6) |
| CLAUDE_CODE_MAX_OUTPUT_TOKENS | Max output tokens (default: 32000, max: 64000) |
| CLAUDE_CODE_DISABLE_AUTO_MEMORY | Set 1 to disable auto memory |
| CLAUDE_CODE_DISABLE_BACKGROUND_TASKS | Set 1 to disable background tasks |
| BASH_DEFAULT_TIMEOUT_MS | Default timeout for bash commands |
| CLAUDE_CONFIG_DIR | Custom config/data directory |
| CLAUDE_CODE_ENABLE_TELEMETRY | Set 1 to enable OpenTelemetry |

## Subagent Configuration
Files: ~/.claude/agents/ (user) or .claude/agents/ (project)
Markdown files with YAML frontmatter

## System Prompt
Internal system prompt not published. Customize via CLAUDE.md or --append-system-prompt

## Verify Active Settings
Run /status inside Claude Code
