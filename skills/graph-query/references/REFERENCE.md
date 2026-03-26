# Graph Query Reference

## Table of Contents
- [Graph Commands](#graph-commands)
  - [graph-describe.sh](#graph-describesh)
  - [graph-find-callers.sh](#graph-find-callerssh)
  - [graph-find-callees.sh](#graph-find-calleessh)
  - [graph-find-path.sh](#graph-find-pathsh)
  - [graph-find-related.sh](#graph-find-relatedsh)
  - [graph-find-associations.sh](#graph-find-associationssh)
  - [graph-find-by-type.sh](#graph-find-by-typesh)
  - [graph-find-serializers.sh](#graph-find-serializerssh)
  - [graph-index-delta.sh](#graph-index-deltash)
  - [graph-helper.sh](#graph-helpersh)
- [Automatic Query Patterns](#automatic-query-patterns)
- [Combined Search Pattern](#combined-search-pattern)
- [Troubleshooting](#troubleshooting)

---

## Graph Commands

All commands auto-detect your agent ID from the tmux session. Scripts are installed at `~/.local/bin/graph-*.sh`.

### graph-describe.sh

**Purpose:** Understand what a code symbol is -- its type, location, documentation, and role.

```bash
graph-describe.sh <symbol>
```

**Examples:**
```bash
graph-describe.sh User
graph-describe.sh process_payment
graph-describe.sh AuthController
```

**Returns:** Symbol type, file location, documentation, attributes, and a summary of its role.

---

### graph-find-callers.sh

**Purpose:** Find all functions that call a given function. Use before changing a function's signature, return type, or behavior.

```bash
graph-find-callers.sh <function>
```

**Examples:**
```bash
graph-find-callers.sh process_payment
graph-find-callers.sh validate_token
```

**Returns:** List of calling functions/methods with file paths.

---

### graph-find-callees.sh

**Purpose:** Find all functions that a given function calls. Use to trace data flow or debug failures.

```bash
graph-find-callees.sh <function>
```

**Examples:**
```bash
graph-find-callees.sh handle_request
graph-find-callees.sh create_order
```

**Returns:** List of called functions/methods with file paths.

---

### graph-find-path.sh

**Purpose:** Trace the call chain between two symbols. Use to understand how components connect (e.g., "How does a user request reach the database?").

```bash
graph-find-path.sh <from> <to>
```

**Examples:**
```bash
graph-find-path.sh handle_request save_to_db
graph-find-path.sh LoginController UserModel
```

**Returns:** The chain of calls connecting the two symbols, or reports no path exists.

---

### graph-find-related.sh

**Purpose:** Discover symbols connected via inheritance, mixins, interfaces, or composition.

```bash
graph-find-related.sh <symbol>
```

**Examples:**
```bash
graph-find-related.sh BaseController    # child classes, mixins
```

**Returns:** Lists of related symbols grouped by relationship type.

---

### graph-find-associations.sh

**Purpose:** Find model associations (belongs_to, has_many, has_one).

```bash
graph-find-associations.sh <symbol>
```

**Examples:**
```bash
graph-find-associations.sh User         # has_many :posts, belongs_to :org
```

**Returns:** Model associations grouped by type.

---

### graph-find-by-type.sh

**Purpose:** List every symbol of a particular kind in the codebase.

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

**Returns:** All symbols of the requested type with file paths.

---

### graph-find-serializers.sh

**Purpose:** Find serializer classes, optionally filtered by model. Use after changing a model to update exposed fields.

```bash
graph-find-serializers.sh [model]
```

**Examples:**
```bash
graph-find-serializers.sh           # list all serializers
graph-find-serializers.sh User      # serializers for User model
```

**Returns:** Serializer classes with file paths.

---

### graph-index-delta.sh

**Purpose:** Build or refresh the graph database. Run after cloning, large refactors, or when queries return stale results.

```bash
graph-index-delta.sh [project-path]
```

**Examples:**
```bash
graph-index-delta.sh                    # index current project
graph-index-delta.sh /path/to/project   # index a specific project
```

**Behavior:**
- **First run:** Full index, initializes file-tracking metadata (30-120s for 1000+ files)
- **Subsequent runs:** Delta mode, only re-indexes changed files (1-5s for 5-10 files)

There is no separate `graph-index.sh`. This single command handles both full and incremental indexing.

---

### graph-helper.sh

Shared library sourced by all `graph-*.sh` scripts. Provides `graph_query` and `init_graph` functions. Located at `~/.local/bin/graph-helper.sh` (installed) or `scripts/graph-helper.sh` (source).

---

## Automatic Query Patterns

When reading a code file, query the graph immediately before proceeding:

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

## Combined Search Pattern

For thorough understanding of a symbol, combine graph queries with memory and docs:

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

---

## Troubleshooting

**Scripts not found:**
```bash
which graph-describe.sh
ls -la ~/.local/bin/graph-*.sh
```
If missing, run: `~/ai-maestro/install-graph-tools.sh`

**API connection fails:**
- Verify AI Maestro is running: `curl http://127.0.0.1:23000/api/hosts/identity`
- Verify your agent is registered (scripts auto-detect from tmux session)
- Symbol names are case-sensitive

**Graph returns stale results:**
- Re-index: `graph-index-delta.sh`

**Graph is unavailable:**
- Inform the user: "Graph unavailable, proceeding with manual analysis -- increased risk of missing dependencies."
