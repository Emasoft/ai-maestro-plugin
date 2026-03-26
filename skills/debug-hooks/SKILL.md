---
name: debug-hooks
description: "Debug Claude Code hooks (PreToolUse, PostToolUse, etc.). Use when hooks aren't firing or produce wrong output. Trigger with /debug-hooks."
allowed-tools: "Bash(cat:*), Bash(jq:*), Bash(ls:*), Bash(chmod:*), Bash(file:*), Bash(find:*), Bash(echo:*), Bash(node:*), Bash(npx:*), Bash(tail:*), Read, Grep, Glob"
metadata:
  author: "Emasoft"
  version: "2.0.0"
---

## Overview

Systematic workflow for debugging Claude Code hooks in AI Maestro agent sessions. Covers all 7 hook types: PreToolUse, PostToolUse, SessionStart, SessionEnd, Stop, Notification, and UserPromptSubmit. Most issues are caught in the first 3 diagnostic steps.

## Prerequisites

- Claude Code installed with hooks support
- Access to `~/.claude/settings.json` (global hooks)
- `jq` available on PATH for JSON parsing
- AI Maestro plugin installed (for AI Maestro-specific hooks)

## Instructions

1. **Check hook registration** — Verify the hook exists in settings.json with correct event name (case-sensitive). Check both global (`~/.claude/settings.json`) and project-level (`.claude/settings.json`).
   ```bash
   cat ~/.claude/settings.json | jq '.hooks // empty'
   cat .claude/settings.json | jq '.hooks // empty' 2>/dev/null
   ```

2. **Verify script exists and is executable** — Check the script path and permissions.
   ```bash
   ls -la /path/to/my-hook.sh
   chmod +x /path/to/my-hook.sh  # fix if needed
   ```

3. **Test hook manually** — Pipe sample JSON to the hook script to see if it runs.
   ```bash
   echo '{"tool_name": "Write", "tool_input": {}, "session_id": "test"}' | /path/to/my-hook.sh
   ```

4. **Check for silent failures** — If hook uses background processes (`&`, `nohup`), redirect stderr to a log file to capture hidden errors.
   ```bash
   nohup my-script.sh >> /tmp/hook-debug.log 2>&1 &
   tail -f /tmp/hook-debug.log
   ```

5. **Verify event name and matcher** — Event names are case-sensitive (`PostToolUse` not `posttooluse`). Tool-specific hooks need a `matcher` field.

6. **Check AI Maestro hooks** — If AI Maestro hooks are broken, verify the hook runner exists and is registered.
   ```bash
   find ~/.claude/plugins/cache -name "ai-maestro-hook.cjs" | head -1
   ```

7. **Rebuild TypeScript hooks** — If you edited TS source, rebuild the bundle. Source edits alone don't take effect.
   ```bash
   npx esbuild src/my-hook.ts --bundle --platform=node --format=esm --outfile=dist/my-hook.mjs
   ```

## Output

- Diagnosis of why a hook is not firing or misbehaving
- Specific fix commands (chmod, path correction, matcher fix, rebuild)
- Debug log file at `/tmp/hook-debug.log` if verbose logging was added

## Error Handling

- If hook script not found: check absolute path, verify plugin installation
- If permission denied: run `chmod +x` on the script
- If hook fires for wrong tool: fix the `matcher` field in settings.json
- If hook runs twice: remove duplicate registration from global or project settings
- If AI Maestro hook missing: reinstall with `./install-messaging.sh -y`

## Examples

```
/debug-hooks
```
Runs the full 7-step diagnosis on all registered hooks.

```
/debug-hooks PostToolUse
```
Focuses diagnosis on PostToolUse hooks only.

Expected result: identification of the root cause and a specific fix command.

## Checklist

Copy this checklist and track your progress:
- [ ] Check global hooks in `~/.claude/settings.json`
- [ ] Check project hooks in `.claude/settings.json`
- [ ] Verify hook script exists at registered path
- [ ] Verify hook script is executable
- [ ] Test hook manually with sample JSON input
- [ ] Check for silent failures (background/spawn patterns)
- [ ] Verify event name casing is correct
- [ ] Verify matcher pattern matches target tool
- [ ] Rebuild TypeScript hooks if source was edited
- [ ] Remove verbose logging after debugging

## Resources

- [Detailed Reference](references/REFERENCE.md) - Full hook debugging procedures
  - Hook Event Reference (all 7 types with input/output fields)
  - PreToolUse Permission Decisions (allow/deny/ask)
  - Testing Hooks Manually (sample JSON for each event type)
  - Silent Failure Patterns (bash and TypeScript)
  - AI Maestro Hook Debugging
  - Rebuilding TypeScript Hooks
  - Common Issues Table
  - Verbose Logging Snippet
  - Hook Registration Format
