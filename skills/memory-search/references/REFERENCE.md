# Memory Search Reference

## Table of Contents

- [Memory Pipeline](#memory-pipeline)
- [CLI Reference](#cli-reference)
- [Search Modes](#search-modes)
- [Use Cases](#use-cases)
- [Combined Search Pattern](#combined-search-pattern)
- [Troubleshooting](#troubleshooting)
- [Helper Scripts](#helper-scripts)

---

## Memory Pipeline

AI Maestro automatically indexes conversations via the subconscious process:

1. Conversations are automatically indexed (subconscious runs `index-delta` periodically)
2. Indexed conversations are available for semantic and keyword search
3. Long-term memory consolidation merges repeated themes into durable summaries

---

## CLI Reference

```
memory-search.sh <query> [--mode MODE] [--role ROLE] [--limit N]
```

| Option | Values | Default | Purpose |
|--------|--------|---------|---------|
| `<query>` | any text | (required) | What to search for |
| `--mode` | `hybrid`, `semantic`, `term`, `symbol` | `hybrid` | Search strategy |
| `--role` | `user`, `assistant` | (both) | Filter by speaker |
| `--limit` | number | `10` | Max results to return |

---

## Search Modes

| Mode | What it does | Best for |
|------|-------------|----------|
| `hybrid` | Combines semantic + keyword matching | General use (recommended default) |
| `semantic` | Vector similarity, finds conceptually related content | Different wording for same idea |
| `term` | Exact text/substring matching | Specific phrases, error messages |
| `symbol` | Code identifier matching across contexts | Function names, class names, constants |

---

## Use Cases

### 1. Semantic search for a topic

Find conceptually related past discussions, even if exact words differ.

```bash
memory-search.sh "authentication flow" --mode semantic
memory-search.sh "database migration strategy" --mode semantic
```

### 2. Exact term or symbol search

Find conversations containing a specific name, error message, or phrase.

```bash
memory-search.sh "PaymentService" --mode term
memory-search.sh "ECONNREFUSED" --mode term
memory-search.sh "MAX_RETRY_COUNT" --mode symbol
```

### 3. Check if something was discussed before

Before starting any task, search memory to avoid repeating past work.

```bash
memory-search.sh "caching"
memory-search.sh "cache" --mode term
```

### 4. Find previous decisions

Locate past agreements, design choices, or conclusions.

```bash
memory-search.sh "decided" --mode semantic
memory-search.sh "architecture decision" --mode semantic
memory-search.sh "preferred approach" --role user
```

### 5. Recall past session work

Find prior implementations or progress on a feature.

```bash
memory-search.sh "implementation progress" --mode semantic
memory-search.sh "solution" --role assistant --limit 5
```

---

## Combined Search Pattern

For complete context, search multiple sources:

```bash
# Step 1: What did we discuss about this?
memory-search.sh "authentication"

# Step 2: What do the project docs say?
docs-search.sh "authentication"

# Step 3: What concepts are connected?
graph-describe.sh "authentication"
```

Always start with memory search. If memory has no results, fall back to docs.

---

## Troubleshooting

### No results found

1. **Try different wording:**

   ```bash
   memory-search.sh "auth" --mode term
   memory-search.sh "login system" --mode semantic
   ```

2. **Broaden the search** — remove specific qualifiers:

   ```bash
   memory-search.sh "authentication error"
   ```

3. **Increase the limit:**

   ```bash
   memory-search.sh "deployment" --limit 20
   ```

4. **Topic may be genuinely new.** No results is valid information.

### Memory not indexed

If searches consistently return nothing for topics you know were discussed:

1. **Check subconscious is running:**

   ```bash
   curl -s http://localhost:23000/api/agents/{agentId}/subconscious/status | jq .
   ```

2. **Verify script is installed:**

   ```bash
   which memory-search.sh
   ```

3. **Re-install if missing:**

   ```bash
   ./install-memory-tools.sh
   ```

4. **Trigger manual indexing:**

   ```bash
   curl -s -X POST http://localhost:23000/api/agents/{agentId}/subconscious/index-delta
   ```

---

## Helper Scripts

This skill relies on `memory-helper.sh`, sourced automatically by tool scripts. It provides `memory_query` and `init_memory` functions.

- Installed location: `~/.local/bin/memory-helper.sh`
- Source location: `scripts/memory-helper.sh` (in ai-maestro repo)
