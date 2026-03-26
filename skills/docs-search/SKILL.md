---
name: docs-search
description: "Search codebase docs for function signatures, APIs, and class definitions. Use when understanding existing patterns before coding. Trigger with /docs-search."
allowed-tools: "Bash(docs-*:*), Bash(curl:*), Read, Grep, Glob"
metadata:
  author: "Emasoft"
  version: "2.0.0"
---

## Overview

Searches auto-generated codebase documentation for function signatures, API documentation, class definitions, and code comments. Supports semantic search, keyword search, type-based filtering, and delta indexing. All commands auto-detect your agent ID from the tmux session.

**Rule: Receive Instruction -> Search Docs -> Then Proceed.** Always search docs before implementing anything to understand existing patterns and avoid duplicating code or using wrong signatures.

## Prerequisites

- AI Maestro running on `localhost:23000`
- `docs-*.sh` scripts installed in `~/.local/bin/` (run `./install-doc-tools.sh` if missing)
- Documentation indexed for your project (`docs-index.sh` or `docs-index-delta.sh`)
- Bash shell access

## Instructions

1. **Search docs when you receive any task** - run `docs-search.sh "<relevant terms>"` immediately
2. **Use semantic search** for conceptual queries: `docs-search.sh "authentication flow"`
3. **Use keyword search** for exact matches: `docs-search.sh --keyword "UserController"`
4. **Filter by type** when looking for specific constructs: `docs-find-by-type.sh function|class|module|interface`
5. **Get full doc details** with `docs-get.sh <doc-id>` after finding relevant results
6. **Check index stats** with `docs-stats.sh` to verify documentation is available
7. **Re-index after code changes** with `docs-index-delta.sh` (fast) or `docs-index.sh` (full rebuild)

## Output

Search results include document IDs, types, names, and relevance scores. Use `docs-get.sh <doc-id>` to retrieve full content including all sections, parameters, return types, and code comments.

- **Search results**: List of matching docs with ID, type, name, and score
- **Full document**: Complete content with all documented sections
- **Stats**: Index count, types breakdown, last indexed timestamp

## Error Handling

| Problem | Solution |
|---------|----------|
| Script not found | Run `./install-doc-tools.sh` to install scripts to `~/.local/bin/` |
| API connection fails | Verify AI Maestro is running: `curl http://127.0.0.1:23000/api/hosts/identity` |
| No docs indexed | Run `docs-index.sh` or `docs-index-delta.sh` for your project |
| Empty results | Try broader terms, keyword search, or different document types |
| "common.sh not found" | Re-run `./install-doc-tools.sh` to reinstall helper scripts |

If no documentation exists for a topic, inform the user and proceed with direct code analysis instead.

## Examples

```bash
# Search for a service
/docs-search PaymentService
```
Returns matching class/function docs for PaymentService.

```bash
# Keyword search for exact function name
docs-search.sh --keyword "validateUser"
```
Returns exact matches for the validateUser function.

```bash
# Find all class documentation
docs-find-by-type.sh class
```
Lists all documented classes in the indexed project.

```bash
# Delta index after code changes
docs-index-delta.sh /path/to/project
```
Indexes only new and modified files since last full index.

## Checklist

Copy this checklist and track your progress:
- [ ] Verify docs scripts are installed (`which docs-search.sh`)
- [ ] Verify AI Maestro is running (`docs-stats.sh`)
- [ ] Index project documentation if not already done
- [ ] Search docs before implementing any task
- [ ] Use keyword search for exact names, semantic for concepts
- [ ] Re-index after significant code changes

## Resources

- [Detailed Reference](references/REFERENCE.md) - Full CLI reference and search patterns
  - CLI Commands (search, indexing, listing)
  - Document Types (function, class, module, interface, component, etc.)
  - Search Patterns by User Intent
  - Combined Search Pattern with memory-search and graph-describe
  - Troubleshooting guide
