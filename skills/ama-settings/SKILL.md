---
name: ama-settings
user-invocable: false
description: "Read and mutate a settings.json / settings.local.json safely via the frozen aimaestro-settings.sh CLI — get, set, delete, and atomic multi-op edit, gated to files living directly inside a .claude directory. Use instead of hand-editing settings JSON, and whenever adding a permission, an env var, or a hook entry. Trigger with 'add this permission to settings', 'set an env var in settings.json', 'add a hook entry', 'edit my Claude settings safely'. CRITICAL gotcha: --key splits on EVERY dot, so a key whose NAME contains a dot (hook matchers, Bash(node script.js:*)) is silently mis-nested — use --key-json for those. Loaded by ai-maestro-plugin"
allowed-tools: "Bash(aimaestro-settings.sh:*), Bash(jq:*), Read, Grep, Glob"
metadata:
  author: "Emasoft"
  version: "1.0.0"
---

# ama-settings — the gated settings.json editor

## Overview

`ama-settings` wraps the frozen `aimaestro-settings.sh` CLI: an in-process,
gated editor for `settings.json` / `settings.local.json` (no HTTP). Use it
instead of hand-editing the JSON — it parses, mutates and writes atomically,
so a malformed hand-edit cannot leave a settings file the harness refuses to load.

## THE GOTCHA — `--key` splits on EVERY dot, including dots inside the key NAME

`--key a.b.c` means "path `a` → `b` → `c`". That is fine until the key you want
**contains a dot**, which in Claude Code settings is routine: hook matchers and
permission strings look like `Bash(node script.js:*)` or `mcp__srv__tool`.

Measured on a throwaway file:

```bash
aimaestro-settings.sh set "$P" --key 'hooks.Bash(x.y:*)' --value dotted
# hooks keys afterwards: ['Bash(x']        ← mis-nested into hooks → Bash(x → y:*)
```

It does **not** error. It silently writes the wrong structure, and the entry you
meant to add is simply not there — a hook that never fires, or a permission that
never matches, with a settings file that still parses.

**Whenever the key name may contain a dot, use `--key-json`**, which takes the
path as an explicit array and never splits:

```bash
aimaestro-settings.sh set "$P" --key-json '["hooks","Bash(x.y:*)"]' --value dotted
# hooks keys afterwards: ['Bash(x.y:*)']   ← correct
```

Rule of thumb: `--key` for plain nested config (`env.FOO`, `model`), `--key-json`
for anything holding a matcher, a command, a filename, or a tool id.

## The path gate

`<path>` must be an **absolute** `settings.json` or `settings.local.json` living
**directly inside a `.claude` directory**. Anything else is refused with a clear
message and **exit 1** — it will not edit an arbitrary JSON file.

## Prerequisites

- `aimaestro-settings.sh` on `PATH` (installed by `install-messaging.sh`).
- It resolves the ai-maestro install that owns the implementation via
  `~/.local/share/aimaestro/install-root`. If that record is stale it exits **2**
  with "re-run install-messaging.sh" — exit 2 is an INSTALL problem, not a bad edit.

## Instructions

1. **Read before writing** — see the current shape:

   ```bash
   aimaestro-settings.sh get /abs/path/.claude/settings.json | jq '.data'
   ```

2. **Single change.** Pick `--key` vs `--key-json` per the gotcha above:

   ```bash
   aimaestro-settings.sh set "$P" --key env.MY_FLAG --value true
   aimaestro-settings.sh set "$P" --key-json '["permissions","Bash(npm test:*)"]' --value allow
   ```

   `--no-create` refuses to create missing intermediate levels — use it when you
   intend to modify something that must already exist, so a typo fails loudly
   instead of silently adding a new branch.

3. **Several related changes → one atomic `edit`**, not N `set` calls. Each `set`
   is its own read-modify-write; a sequence of them can interleave with another
   writer and lose an edit:

   ```bash
   aimaestro-settings.sh edit "$P" --ops '[
     {"op":"set","keyPath":["env","A"],"value":"1"},
     {"op":"delete","keyPath":["env","OLD"]}
   ]'
   ```

4. **Verify by reading back** — `get` the file and confirm the key landed where
   you meant, especially after any dotted-name write.

### Quick CLI Reference

| Subcommand | Form |
|---|---|
| `get <path>` | — |
| `set <path>` | `--key <dot.path>` \| `--key-json '["a","b"]'` · `--value <json-or-string>` · `[--no-create]` |
| `delete <path>` | `--key <dot.path>` \| `--key-json '[...]'` · `[--no-create]` |
| `edit <path>` | `--ops '<json array of {"op":"set"\|"delete","keyPath":[...],"value"?:...}>'` · `[--no-create]` |

## Output

JSON on STDOUT: `get` returns `{ ok, data }`; mutations return `{ success: true, … }`.

## Error Handling

| Symptom | Exit | Meaning |
|---|---|---|
| "must live directly inside a `.claude` directory" | 1 | the path gate rejected the target |
| "recorded ai-maestro install is stale or incomplete" | 2 | install problem — re-run `install-messaging.sh`, the edit never happened |
| write "succeeded" but the key isn't where you expected | 0 | almost certainly the dotted-key split — re-do with `--key-json` |

## Examples

<example>
Add a permission whose name contains dots.
→ `set "$P" --key-json '["permissions","Bash(node build.js:*)"]' --value allow` —
`--key` would have nested it under `Bash(node build` and silently lost the entry.
</example>

<example>
Two related changes that must not interleave with another writer.
→ one `edit --ops '[…]'` call, not two `set` calls.
</example>

## Scope

Editing `.claude` settings files. **Editing a hook entry does not reload it** —
project `settings.json` hook changes need a full session restart before the
harness picks them up; a successful write here is not a live hook.

## Use also

- `Skill(skill: "debug-hooks")` — when a hook was written correctly and still
  does not fire.
