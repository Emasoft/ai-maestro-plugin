---
name: docs-search
user-invocable: false
description: "Search codebase docs for function signatures, APIs, and class definitions. Use when understanding existing patterns before coding. Trigger with /docs-search.. Loaded by ai-maestro-plugin"
allowed-tools: "Bash(docs-*:*), Bash(curl:*), Read, Grep, Glob"
metadata:
  author: "Emasoft"
  version: "2.0.0"
---

## Overview

Searches auto-generated codebase documentation for function signatures, API docs, class definitions, and code comments. Supports semantic search, keyword search, type-based filtering, and delta indexing. Commands auto-detect your agent ID from the tmux session.

**Rule: Receive Instruction -> Search Docs -> Then Proceed.** Always search docs before implementing.

## Prerequisites

- AI Maestro running on `localhost:23000`
- `docs-*.sh` scripts in `~/.local/bin/` (run `./install-doc-tools.sh` if missing)
- Documentation indexed (`docs-index.sh` or `docs-index-delta.sh`)

## Instructions

1. **Search first** — run `docs-search.sh "<terms>"` before any task
2. **Semantic search** for concepts: `docs-search.sh "authentication flow"`
3. **Keyword search** for exact names: `docs-search.sh --keyword "UserController"`
4. **Filter by type**: `docs-find-by-type.sh function|class|module|interface`
5. **Get details**: `docs-get.sh <doc-id>` for full content
6. **Check stats**: `docs-stats.sh` to verify index availability
7. **Re-index after changes**: `docs-index-delta.sh` (fast) or `docs-index.sh` (full)

## Output

- **Search results**: List with ID, type, name, relevance score
- **Full document**: All sections, parameters, return types, comments
- **Stats**: Index count, types breakdown, last indexed timestamp

## Error Handling

| Problem | Solution |
|---------|----------|
| Script not found | Run `./install-doc-tools.sh` |
| API connection fails | Verify AI Maestro: `curl http://127.0.0.1:23000/api/hosts/identity` |
| No docs indexed | Run `docs-index.sh` or `docs-index-delta.sh` |
| Empty results | Try broader terms, keyword search, or different types |

If no docs exist for a topic, proceed with direct code analysis instead.

## Examples

```bash
# Search for a service
/docs-search PaymentService
```

Returns matching class/function docs.

```bash
# Keyword search for exact function
docs-search.sh --keyword "validateUser"
```

```bash
# Delta index after code changes
docs-index-delta.sh /path/to/project
```

## Checklist

Copy this checklist and track your progress:

- [ ] Verify docs scripts installed (`which docs-search.sh`)
- [ ] Verify AI Maestro running (`docs-stats.sh`)
- [ ] Index project documentation if needed
- [ ] Search docs before implementing any task
- [ ] Re-index after significant code changes

## Resources

- [Detailed Reference](references/REFERENCE.md) - CLI Commands, Document Types, Search Patterns, Combined Search with memory-search and graph-describe, Troubleshooting
