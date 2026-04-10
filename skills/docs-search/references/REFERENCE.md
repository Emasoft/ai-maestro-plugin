# Docs-Search Reference

## Table of Contents

- [CLI Commands](#cli-commands)
- [Search Commands](#search-commands)
- [Indexing Commands](#indexing-commands)
- [Document Types](#document-types)
- [Search Patterns by User Intent](#search-patterns-by-user-intent)
- [Combined Search Pattern](#combined-search-pattern)
- [Helper Scripts](#helper-scripts)
- [Troubleshooting](#troubleshooting)

---

## CLI Commands

All commands auto-detect your agent ID from the tmux session. Scripts are installed to `~/.local/bin/`.

### Search Commands

| Command | Description |
|---------|-------------|
| `docs-search.sh <query>` | Semantic search through documentation |
| `docs-search.sh --keyword <term>` | Keyword/exact match search |
| `docs-find-by-type.sh <type>` | Find docs by type (function, class, module, etc.) |
| `docs-get.sh <doc-id>` | Get full document with all sections |
| `docs-list.sh` | List all indexed documents |
| `docs-stats.sh` | Get documentation index statistics |

### Indexing Commands

| Command | Description |
|---------|-------------|
| `docs-index.sh [project-path]` | Full index documentation from project |
| `docs-index-delta.sh [project-path]` | Delta index - only new and modified files (faster) |

Use delta indexing for incremental updates. Use full `docs-index.sh` for a complete re-index.

---

## Search Commands

### Semantic Search

```bash
# Finds conceptually related docs
docs-search.sh "authentication flow"
docs-search.sh "how to validate user input"
docs-search.sh "database connection pooling"
```

### Keyword Search

```bash
# Exact term matching
docs-search.sh --keyword "authenticate"
docs-search.sh --keyword "UserController"
```

### Find by Document Type

```bash
docs-find-by-type.sh function    # All function documentation
docs-find-by-type.sh class       # All class documentation
docs-find-by-type.sh module      # All module/namespace docs
docs-find-by-type.sh interface   # All interface documentation
docs-find-by-type.sh component   # React/Vue component docs
docs-find-by-type.sh constant    # Documented constants
docs-find-by-type.sh readme      # README files
docs-find-by-type.sh guide       # Guide/tutorial documentation
```

### Get Full Document

```bash
# After finding a doc ID from search results
docs-get.sh doc-abc123
```

### List and Stats

```bash
docs-list.sh     # List all indexed documents
docs-stats.sh    # Get index statistics
```

### Index Documentation

```bash
# Index current project (auto-detected from agent config)
docs-index.sh

# Index specific project
docs-index.sh /path/to/project

# Delta index - only new/modified files (much faster)
docs-index-delta.sh
docs-index-delta.sh /path/to/project
```

---

## Document Types

| Type | Description | Sources |
|------|-------------|---------|
| `function` | Function/method documentation | JSDoc, RDoc, docstrings |
| `class` | Class documentation | Class-level comments |
| `module` | Module/namespace documentation | Module comments |
| `interface` | Interface/type documentation | TypeScript interfaces |
| `component` | React/Vue component documentation | Component comments |
| `constant` | Documented constants | Constant comments |
| `readme` | README files | README.md, README.txt |
| `guide` | Guide/tutorial documentation | docs/ folder |

---

## Search Patterns by User Intent

| User Says | IMMEDIATELY Search |
|-----------|-------------------|
| "Create a service for X" | `docs-search.sh "service"`, `docs-find-by-type.sh class` |
| "Call the Y function" | `docs-search.sh "Y"`, `docs-search.sh --keyword "Y"` |
| "Implement authentication" | `docs-search.sh "authentication"`, `docs-search.sh "auth"` |
| "Fix the Z method" | `docs-search.sh "Z" --keyword`, `docs-find-by-type.sh function` |
| Any API/function name | `docs-search.sh "<name>" --keyword` |

---

## Combined Search Pattern

When you receive ANY user instruction, combine with other skills for full context:

```bash
# 1. Search your memory first
memory-search.sh "topic"

# 2. Search documentation
docs-search.sh "topic"

# 3. Check code structure
graph-describe.sh ComponentName
```

This gives you:

- **Memory**: What was discussed before?
- **Docs**: What does the documentation say?
- **Graph**: What is the code structure?

---

## Helper Scripts

- **`docs-helper.sh`** - Sourced by all `docs-*.sh` tool scripts. Provides documentation-specific API functions (`docs_query`, `docs_index`) and initialization logic.
- Located at `~/.local/bin/` (installed) or `scripts/` (in ai-maestro repo source).
- If tool scripts fail with "common.sh not found", re-run: `./install-doc-tools.sh`

---

## Troubleshooting

### Script not found

- Check PATH: `which docs-search.sh`
- Verify scripts installed: `ls -la ~/.local/bin/docs-*.sh`
- If not found, run: `./install-doc-tools.sh`

### API connection fails

- Ensure AI Maestro is running: `curl http://127.0.0.1:23000/api/hosts/identity`
- Ensure documentation has been indexed: `docs-stats.sh`
- If no docs indexed, run: `docs-index.sh`

### Documentation is empty

- Check project has documented code (JSDoc, docstrings, comments)
- Verify project path is correct
- Re-index with: `docs-index.sh /path/to/project`

### No results found

- Inform the user: "No documentation found for X - proceeding with code analysis, but documentation may need to be generated."
- Try keyword search if semantic search returned nothing
- Try broader terms or different document types
