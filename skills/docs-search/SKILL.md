---
name: docs-search
user-invocable: false
description: "RETIRED — the AI Maestro docs indexing backend (the docs-search/docs-index shell wrappers) is permanently gone. Use the tldr CLI (tldr-code skill) for codebase docs/signatures instead. Trigger with /docs-search. Loaded by ai-maestro-plugin"
allowed-tools: "Bash(tldr:*), Read, Glob, Grep"
metadata:
  author: "Emasoft"
  version: "3.0.0"
---

## Retired — use the tldr-code skill instead

This skill used to wrap a family of shell scripts that queried an AI Maestro
documentation-index backend. That backend has been **permanently removed** —
there is no replacement CLI, and none is planned. Do not look for
`docs-search`, `docs-index`, `docs-get`, or any sibling wrapper script; they
no longer exist anywhere.

For "find the function/class/API that does X" or "understand this module
before coding" questions, use the **`tldr-code` skill** (the `tldr` CLI — an
official ai-maestro dependency, tree-sitter based, nothing to index):

| Old docs-backend command | `tldr` equivalent |
|---|---|
| `docs-search "<terms>"` (semantic search) | `tldr semantic '<terms>' <path>` |
| `docs-search --keyword "<name>"` | `tldr search '<name>' <path>` or `tldr definition --symbol <name> --file <f>` |
| `docs-find-by-type function\|class\|module\|interface\|...` | `tldr structure <path>` (functions/classes/imports per file) |
| `docs-get <doc-id>` (full document) | `tldr definition ...` to pin the location, then `Read` just those lines |
| `docs-list` / `docs-stats` | `tldr structure <path>` / `tldr health <path>` |
| `docs-index` / `docs-index-delta` (indexing step) | not needed — `tldr` parses on demand, there is no index to build |

**Rule of thumb:** default to `tldr` before reading a whole file — it extracts
only the lines that define, call, or are called by the symbol you asked about.
See the `tldr-code` skill for the full 63-command catalog
(`tldr definition|references|structure|search|impact`, plus security/quality/
metrics commands).

For *official product* documentation (a framework's or library's public API —
not this codebase), use Claude Code's built-in web lookup (`WebFetch`/
`WebSearch`) or a project's `Context7`/`Mintlify` MCP tools when installed —
not this skill.

## Resources

None — this skill has no `references/` anymore (the dead docs-backend docs
were removed). See the `tldr-code` skill for the full command catalog.
