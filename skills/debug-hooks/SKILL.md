---
name: debug-hooks
user-invocable: false
description: "Debug Claude Code hooks (PreToolUse, PostToolUse, etc.). Use when hooks aren't firing or produce wrong output. Trigger with /debug-hooks.. Loaded by ai-maestro-plugin"
allowed-tools: "Bash(cat:*), Bash(jq:*), Bash(ls:*), Bash(chmod:*), Bash(file:*), Bash(find:*), Bash(echo:*), Bash(node:*), Bash(npx:*), Bash(tail:*), Read, Grep, Glob"
metadata:
  author: "Emasoft"
  version: "2.0.0"
---

## Overview

Systematic workflow for debugging Claude Code hooks. Covers all 7 hook types: PreToolUse, PostToolUse, SessionStart, SessionEnd, Stop, Notification, UserPromptSubmit.

## Prerequisites

- Claude Code with hooks support
- Access to `~/.claude/settings.json`
- `jq` on PATH; AI Maestro plugin installed

## Instructions

1. **Check registration** — Verify hook in settings.json (case-sensitive event name). Check global (`~/.claude/settings.json`) and project (`.claude/settings.json`):
   ```bash
   cat ~/.claude/settings.json | jq '.hooks // empty'
   ```

2. **Verify script** — Check path exists and is executable:
   ```bash
   ls -la /path/to/my-hook.sh && chmod +x /path/to/my-hook.sh
   ```

3. **Test manually** — Pipe sample JSON to the hook:
   ```bash
   echo '{"tool_name":"Write","tool_input":{},"session_id":"test"}' | /path/to/my-hook.sh
   ```

4. **Check silent failures** — Redirect stderr to log if hook uses background processes:
   ```bash
   nohup my-script.sh >> /tmp/hook-debug.log 2>&1 &
   ```

5. **Verify event name/matcher** — Names are case-sensitive. Tool-specific hooks need a `matcher` field.

6. **Check AI Maestro hooks** — Find the hook runner:
   ```bash
   find ~/.claude/plugins/cache -name "ai-maestro-hook.cjs" | head -1
   ```

7. **Rebuild TS hooks** — If you edited TS source, rebuild:
   ```bash
   npx esbuild src/my-hook.ts --bundle --platform=node --format=esm --outfile=dist/my-hook.mjs
   ```

## Output

- Diagnosis of why a hook is not firing or misbehaving
- Specific fix commands (chmod, path correction, matcher fix, rebuild)

## Error Handling

- Script not found: check absolute path, verify plugin installation
- Permission denied: `chmod +x` the script
- Fires for wrong tool: fix `matcher` in settings.json
- Runs twice: remove duplicate registration
- AI Maestro hook missing: reinstall with `./install-messaging.sh -y`

## Examples

```
/debug-hooks
```
Runs full 7-step diagnosis on all registered hooks.

```
/debug-hooks PostToolUse
```
Focuses on PostToolUse hooks only. Returns root cause and fix command.

## Checklist

Copy this checklist and track your progress:

- [ ] Check global hooks in `~/.claude/settings.json`
- [ ] Check project hooks in `.claude/settings.json`
- [ ] Verify hook script exists and is executable
- [ ] Test hook manually with sample JSON
- [ ] Verify event name casing and matcher pattern
- [ ] Rebuild TypeScript hooks if source was edited

## Resources

- [Detailed Reference](references/REFERENCE.md)
  - Hook Event Reference
  - PreToolUse Permission Decisions
  - Testing Hooks Manually
  - Silent Failure Patterns
  - AI Maestro Hook Debugging
  - Rebuilding TypeScript Hooks
  - Common Issues Table
  - Verbose Logging Snippet
