# Claude Code Permissions
Source: https://code.claude.com/docs/en/permissions

## Permission System
| Tool type | Approval required | Persistence |
|-----------|------------------|-------------|
| Read-only (File reads, Grep) | No | N/A |
| Bash commands | Yes | Permanent per project directory+command |
| File modification (Edit/Write) | Yes | Until session end |

## Permission Modes (set defaultMode in settings.json)
| Mode | Description |
|------|-------------|
| default | Prompts for permission on first use |
| acceptEdits | Auto-accepts file edit permissions for session |
| plan | Read-only; creates plan for approval before execution |
| dontAsk | Auto-denies unless pre-approved |
| bypassPermissions | Skips all permission prompts (isolated environment only) |

## Rule Syntax: Tool or Tool(specifier)
Evaluation order: **deny → ask → allow** (first matching rule wins)

| Rule | Effect |
|------|--------|
| Bash | All Bash commands |
| Bash(*) | Same as Bash (all) |
| Bash(npm run build) | Exact command |
| Bash(npm run test *) | Prefix match with wildcard |
| Bash(git * main) | Middle wildcard |
| Read(./.env) | Specific file |
| WebFetch(domain:example.com) | Domain-specific fetch |

## Wildcard Rules
- Space before * → word boundary: Bash(ls *) matches "ls -la" but NOT "lsof"
- No space: Bash(ls*) matches both

## Tool-Specific Rules
### Bash
- Supports glob patterns with * at any position
- Warning: URL-based constraints fragile (curl options, variables, redirects bypass them)
- Better: use deny rules for curl/wget + WebFetch with domain permission

### Read/Edit
- Follow gitignore specification
- //path → absolute from filesystem root
- ~/path → relative to home directory
- /path → relative to project root
- path or ./path → relative to current directory

### MCP
- mcp__servername → all tools from server
- mcp__servername__toolname → specific tool

### Agent (Subagents)
- Agent(Explore), Agent(Plan), Agent(my-custom) → specific subagent
- Add to deny array to disable

## Managed-Only Settings
| Setting | Description |
|---------|-------------|
| disableBypassPermissionsMode | Prevent bypassPermissions mode |
| allowManagedPermissionRulesOnly | Prevent user/project permission rules |
| allowManagedHooksOnly | Prevent user/project/plugin hooks |
| allowManagedMcpServersOnly | Only managed MCP servers |

## Working Directories
- Default: directory where claude was launched
- Add more: --add-dir <path> (startup) / /add-dir (during session) / additionalDirectories in settings
