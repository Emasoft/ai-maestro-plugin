---
name: graph-query
user-invocable: false
description: "RETIRED — the CozoDB graph backend (the graph-describe/graph-find-* shell wrappers) is permanently gone. Use the codegraph MCP tools instead for symbol/caller/callee/impact queries. Trigger with /graph-query. Loaded by ai-maestro-plugin"
allowed-tools: "Read, Glob, Grep"
metadata:
  author: "Emasoft"
  version: "3.0.0"
---

## Retired — use the codegraph MCP tools instead

This skill used to wrap a family of shell scripts that queried an AI Maestro
CozoDB graph backend. That backend has been **permanently removed** — there
is no replacement CLI, and none is planned. Do not look for `graph-describe`,
`graph-find-callers`, `graph-index-delta`, or any sibling wrapper script; they
no longer exist anywhere.

For code-structure questions, reach for the **`codegraph` MCP tools** (present
whenever a project has `.codegraph/` initialized — check with
`codegraph_status`):

| Old graph-backend command | codegraph MCP tool |
|---|---|
| `graph-describe <symbol>` | `codegraph_node` (pass `includeCode: true` for source) |
| `graph-find-callers <fn>` | `codegraph_callers` |
| `graph-find-callees <fn>` | `codegraph_callees` |
| `graph-find-path <from> <to>` | `codegraph_trace` — one call returns the whole path, including dynamic-dispatch hops |
| `graph-find-related <sym>` / `graph-find-associations <sym>` | `codegraph_context` (composes search + node + callers + callees in one call) |
| `graph-find-by-type <type>` | `codegraph_search` (filter with `kind`) |
| survey several related symbols at once | `codegraph_explore` (one capped call instead of many `codegraph_node`/`Read` calls) |
| "what's in this directory" | `codegraph_files` |
| "what would break if I changed this" | `codegraph_impact` |
| re-index after a refactor | not needed — the file watcher keeps the index current (~500ms debounce behind writes) |

**Rule of thumb:** for "how does X work" / architecture / "what calls this" /
"what would break" questions, start with `codegraph_context` (broad survey) or
`codegraph_trace` (a specific flow from A to B) — both answer in 2-3 calls what
a grep+read loop would take dozens of calls to reconstruct.

If `.codegraph/` is not initialized for the project, ask the user: "This
project doesn't have CodeGraph initialized — want me to run `codegraph init -i`
to build the index?"

Fall back to `Grep`/`Glob`/`Read` only for literal-text lookups (string
contents, log messages, comments) that codegraph cannot answer structurally.

## Resources

None — this skill has no `references/` anymore (the dead graph-backend docs
were removed). See the CodeGraph section of `~/.claude/rules/` for the full
tool-selection table, or ask `codegraph_context`/`codegraph_search` directly.
