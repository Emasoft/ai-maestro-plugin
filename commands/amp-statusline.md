---
name: amp-statusline
description: Install or manage the AMP status line for Claude Code
---
# amp-statusline

Install or manage the AMP status line for Claude Code.

## Usage

```bash
amp-statusline.sh --install     # Add to Claude Code settings
amp-statusline.sh --uninstall   # Remove from Claude Code settings
amp-statusline.sh --test        # Preview output with current agent
```

## What It Shows

The status line appears at the bottom of your Claude Code terminal:

```text
alice@myteam.aimaestro.local | 3 unread
Opus 4.6 | ctx 42% | $1.23
```

- **Line 1**: Your AMP agent address and unread message count
- **Line 2**: Model name, context window usage, and session cost

## How It Finds Your Agent

The script resolves your AMP identity automatically:

1. `AMP_AGENT_ID` env var (explicit UUID)
2. `CLAUDE_AGENT_NAME` env var (AI Maestro sets this for managed agents)
3. tmux session name
4. Working directory → AI Maestro API (matches agents by their configured
   working directory)
5. Working directory → walks up to find `.claude/settings.local.json`
   containing a `CLAUDE_AGENT_NAME=` reference

If no agent is resolved, it shows "AMP: not configured (run amp-init)".

## Setup

```bash
# Install (one-time)
amp-statusline.sh --install

# Restart Claude Code to see the status bar
```

## Uninstall

```bash
amp-statusline.sh --uninstall
```
