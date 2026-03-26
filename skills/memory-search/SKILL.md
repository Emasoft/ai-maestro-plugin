---
name: memory-search
description: "Search conversation history and semantic memory for past discussions and decisions. Use when recalling prior context or decisions. Trigger with /memory-search."
allowed-tools: "Bash(memory-*:*), Bash(curl:*), Bash(jq:*), Bash(docs-*:*), Bash(graph-*:*), Read, Grep, Glob"
metadata:
  author: "Emasoft"
  version: "2.0.0"
---

## Overview

Searches AI Maestro's indexed conversation history using `memory-search.sh`. Supports semantic, keyword, term, and symbol search modes. Conversations are automatically indexed by the subconscious process, creating a searchable memory across all sessions.

## Prerequisites

- AI Maestro running on `localhost:23000`
- `memory-search.sh` installed at `~/.local/bin/` (via `./install-memory-tools.sh`)
- Subconscious process running and indexing conversations
- Optional: `docs-search.sh` and `graph-query.sh` for combined search

## Instructions

1. **Identify the search query** from the user's request (topic, term, code symbol, or question).

2. **Choose the search mode** based on query type:
   - `hybrid` (default) — general purpose, combines semantic + keyword
   - `semantic` — conceptually related content, different wording
   - `term` — exact text/substring matching
   - `symbol` — code identifiers (functions, classes, variables)

3. **Run the search:**
   ```bash
   memory-search.sh "<query>" --mode <mode> --limit 10
   ```

4. **Filter by speaker** if needed:
   ```bash
   memory-search.sh "<query>" --role user      # user instructions only
   memory-search.sh "<query>" --role assistant  # assistant responses only
   ```

5. **Review results** and summarize relevant findings for the user.

6. **If no results**, try: different wording, broader query, `--limit 20`, or different mode. If still nothing, the topic is genuinely new.

7. **For complete context**, optionally search docs and graph too:
   ```bash
   docs-search.sh "<query>"
   graph-query.sh "<query>"
   ```

## Output

Returns matching conversation excerpts with timestamps, session context, and relevance scores. Present results as a concise summary highlighting key decisions, prior work, and relevant context.

## Error Handling

- **No results**: Try alternate wording, broader terms, increased limit, or different mode. No results is valid — report the topic as new.
- **Script not found**: Run `./install-memory-tools.sh` to install.
- **Memory not indexed**: Check subconscious status via `curl -s http://localhost:23000/api/agents/{agentId}/subconscious/status | jq .` and trigger manual indexing if needed.
- **Connection refused**: Verify AI Maestro is running on port 23000.

## Examples

```
/memory-search authentication flow
```
Searches for past discussions about authentication using hybrid mode.

```
/memory-search "ECONNREFUSED" --mode term
```
Finds exact occurrences of the error message in conversation history.

```
/memory-search MAX_RETRY_COUNT --mode symbol
```
Locates discussions about the `MAX_RETRY_COUNT` code identifier.

## Checklist

Copy this checklist and track your progress:
- [ ] Identify search query from user request
- [ ] Select appropriate search mode
- [ ] Run memory-search.sh with chosen parameters
- [ ] Review and summarize results
- [ ] If no results, retry with alternate strategy
- [ ] Optionally search docs/graph for broader context
- [ ] Present findings to user

## Resources

- [Detailed Reference](references/REFERENCE.md) - Full CLI reference and search patterns
  - Memory Pipeline
  - CLI Reference and Options
  - Search Modes Explained
  - Use Cases with Examples
  - Combined Search Pattern
  - Troubleshooting Guide
  - Helper Scripts
