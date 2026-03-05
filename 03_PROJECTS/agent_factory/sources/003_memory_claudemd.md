# Memory and CLAUDE.md
Source: https://code.claude.com/docs/en/memory

## Two Memory Systems
| | CLAUDE.md | Auto Memory |
|--|--|--|
| Who writes | You | Claude |
| Contains | Instructions/rules | Learnings/patterns |
| Scope | Project/user/org | Per working tree |
| Loaded | Every session (full) | Every session (first 200 lines of MEMORY.md) |
| Use for | Standards, workflows, architecture | Build commands, debugging insights, preferences |

## CLAUDE.md File Locations (scope precedence: more specific wins)
| Scope | Location | Purpose |
|-------|----------|---------|
| Managed policy | /Library/Application Support/ClaudeCode/CLAUDE.md (macOS) | Org-wide, cannot be excluded |
| Project | ./CLAUDE.md or ./.claude/CLAUDE.md | Team-shared, in version control |
| User | ~/.claude/CLAUDE.md | Personal, all projects |
| Local | ./CLAUDE.local.md | Personal, project-specific, gitignored |

## Writing Effective CLAUDE.md
- Size: target under 200 lines per file
- Structure: use markdown headers and bullets
- Specificity: concrete and verifiable ("Use 2-space indentation" not "Format properly")
- Consistency: review for contradictions

## Import Syntax
```text
@path/to/file  ← expands file content into context at launch
@README
@docs/git-instructions.md
```
- Relative paths resolve relative to the file containing import
- Max 5 hops recursive imports
- First encounter shows approval dialog

## .claude/rules/ Directory
- Organize instructions into topic-specific files
- Rules without paths frontmatter: loaded at launch (same priority as .claude/CLAUDE.md)
- Path-specific rules (YAML frontmatter `paths` field): load when matching files opened
```yaml
---
paths:
  - "src/api/**/*.ts"
---
# API Development Rules
```
- Supports glob patterns, brace expansion, symlinks

## User-level Rules
~/.claude/rules/ — applies to every project on machine

## Auto Memory
- On by default (toggle: /memory, or `autoMemoryEnabled: false` in settings)
- Storage: ~/.claude/projects/<project>/memory/MEMORY.md + topic files
- First 200 lines of MEMORY.md loaded per session
- Topic files loaded on-demand (not at startup)
- Machine-local, not shared across machines
- Disable: `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`

## /memory Command
- Lists all CLAUDE.md and rules files loaded in current session
- Toggle auto memory on/off
- Open memory folder link
- Select any file to open in editor

## CLAUDE.md Loading Order
1. Walk up from current directory to filesystem root (load CLAUDE.md + CLAUDE.local.md)
2. Subdirectory CLAUDE.md files: loaded on-demand when Claude reads files in those dirs
3. --add-dir: additional directories (CLAUDE.md not loaded by default; set CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1 to enable)

## claudeMdExcludes
Skip specific CLAUDE.md files by path or glob:
```json
{"claudeMdExcludes": ["**/monorepo/CLAUDE.md"]}
```
Cannot exclude Managed policy CLAUDE.md.

## Subagent Memory
Subagents can maintain own auto memory (see sub-agents docs)
