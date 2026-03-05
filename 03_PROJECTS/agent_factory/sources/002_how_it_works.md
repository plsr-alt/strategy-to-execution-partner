# How Claude Code Works
Source: https://code.claude.com/docs/en/how-claude-code-works

## Agentic Loop
Three phases: gather context → take action → verify results
- Phases blend together; Claude uses tools throughout
- Loop adapts to task complexity (question: context only, refactor: all phases)
- User can interrupt at any point to steer

## Models
- Multiple models with different tradeoffs
- Sonnet: handles most coding tasks well
- Opus: stronger reasoning for complex architectural decisions
- Switch with `/model` or `claude --model <name>`

## Tools (5 categories)
| Category | Capabilities |
|---------|-------------|
| File operations | Read, edit, create, rename/reorganize files |
| Search | Find files by pattern, regex content search, codebase exploration |
| Execution | Shell commands, start servers, run tests, git |
| Web | Search, fetch documentation, look up errors |
| Code intelligence | Type errors, definitions, references (requires plugins) |

## Project Access
When `claude` runs in directory, it accesses:
- Files in directory and subdirectories (+ permission for elsewhere)
- Terminal commands (anything you can run from command line)
- Git state (current branch, uncommitted changes, recent history)
- CLAUDE.md (project-specific instructions)
- Auto memory (first 200 lines of MEMORY.md per session)
- Extensions (MCP servers, skills, subagents, Claude in Chrome)

## Sessions
- Each new session = fresh context window
- Saved locally (enables rewind, resume, fork)
- File snapshots before edits (reversible)
- `claude --continue`: resume most recent session
- `claude --resume`: session picker
- `--fork-session`: branch off for different approach

## Context Window
- Holds conversation, file contents, command outputs, CLAUDE.md, skills, system instructions
- Auto-compact when filling up (clears older tool outputs first)
- CLAUDE.md survives /compact (re-read from disk after compact)
- Skills: descriptions always in context, full content loads on-demand

## Permission Modes (Shift+Tab to cycle)
- Default: prompts for file edits and shell commands
- Auto-accept edits: edits without asking, still asks for commands
- Plan mode: read-only tools only (creates plan for approval)

## Checkpoints
- Every file edit is reversible (snapshots before edits)
- Press Esc twice to rewind
- Only file changes; external side effects (DB, APIs, deployments) cannot be checkpointed
