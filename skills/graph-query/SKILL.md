---
name: graph-query
user-invocable: false
description: "Query code graph DB for symbol relationships, callers, callees, and dependencies. Use when exploring codebase structure or impact. Trigger with /graph-query.. Loaded by ai-maestro-plugin"
allowed-tools: "Bash(graph-*:*), Bash(curl:*), Bash(jq:*), Read, Glob, Grep"
metadata:
  author: "Emasoft"
  version: "2.0.0"
---

## Overview

Query the indexed code graph (CozoDB) to understand symbols, call chains, dependencies, and relationships before making changes. All `graph-*.sh` commands auto-detect your agent ID from the tmux session. Scripts are installed at `~/.local/bin/`.

## Prerequisites

- AI Maestro running on `localhost:23000`
- Graph scripts installed: `~/.local/bin/graph-*.sh`
- Agent registered (auto-detected from tmux session)
- Project indexed: run `graph-index-delta.sh` if first time

## Instructions

1. **Index the project** (if not already done):

   ```bash
   graph-index-delta.sh [project-path]
   ```

2. **Query symbols** using the appropriate command:

   | Command | Purpose |
   |---------|---------|
   | `graph-describe.sh <symbol>` | What is this symbol? Type, location, docs |
   | `graph-find-callers.sh <fn>` | Who calls this function? |
   | `graph-find-callees.sh <fn>` | What does this function call? |
   | `graph-find-path.sh <from> <to>` | Call chain between two symbols |
   | `graph-find-related.sh <sym>` | Inheritance, mixins, interfaces |
   | `graph-find-associations.sh <sym>` | Model associations (has_many, belongs_to) |
   | `graph-find-by-type.sh <type>` | List all symbols of a type |
   | `graph-find-serializers.sh [model]` | Find serializer classes |

3. **Before modifying code**, always check impact:
   - Changing a function? Run `graph-find-callers.sh` first
   - Changing a model? Run `graph-find-serializers.sh` and `graph-find-associations.sh`
   - Tracing a bug? Run `graph-find-callees.sh` to follow data flow

4. **Re-index after large refactors**:

   ```bash
   graph-index-delta.sh
   ```

## Output

Each command returns structured text output with:

- Symbol names and types
- File paths and line numbers
- Relationship types (calls, inherits, associates)
- Path chains (for `graph-find-path.sh`)

## Error Handling

- **Scripts not found**: Run `~/ai-maestro/install-graph-tools.sh` to install
- **API connection fails**: Verify AI Maestro is running with `curl http://127.0.0.1:23000/api/hosts/identity`
- **Stale results**: Re-index with `graph-index-delta.sh`
- **Graph unavailable**: Inform user: "Graph unavailable, proceeding with manual analysis"

## Examples

```bash
/graph-query process_payment
```

Runs `graph-describe.sh process_payment` then `graph-find-callers.sh process_payment` to show what the function does and who calls it.

```bash
/graph-query User --associations
```

Runs `graph-find-associations.sh User` to show model relationships (has_many, belongs_to).

```bash
/graph-query handle_request save_to_db --path
```

Runs `graph-find-path.sh handle_request save_to_db` to trace the call chain.

## Checklist

Copy this checklist and track your progress:

- [ ] Project is indexed (`graph-index-delta.sh`)
- [ ] Describe the target symbol (`graph-describe.sh`)
- [ ] Check callers before changing signatures (`graph-find-callers.sh`)
- [ ] Check callees to understand dependencies (`graph-find-callees.sh`)
- [ ] Verify serializers if model changed (`graph-find-serializers.sh`)
- [ ] Re-index after refactoring (`graph-index-delta.sh`)

## Resources

- [Detailed Reference](references/REFERENCE.md)
  - Graph Commands
  - graph-describe.sh
  - graph-find-callers.sh
  - graph-find-callees.sh
  - graph-find-path.sh
  - graph-find-related.sh
  - graph-find-associations.sh
  - graph-find-by-type.sh
  - graph-find-serializers.sh
  - graph-index-delta.sh
  - graph-helper.sh
  - Automatic Query Patterns
  - Combined Search Pattern
  - Troubleshooting
