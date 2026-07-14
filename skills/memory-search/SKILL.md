---
name: memory-search
user-invocable: false
description: "Recall prior knowledge from the markdown wiki-memory corpus via memgrep and the janitor's global recall skills. Use before acting on a recurring problem, a design decision, or a repeated alert. Trigger with /memory-search. Loaded by ai-maestro-plugin"
allowed-tools: "Bash(memgrep:*), Bash(grep:*), Bash(git:*), Bash(find:*), Read, Grep, Glob"
metadata:
  author: "Emasoft"
  version: "3.0.0"
---

## Overview

Recalls prior knowledge before acting on a recurring problem, a design
decision, or a repeated alert. **The AI Maestro conversation-transcript RAG
backend this skill used to query (a shell wrapper that hit the subconscious
index) has been permanently removed — there is no replacement CLI for it and
none is planned.** This skill is reimplemented around the two memory systems
that actually exist and are actively maintained:

1. **`memgrep`** (hosted in this repo at `scripts/memgrep/`) — a
   markdown-AST-aware grep over the curated wiki-memory corpus: symptom-indexed
   notes with `[^N]` lessons-learned, a persistent SQLite query index, and a
   keyword/boolean query DSL.
2. **The janitor's global wiki-memory skills** —
   `/janitor-memory-recall`, `/janitor-memory-write`, `/janitor-memory-update`
   (and `/janitor-memory-bootstrap` to stand up a project's wikimem the first
   time) — the authoring/maintenance layer built on top of `memgrep`.
3. **Claude Code's own built-in memory** (project `CLAUDE.md`, the
   auto-loaded per-project `MEMORY.md`) — always available, needs no extra
   tooling.

