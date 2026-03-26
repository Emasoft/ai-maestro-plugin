---
name: graph-query
description: Queries the code graph database to understand component relationships, dependencies, and the impact of changes. Use when the user asks to "find callers", "check dependencies", "what uses this", or when exploring codebase structure to avoid breaking changes.
allowed-tools: Bash
compatibility: Requires AI Maestro (aimaestro.dev) with Bash shell access
metadata:
  author: 23blocks
  version: 2.0.0
---

# AI Maestro Code Graph Query

Query the indexed code graph to understand symbols, call chains, dependencies, and relationships before making changes. All commands auto-detect your agent ID from the tmux session.

---

## Use Cases

### 1. Understand a Code Symbol

**When:** You need to know what a class, function, module, or variable is, where it is defined, and what it does.

```bash
graph-describe.sh <symbol>
```

**Examples:**
```bash
graph-describe.sh User
graph-describe.sh process_payment
graph-describe.sh AuthController
```

**Returns:** Symbol type, file location, documentation, attributes, and a summary of its role in the codebase.

---

### 2. Find All Functions That Call X (Callers)

**When:** You are about to change a function's signature, return type, or behavior and need to know every call site that will be affected.

```bash
graph-find-callers.sh <function>
```

**Examples:**
```bash
graph-find-callers.sh process_payment
graph-find-callers.sh validate_token
```

**Returns:** List of functions/methods that call the target, with file paths.

---

### 3. Find All Functions X Calls (Callees)

**When:** You want to understand what a function depends on -- its downstream calls -- to trace data flow or debug failures.

```bash
graph-find-callees.sh <function>
```

**Examples:**
```bash
graph-find-callees.sh handle_request
graph-find-callees.sh create_order
```

**Returns:** List of functions/methods called by the target, with file paths.

---

### 4. Trace the Path Between Two Symbols

**When:** You need to understand how two components are connected through the call graph, e.g., "How does a user request reach the database layer?"

```bash
graph-find-path.sh <from> <to>
```

**Examples:**
```bash
graph-find-path.sh handle_request save_to_db
graph-find-path.sh LoginController UserModel
```

**Returns:** The chain of calls connecting the two symbols, or reports that no path exists.

---

### 5. Find Related Code (Related Symbols and Associations)

**When:** You need to discover symbols connected to a target -- parent classes, mixins, interfaces, child classes, or model associations (belongs_to, has_many, etc.).

**Find related symbols (extends, includes, inherits):**
```bash
graph-find-related.sh <symbol>
```

**Find model associations (belongs_to, has_many, has_one):**
```bash
graph-find-associations.sh <symbol>
```

**Examples:**
```bash
graph-find-related.sh BaseController    # child classes, mixins
graph-find-associations.sh User         # has_many :posts, belongs_to :org
```

**Returns:** Lists of related symbols grouped by relationship type.

---

### 6. Find All Classes, Functions, or Modules by Type

**When:** You want to list every symbol of a particular kind -- all models, all controllers, all hooks, etc.

```bash
graph-find-by-type.sh <type>
```

**Supported types:** `model`, `serializer`, `controller`, `service`, `job`, `concern`, `component`, `hook`, `module`, `class`, `function`

**Examples:**
```bash
graph-find-by-type.sh model
graph-find-by-type.sh controller
graph-find-by-type.sh hook
```

**Returns:** All symbols of the requested type, with file paths.

---

### 7. Find Serializer Classes

**When:** You changed a model and need to know which serializers expose its fields, so you can update them to match.

```bash
graph-find-serializers.sh
```

**Examples:**
```bash
graph-find-serializers.sh           # list all serializers
graph-find-serializers.sh User      # serializers for User model
```

**Returns:** Serializer classes, optionally filtered to those associated with a specific model.

---

### 8. Index the Code Graph for a Project

**When:** You need to build or refresh the graph database so the query commands have up-to-date data. Run this after cloning a repo, after large refactors, or when queries return stale results.

```bash
graph-index-delta.sh [project-path]
```

**Examples:**
```bash
graph-index-delta.sh                    # index current project
graph-index-delta.sh /path/to/project   # index a specific project
```

**First run:** Performs a full index and initializes file-tracking metadata.
**Subsequent runs:** Only re-indexes new, modified, or deleted files (delta mode).

**Performance:**
- Full index: 30-120 seconds (1000+ files)
- Delta index: 1-5 seconds (5-10 changed files)

There is no separate `graph-index.sh`. This single command handles both full and incremental indexing.

---

### 9. Combined Search: Graph + Memory + Docs

**When:** You want a thorough understanding of a symbol -- not just its code structure, but also prior conversations, documentation, and design context.

**Pattern:**
```bash
# Step 1: Graph structure
graph-describe.sh PaymentService
graph-find-callers.sh process_payment
graph-find-callees.sh process_payment

# Step 2: Memory search (if agent-memory skill is available)
memory-search.sh "PaymentService"

# Step 3: Documentation search (if docs-graph skill is available)
docs-search.sh "payment processing"
```

This combined pattern gives you the full picture: code structure from the graph, historical context from memory, and design intent from documentation.

---

## Automatic Query Behavior

When you read a code file, query the graph immediately before proceeding:

| File Type | Query Immediately |
|-----------|-------------------|
| Model / data class | `graph-describe.sh`, `graph-find-serializers.sh`, `graph-find-associations.sh` |
| Controller / handler | `graph-describe.sh`, `graph-find-callees.sh` |
| Service / business logic | `graph-describe.sh`, `graph-find-callers.sh` |
| Function (any) | `graph-find-callers.sh`, `graph-find-callees.sh` |
| Serializer / transformer | `graph-describe.sh` |
| Any class | `graph-find-related.sh` |

**Rule:** Read file -> Query graph -> Then proceed. The graph query takes 1 second. A broken deployment takes hours to fix.

---

## Troubleshooting

**Scripts not found:**
```bash
which graph-describe.sh
ls -la ~/.local/bin/graph-*.sh
```
Scripts are installed to `~/.local/bin/`. If missing, run the installer:
```bash
~/ai-maestro/install-graph-tools.sh
```

**API connection fails:**
- Verify AI Maestro is running: `curl http://127.0.0.1:23000/api/hosts/identity`
- Verify your agent is registered (scripts auto-detect from tmux session)
- Symbol names are case-sensitive

**Graph returns stale results:**
- Re-index: `graph-index-delta.sh`

**Graph is unavailable:**
- Inform the user: "Graph unavailable, proceeding with manual analysis -- increased risk of missing dependencies."

**Helper script:**
- `graph-helper.sh` is sourced by all `graph-*.sh` scripts. It provides shared API functions (`graph_query`, `init_graph`). Located in `~/.local/bin/` (installed) or `plugin/plugins/ai-maestro/scripts/` (source).
