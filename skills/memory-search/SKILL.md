---
name: memory-search
description: Searches conversation history and semantic memory to find previous discussions, decisions, and context. Use when the user asks to "search memory", "what did we discuss", "remember when", "find previous conversation", "check history", or before starting new work to recall prior decisions and avoid repeating past discussions.
allowed-tools: Bash
compatibility: Requires AI Maestro (aimaestro.dev) with Bash shell access
metadata:
  author: 23blocks
  version: 2.0.0
---

# AI Maestro Memory Search

## How It Works

AI Maestro automatically indexes your conversations via the subconscious process. This creates a searchable memory of everything discussed across sessions. You search it with `memory-search.sh`.

**Memory pipeline:**
1. Conversations are automatically indexed (subconscious runs `index-delta` periodically)
2. Indexed conversations are available for semantic and keyword search
3. Long-term memory consolidation merges repeated themes into durable summaries

## Command Reference

```
memory-search.sh <query> [--mode MODE] [--role ROLE] [--limit N]
```

| Option | Values | Default | Purpose |
|--------|--------|---------|---------|
| `<query>` | any text | (required) | What to search for |
| `--mode` | `hybrid`, `semantic`, `term`, `symbol` | `hybrid` | Search strategy |
| `--role` | `user`, `assistant` | (both) | Filter by speaker |
| `--limit` | number | `10` | Max results to return |

**Search modes explained:**

| Mode | What it does | Best for |
|------|-------------|----------|
| `hybrid` | Combines semantic + keyword matching | General use (recommended default) |
| `semantic` | Vector similarity, finds conceptually related content | Different wording for same idea |
| `term` | Exact text/substring matching | Specific phrases, error messages |
| `symbol` | Code identifier matching across contexts | Function names, class names, constants |

---

## Use Cases

### 1. Search memory for a topic (semantic)

Find conceptually related past discussions, even if the exact words differ.

```bash
memory-search.sh "authentication flow" --mode semantic
memory-search.sh "database migration strategy" --mode semantic
```

Use semantic mode when you know the topic but not the exact words used before.

### 2. Search memory for an exact term (keyword)

Find conversations containing a specific name, error message, or phrase.

```bash
memory-search.sh "PaymentService" --mode term
memory-search.sh "ECONNREFUSED" --mode term
memory-search.sh "MAX_RETRY_COUNT" --mode symbol
```

Use `term` for exact text. Use `symbol` specifically for code identifiers (functions, classes, variables).

### 3. Check if something was discussed before

Before starting any task, search memory to avoid repeating past work or contradicting previous decisions.

```bash
# User says "let's add caching"
memory-search.sh "caching"
memory-search.sh "cache" --mode term
```

If results come back, review them before proceeding. If no results, this is a new topic.

### 4. Find previous decisions about a topic

Locate past agreements, design choices, or conclusions.

```bash
memory-search.sh "decided" --mode semantic
memory-search.sh "approach we agreed on" --mode semantic
memory-search.sh "architecture decision" --mode semantic
```

Filter to see only what the user said (their instructions and preferences):

```bash
memory-search.sh "preferred approach" --role user
```

### 5. Recall what was done in a past session

Find prior work, implementations, or progress on a feature.

```bash
memory-search.sh "last session" --mode semantic
memory-search.sh "implementation progress" --mode semantic
memory-search.sh "what we built" --role assistant
```

To see your own past explanations and solutions:

```bash
memory-search.sh "solution" --role assistant --limit 5
```

### 6. Combined search: memory + docs + graph

For complete context, search multiple sources. Memory tells you what was discussed; docs tell you what is documented; graph tells you how concepts relate.

```bash
# Step 1: What did we discuss about this?
memory-search.sh "authentication"

# Step 2: What do the project docs say?
docs-search.sh "authentication"

# Step 3: What concepts are connected?
graph-query.sh "authentication"
```

Always start with memory search. If memory has no results, fall back to docs.

### 7. Troubleshooting: no results found

If `memory-search.sh` returns zero results:

1. **Try different wording.** Semantic search handles synonyms, but very different phrasing may miss.
   ```bash
   memory-search.sh "auth" --mode term          # shorter keyword
   memory-search.sh "login system" --mode semantic  # different angle
   ```

2. **Broaden the search.** Remove specific qualifiers.
   ```bash
   # Instead of:
   memory-search.sh "React authentication component error handling"
   # Try:
   memory-search.sh "authentication error"
   ```

3. **Increase the limit.** Low-scoring results may still be relevant.
   ```bash
   memory-search.sh "deployment" --limit 20
   ```

4. **Check if the topic is genuinely new.** No results is valid information. Say so and proceed.

### 8. Troubleshooting: memory not indexed

If searches consistently return nothing even for topics you know were discussed:

1. **Check the subconscious is running:**
   ```bash
   curl -s http://localhost:23000/api/agents/{agentId}/subconscious/status | jq .
   ```

2. **Verify the script is installed:**
   ```bash
   which memory-search.sh
   ls -la ~/.local/bin/memory-search.sh
   ```

3. **Re-install if missing:**
   ```bash
   ./install-memory-tools.sh
   ```

4. **Trigger manual indexing** if the subconscious timer has not run yet:
   ```bash
   curl -s -X POST http://localhost:23000/api/agents/{agentId}/subconscious/index-delta
   ```

---

## Default Behavior Rule

When you receive ANY task instruction, search memory FIRST:

```
1. User gives instruction
2. Search memory for the topic mentioned
3. Review results for prior context, decisions, progress
4. Proceed with the task, building on what was already discussed
```

This prevents repeating explanations, contradicting past decisions, or restarting completed work.

## Helper Scripts

This skill relies on `memory-helper.sh`, sourced automatically by the tool scripts. It provides `memory_query` and `init_memory` functions. Located at `~/.local/bin/memory-helper.sh` (installed) or `plugin/src/scripts/memory-helper.sh` (source).
