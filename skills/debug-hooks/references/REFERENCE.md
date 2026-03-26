# Debug Hooks Reference

## Table of Contents
- [Hook Event Reference](#hook-event-reference)
- [PreToolUse Permission Decisions](#pretooluse-permission-decisions)
- [Testing Hooks Manually](#testing-hooks-manually)
- [Silent Failure Patterns](#silent-failure-patterns)
- [AI Maestro Hook Debugging](#ai-maestro-hook-debugging)
- [Rebuilding TypeScript Hooks](#rebuilding-typescript-hooks)
- [Common Issues Table](#common-issues-table)
- [Verbose Logging Snippet](#verbose-logging-snippet)

---

## Hook Event Reference

| Event | Fires When | Input Fields | Output |
|-------|-----------|-------------|--------|
| `PreToolUse` | Before a tool runs | `tool_name`, `tool_input` | `permissionDecision`, `reason` (optional) |
| `PostToolUse` | After a tool runs | `tool_name`, `tool_input`, `tool_output` | (ignored) |
| `SessionStart` | Session begins | `session_id`, `cwd` | (ignored) |
| `SessionEnd` | Session ends | `session_id`, `reason`, `transcript_path` | (ignored) |
| `Stop` | Response completes | `session_id`, `stop_reason` | (ignored) |
| `Notification` | Notification sent | `title`, `body` | (ignored) |
| `UserPromptSubmit` | User sends prompt | `prompt`, `session_id` | (ignored) |

---

## PreToolUse Permission Decisions

PreToolUse hooks can return JSON to control tool execution:

```json
{"permissionDecision": "allow"}
{"permissionDecision": "deny", "reason": "Blocked by policy"}
{"permissionDecision": "ask"}
```

If no JSON returned, the default permission model applies.

---

## Testing Hooks Manually

Each hook type receives different JSON on stdin. Test with sample input:

### PreToolUse / PostToolUse

```bash
# PreToolUse — receives tool_name + tool_input
echo '{"tool_name": "Write", "tool_input": {"file_path": "/tmp/test.txt", "content": "hello"}, "session_id": "test-123"}' | /path/to/my-hook.sh

# PostToolUse — receives tool_name + tool_input + tool_output
echo '{"tool_name": "Bash", "tool_input": {"command": "ls"}, "tool_output": "file1.txt\nfile2.txt", "session_id": "test-123"}' | /path/to/my-hook.sh
```

### SessionStart / SessionEnd / Stop

```bash
# SessionStart — receives session info
echo '{"session_id": "test-123", "cwd": "/path/to/project"}' | /path/to/my-hook.sh

# SessionEnd — receives session + transcript path
echo '{"session_id": "test-123", "reason": "user_exit", "transcript_path": "/tmp/test.jsonl"}' | /path/to/my-hook.sh

# Stop — receives final message
echo '{"session_id": "test-123", "stop_reason": "end_turn"}' | /path/to/my-hook.sh
```

### UserPromptSubmit

```bash
# Receives the user's prompt text
echo '{"prompt": "write a function", "session_id": "test-123"}' | /path/to/my-hook.sh
```

### Notification

```bash
# Receives notification content
echo '{"title": "Test", "body": "Test notification", "session_id": "test-123"}' | /path/to/my-hook.sh
```

---

## Silent Failure Patterns

If your hook uses `spawn` or `&` to run in background:

```bash
# This pattern HIDES all errors!
nohup my-script.sh &>/dev/null &
```

**Fix:** Redirect output to a log file temporarily:

```bash
# Debug version — captures all output
nohup my-script.sh >> /tmp/hook-debug.log 2>&1 &

# Check the log
tail -f /tmp/hook-debug.log
```

For TypeScript/Node hooks using `spawn`:

```typescript
// BAD — hides errors
spawn(cmd, args, { detached: true, stdio: 'ignore' })

// GOOD — captures errors to a log
const logFile = fs.openSync('/tmp/hook-debug.log', 'a');
spawn(cmd, args, {
  detached: true,
  stdio: ['ignore', logFile, logFile]
});
```

---

## AI Maestro Hook Debugging

AI Maestro installs its own hooks via `hooks.json`. If these aren't working:

```bash
# Check the hook runner exists
ls -la ~/.local/bin/ai-maestro-hook.cjs 2>/dev/null || \
  find ~/.claude/plugins/cache -name "ai-maestro-hook.cjs" | head -1

# Test it directly
echo '{"session_id": "test"}' | node $(find ~/.claude/plugins/cache -name "ai-maestro-hook.cjs" | head -1) Notification

# Check it's registered
cat ~/.claude/settings.json | jq '.hooks.Notification // empty'
```

---

## Rebuilding TypeScript Hooks

If you edited TypeScript hook source, you MUST rebuild:

```bash
cd .claude/hooks
npx esbuild src/my-hook.ts \
  --bundle --platform=node --format=esm \
  --outfile=dist/my-hook.mjs
```

Source edits alone don't take effect — the shell wrapper runs the bundled `.mjs`.

---

## Common Issues Table

| Symptom | Cause | Fix |
|---------|-------|-----|
| Hook never fires | Wrong event name | Use exact casing: `PostToolUse` not `posttooluse` |
| Hook fires for wrong tool | Missing/wrong `matcher` | Set `"matcher": "Write"` for tool-specific hooks |
| Hook runs but no effect | Script error hidden | Test manually with `echo '{}' \| /path/to/hook.sh` |
| Hook works locally, not on agent | Different PATH | Use absolute paths in `command` |
| "Permission denied" | Not executable | `chmod +x /path/to/hook.sh` |
| Hook runs twice | Registered in both global + project | Remove duplicate from one settings.json |
| PreToolUse blocks everything | Bad matcher/logic | Check matcher regex, test with sample input |
| AI Maestro hook missing | Plugin not installed | Run `./install-messaging.sh -y` |

---

## Verbose Logging Snippet

Add temporary logging to any hook:

```bash
#!/usr/bin/env bash
# Add at top of any hook script for debugging
exec >> /tmp/hook-$(basename "$0").log 2>&1
echo "=== $(date) ==="
echo "Event: ${1:-unknown}"
echo "Stdin:"
cat  # dumps the JSON input
echo ""
echo "---"

# ... your actual hook logic below ...
```

Remove the logging lines when done debugging.

---

## Hook Registration Format

Hooks are registered in `settings.json` (global or project-level). Both are merged at runtime.

```bash
# Global hooks (apply to ALL sessions)
cat ~/.claude/settings.json | jq '.hooks // empty'

# Project-level hooks (apply to this project only)
cat .claude/settings.json | jq '.hooks // empty' 2>/dev/null

# AI Maestro's own hooks (from plugin)
cat ~/.claude/plugins/cache/*/ai-maestro/*/hooks/hooks.json 2>/dev/null | jq .
```

### Registration JSON Structure

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write",
        "command": "/path/to/my-hook.sh"
      }
    ],
    "SessionEnd": [
      {
        "command": "/path/to/cleanup.sh"
      }
    ]
  }
}
```

**Common registration issues:**
- Hook type misspelled (case-sensitive: `PostToolUse` not `posttooluse`)
- `command` path is relative (must be absolute or on PATH)
- Missing `matcher` when needed (tool-specific hooks)