This is **curated-note recall**, not conversation-transcript search — index
by the **SYMPTOM** (the user's words / the error text), never the answer's
jargon. Full protocol: `~/.claude/rules/markdown-memory-recall.md`.

## Prerequisites

- `memgrep` on `PATH` — install with `scripts/install-memgrep.sh` (downloads a
  prebuilt binary to `~/.local/bin/memgrep`, falls back to
  `cargo install --path scripts/memgrep` if no prebuilt asset exists for the
  platform). If `memgrep` is unavailable, recall degrades to plain `grep` —
  it never blocks.
- The `ai-maestro-janitor` plugin, if you want the `/janitor-memory-*` authoring
  skills (optional — `memgrep recall`/`find` work standalone against any
  directory of markdown notes).

## Instructions

1. **Build the search roots.** Zero, one, two, or three may exist for a given
   project — skip any that don't:

   ```bash
   LOCAL_MEM="$HOME/.claude/projects/$(pwd | sed 's#[/ ]#-#g')/memory"                # machine-private
   PROJECT_MEM="$(git rev-parse --show-toplevel 2>/dev/null || pwd)/.claude/project/memory"  # git-tracked, shared
   USER_MEM="$HOME/.claude/plugins/data/ai-maestro-janitor-ai-maestro-plugins/memory" # global (fixed janitor path)
   ROOTS=(); for d in "$LOCAL_MEM" "$PROJECT_MEM" "$USER_MEM"; do [ -d "$d" ] && ROOTS+=("$d"); done
   ```

   Build an **array**, never a space-joined string — zsh (the macOS default
   shell) does not word-split an unquoted variable, so a joined string passes
   every root as one bogus path and silently returns 0 results. `"${ROOTS[@]}"`
   works in bash and zsh alike.

2. **Recall by symptom** — the user's words / the error text, NOT the fix's
   jargon:

   ```bash
   if command -v memgrep >/dev/null 2>&1; then
     memgrep recall "<symptom>" "${ROOTS[@]}"    # ranked: path — description (+ lessons)
   else
     grep -rliE "<symptom>" "${ROOTS[@]}"          # fallback: degrade, never break
   fi
   ```

3. **Read the top 1-3 notes returned.** `recall` auto-resolves and appends
   each note's `[^N]` lessons-learned by default, so one call yields the fact
   AND every WHY behind it. On conflicting facts across scopes, the more
   specific one wins: **LOCAL > PROJECT > USER**.

4. **Keyword search** when you need AND/OR/exclude instead of symptom ranking:

   ```bash
   memgrep find "+must -exclude \"exact phrase\"" "${ROOTS[@]}"   # note-level keyword DSL
   memgrep find "+term" "${ROOTS[@]}" --only-notes                # search ONLY the lessons-learned
   ```

5. **Nothing returned is valid information** — the memory doesn't exist yet.
   After solving the problem, write it with `/janitor-memory-write` (or
   `/janitor-memory-update` if it extends an existing page), routed to the
   right scope (LOCAL/PROJECT/USER — see below), rather than re-deriving the
   same fix next session.

6. **"What did we SAY in chat" vs "what did we LEARN"** — this skill answers
   the second question (curated notes). For the first, there is no separate
   transcript-search backend anymore; use Claude Code's own conversation
   history and project `CLAUDE.md`.

7. **Keep the index fresh** after a large batch of memory edits (not required
   for correctness — `recall`/`find` fall back to a live walk when the sidecar
   is stale — but faster on a large corpus):

   ```bash
   memgrep reindex "${ROOTS[@]}"   # rebuilds .memgrep/index.db (git-incremental, gitignored)
   ```

## Output

`memgrep recall`/`find` print ranked notes as `path — description`, each
followed by its resolved `[^N]` lessons-learned. Present the top 1-3 hits and
their lessons to the user; state clearly when nothing was found (new topic,
not a failure).

## Error Handling

| Problem | Solution |
|---------|----------|
| `memgrep` not found | Run `scripts/install-memgrep.sh`; use the `grep -rliE` fallback above until it's installed |
| No results | Broaden or reword — `recall` ranks on `description + title + tags`, not full body text; a genuinely new topic is valid, don't force a match |
| Wrong/stale-looking results | `memgrep reindex <memdir>` to refresh the SQLite sidecar |
| No memory directory exists yet for this project | Run `/janitor-memory-bootstrap` (if the janitor plugin is installed) to stand up the project's wikimem, or just start writing notes — the directories are created on first write |
| `/janitor-memory-*` skills unavailable | The `ai-maestro-janitor` plugin isn't installed here — `memgrep recall`/`find` still work standalone against any markdown directory |

## Examples

```
/memory-search rotator failed, had to log in manually
```

Builds the LOCAL/PROJECT/USER roots, runs `memgrep recall` (or the `grep`
fallback if `memgrep` is absent) ranked by symptom, and reports the top
matching note plus its lessons-learned.

```
/memory-search +oauth +keychain -widget
```

Runs `memgrep find "+oauth +keychain -widget" <roots>` — a mandatory-AND,
exclude-one keyword search instead of symptom ranking.

## Checklist

Copy this checklist and track your progress:

- [ ] Build the LOCAL/PROJECT/USER root array (skip roots that don't exist)
- [ ] Recall by symptom with `memgrep recall` (or the `grep` fallback)
- [ ] Read the top hits AND their `[^N]` lessons before acting
- [ ] If nothing found, note it as new information — don't guess or re-derive silently
- [ ] After solving, write/update the owning page via `/janitor-memory-write`/`update`

## Resources

- `~/.claude/rules/markdown-memory-recall.md` — the full recall protocol
  (scope routing, the wikimem hub/aspect/component model, dual-test
  evaluation)
- `/janitor-memory-recall`, `/janitor-memory-write`, `/janitor-memory-update`,
  `/janitor-memory-bootstrap` — the janitor's global authoring/maintenance
  skills this one complements
- [Detailed Reference](references/REFERENCE.md)
  - memgrep Command Reference
  - Search Modes (recall vs find)
  - Scope Routing (LOCAL / PROJECT / USER)
  - Use Cases with Examples
  - Combined Search Pattern
  - Troubleshooting Guide
  - Installation
