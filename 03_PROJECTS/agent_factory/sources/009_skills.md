# Claude Code Skills
Source: https://code.claude.com/docs/en/skills

## What are Skills
Skills extend Claude's capabilities. Create SKILL.md with instructions.
- Claude uses when relevant (auto-invocation)
- Or invoke directly: /skill-name
- Follow Agent Skills open standard (agentskills.io)

## Bundled Skills (ship with Claude Code)
| Skill | Description |
|-------|-------------|
| /simplify | Review changed files, fix code reuse/quality/efficiency issues (parallel agents) |
| /batch <instruction> | Large-scale codebase changes in parallel (5-30 units, isolated worktrees) |
| /debug | Troubleshoot current Claude Code session |
| /claude-api | Load Claude API reference material |

## Skill File Locations
| Location | Scope |
|----------|-------|
| ~/.claude/skills/<name>/SKILL.md | Personal, all projects |
| .claude/skills/<name>/SKILL.md | Project only |
| Plugin skills/<name>/SKILL.md | Plugin scope |
| Managed | Organization-wide |

Priority: Enterprise > Personal > Project (plugin uses namespace, no conflict)

## Skill File Structure
```
skill-name/
├── SKILL.md  (required)
├── template.md
├── examples/
└── scripts/
```

## SKILL.md Format
```yaml
---
name: skill-name
description: What and when to use. Claude uses this for auto-invocation.
disable-model-invocation: true  # only you can invoke (not Claude)
user-invocable: false  # only Claude can invoke
allowed-tools: Read, Grep, Glob
model: sonnet
context: fork  # run in isolated subagent context
agent: Explore  # which subagent type (with context: fork)
argument-hint: "[issue-number]"
---

Skill instructions here...
```

## Frontmatter Fields
| Field | Default | Description |
|-------|---------|-------------|
| name | dir name | Lowercase, hyphens, max 64 chars |
| description | First paragraph | When Claude should use this skill |
| disable-model-invocation | false | Prevents Claude from auto-using |
| user-invocable | true | false = hide from / menu |
| allowed-tools | — | Tools allowed without per-use approval |
| model | — | Model to use when skill active |
| context | — | "fork" = run in isolated subagent |
| agent | general-purpose | Subagent type (with context: fork) |
| argument-hint | — | Hint in autocomplete |
| hooks | — | Hooks scoped to skill lifecycle |

## Invocation Control
| Frontmatter | You invoke | Claude invokes | Context loaded |
|-------------|-----------|----------------|----------------|
| (default) | Yes | Yes | Description always; full on invocation |
| disable-model-invocation: true | Yes | No | Description not in context |
| user-invocable: false | No | Yes | Description always; full on invocation |

## Arguments
- $ARGUMENTS: all arguments after skill name
- $ARGUMENTS[N] or $N: specific argument by 0-based index
- If $ARGUMENTS not in content: appended as "ARGUMENTS: <value>"

## Dynamic Context Injection
```yaml
!`command`  ← runs shell command, inserts output before Claude sees content
```
Example:
```yaml
PR diff: !`gh pr diff`
PR comments: !`gh pr view --comments`
```
Preprocessing, not executed by Claude.

## context: fork
- Skill runs in isolated subagent context
- Skill content = prompt driving the subagent
- No access to conversation history
- agent field: which subagent type (Explore, Plan, general-purpose, or custom)

## Control Claude's Skill Access
- Deny all: add "Skill" to deny rules
- Allow specific: Skill(commit), Skill(review-pr *)
- Deny specific: Skill(deploy *)
- Hide individual: disable-model-invocation: true

## Skill Context Budget
- Skill descriptions: 2% of context window (fallback: 16,000 chars)
- Override: SLASH_COMMAND_TOOL_CHAR_BUDGET env variable
