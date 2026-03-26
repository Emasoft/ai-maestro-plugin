---
name: debug-hooks
description: >-
  Systematic hook debugging workflow for AI Maestro agents. Use when hooks
  aren't firing, producing wrong output, or behaving unexpectedly. Covers
  PreToolUse, PostToolUse, SessionStart, SessionEnd, Stop, Notification,
  and UserPromptSubmit hooks.
allowed-tools: [Bash, Read, Grep]
metadata:
  author: 23blocks
  version: "1.0"
---

# Debug Hooks

Systematic workflow for debugging Claude Code hooks in AI Maestro agent sessions.

---

## When to Use

- "My hook isn't firing"
- "Hook produces wrong output"
- "SessionEnd/Stop not working"
- "PostToolUse hook not triggering"
- "Why didn't my hook run?"
- "Notification hook not showing"
- "UserPromptSubmit hook blocked something"
- "Hook works locally but not on agent"

---

## Quick Diagnosis Checklist

Run these in order. Most issues are caught by step 1-3.

| Step | Check | Command |
|------|-------|---------|
| 1 | Is hook registered? | `cat ~/.claude/settings.json \| jq '.hooks'` |
| 2 | Does the script exist? | `ls -la <script-path>` |
| 3 | Is script executable? | `chmod +x <script-path>` |
| 4 | Does it run standalone? | `echo '{}' \| <script-path>` |
| 5 | Is the event name correct? | See Event Reference below |
| 6 | Does it match tool/event? | Check matcher pattern |
| 7 | Check for silent failures | Look at stderr/exit code |

---

## Step 1: Check Hook Registration

Hooks are registered in `settings.json` (global or project-level). Both are merged at runtime.

```bash
# Global hooks (apply to ALL sessions)
cat ~/.claude/settings.json | jq '.hooks // empty'

# Project-level hooks (apply to this project only)
cat .claude/settings.json | jq '.hooks // empty' 2>/dev/null

# AI Maestro's own hooks (from plugin)
cat ~/.claude/plugins/cache/*/ai-maestro/*/hooks/hooks.json 2>/dev/null | jq .
```

### Hook Registration Format

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

**Common issues:**
- Hook type misspelled (case-sensitive: `PostToolUse` not `posttooluse`)
- `command` path is relative (must be absolute or on PATH)
- Missing `matcher` when needed (tool-specific hooks)

---

## Step 2: Verify Script Exists and Is Executable

```bash
# Check the script exists
ls -la /path/to/my-hook.sh

# Check it's executable
file /path/to/my-hook.sh
ls -la /path/to/my-hook.sh | awk '{print $1}'

# Fix if not executable
chmod +x /path/to/my-hook.sh
```

---

## Step 3: Test Hook Manually

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

## Step 4: Check for Silent Failures

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

## Step 5: Check AI Maestro Hook (ai-maestro-hook.cjs)

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

## Step 6: Rebuild After TypeScript Edits

If you edited TypeScript hook source, you MUST rebuild:

```bash
cd .claude/hooks
npx esbuild src/my-hook.ts \
  --bundle --platform=node --format=esm \
  --outfile=dist/my-hook.mjs
```

Source edits alone don't take effect — the shell wrapper runs the bundled `.mjs`.

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

### PreToolUse Permission Decisions

PreToolUse hooks can return JSON to control tool execution:

```json
{"permissionDecision": "allow"}
{"permissionDecision": "deny", "reason": "Blocked by policy"}
{"permissionDecision": "ask"}
```

If no JSON returned, the default permission model applies.

---

## Common Issues

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

## Debugging with Verbose Logging

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
