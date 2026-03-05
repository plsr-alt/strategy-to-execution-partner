# Claude Code Overview
Source: https://code.claude.com/docs/en/overview

## What is Claude Code
Claude Code is an AI-powered coding assistant (agentic coding tool) that:
- Reads codebase, edits files, runs commands
- Available in terminal, IDE (VS Code, JetBrains), desktop app, browser
- Requires Claude subscription or Anthropic Console account

## Core Capabilities
- Automate tedious tasks (tests, lint errors, merge conflicts, dependencies)
- Build features and fix bugs across multiple files
- Create commits and pull requests (git integration)
- Connect tools with MCP (Model Context Protocol)
- Customize with CLAUDE.md, skills, hooks
- Run agent teams and build custom agents
- Pipe, script, automate with CLI

## Installation
- macOS/Linux/WSL: `curl -fsSL https://claude.ai/install.sh | bash`
- Windows PowerShell: `irm https://claude.ai/install.ps1 | iex`
- Homebrew: `brew install --cask claude-code` (no auto-update)
- WinGet: `winget install Anthropic.ClaudeCode`

## Start
```bash
cd your-project
claude
```

## Surfaces
Terminal, VS Code, JetBrains, Desktop App, Web (claude.ai/code)

## Cross-surface: CLAUDE.md files, settings, MCP servers work across all surfaces
