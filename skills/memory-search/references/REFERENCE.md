# Memory Search Reference

## Table of Contents

- [Why This Skill Was Reimplemented](#why-this-skill-was-reimplemented)
- [memgrep Command Reference](#memgrep-command-reference)
- [Search Modes: recall vs find](#search-modes-recall-vs-find)
- [Scope Routing (LOCAL / PROJECT / USER)](#scope-routing-local--project--user)
- [Use Cases with Examples](#use-cases-with-examples)
- [Combined Search Pattern](#combined-search-pattern)
- [Troubleshooting](#troubleshooting)
- [Installation](#installation)

---

## Why This Skill Was Reimplemented

This skill used to shell out to a `memory-search` wrapper script, which
queried the AI Maestro server's subconscious RAG index over conversation
transcripts. That backend — and its sibling `memory-helper` / `memory-tools`
wrapper scripts — has been **permanently removed**. There is no replacement
CLI and none is planned; do not wait for one or try to reconstruct the old
`/api/agents/{id}/subconscious/*` calls (this plugin never calls `/api/*`
directly — see core#11 decoupling).

What replaces it is not a drop-in swap of one search backend for another —
it's a different kind of memory entirely: a **curated, symptom-indexed
markdown wiki** (not a transcript index), searched with `memgrep` and
authored via the janitor's global `/janitor-memory-*` skills. The rest of
this reference documents that system.

---

## memgrep Command Reference

`memgrep` (Rust; owned and published by the **ai-maestro-janitor**) is grep/rg for markdown, plus memory
subcommands layered on top. Base grep flags (`-i -w -n -l -c -e PATTERN
[PATH...]`, `--json`, `--hidden`) all work as expected; the memory-relevant
subcommands are:

| Subcommand | What it does |
|---|---|
| `recall "SYMPTOM" <memdir>` | rank notes by symptom match → `path — description`, best first; each note's `[^N]` lessons appended (default-on). Query the QUESTION's words, not the answer's. |
| `find "<query>" <memdir>` | note-level `+`/`-`/wildcard/phrase keyword search (see below); `--only-notes` searches the lessons instead of pages. |
| `index <memdir>` / `reindex <memdir>` | build the persistent SQLite query index `.memgrep/index.db` (gitignored, git-incremental — re-parses only changed files); `--full` rebuilds from scratch. |
| `index --markdown <memdir>` | the legacy doc-generator → `memory-index.md` (per-note title+summary+tags+TOC+backlinks); add `--write` to write the file instead of stdout. |
| `links --broken\|--orphans\|--to N\|--from N` | link graph / semijoin over the corpus. |
| `fact [--cat/--comp/--session/--kind/--since/--until]` | query one-fact-per-line memory lines; `--with-notes` (OFF by default here) appends matched files' lessons. |

### `recall` / `find` shared flags

`--with-notes` (default ON — resolve+append `[^N]` lessons) · `--no-notes`
(body only) · `--full-notes` (keep each lesson's leading `[…]` metadata
prefix; default stripped — URLs/images always kept) · `--sort score|ocd|lmd`
(default `score` = relevance) · `--order asc|desc` (default `desc`) ·
`--since <ISO>` / `--until <ISO>` over `--date-field ocd|lmd` (default `lmd`)
· `--top N` (default 10) · `--use-index` (force the SQLite sidecar; auto-used
when fresh, else a live walk — results always correct either way).

### The `find` query DSL

`memgrep find "<query>" <memdir>` ranks whole notes (NOT line grep). The
query is ONE whitespace-separated string (quote it): `+TERM` mandatory,
`-TERM` exclude, bare `TERM` optional (ranks). A word may use `*` (wildcard:
`pro*`, `*debug`); a `"quoted phrase"` matches verbatim WITH spaces and can
itself be `+`/`-` prefixed. A `+`/`-` INSIDE a token is literal —
`pro*-debug*` is ONE wildcard term, not `pro*` minus `debug*`. Result = notes
with every `+` term and no `-` term, ranked by optional hits. `--only-notes`
runs the same DSL over the resolved lessons instead.

---

## Search Modes: recall vs find

| Mode | Use for | Ranking |
|---|---|---|
| `recall` | "have we hit this symptom before?" — the default, unprompted-recall case | symptom relevance (`description + title + tags`) |
| `find` | precise AND/OR/exclude keyword control, or searching only the lessons-learned | boolean match, then optional-term hits |

Both resolve and append `[^N]` lessons-learned by default — a `recall`/`find`
call gets you the fact AND every WHY in one shot.

---

## Scope Routing (LOCAL / PROJECT / USER)

Three possible roots, checked in this order of specificity:

| Scope | Root | Git | Contains |
|---|---|---|---|
| **LOCAL** | `~/.claude/projects/<slug>/memory/` | outside any repo, never pushed | machine-private: local paths, usernames, hostnames, secret hints, per-instance facts |
| **PROJECT** | `<git-root>/.claude/project/memory/` | tracked + pushed | machine-agnostic project knowledge any dev needs — architecture, gotchas, lessons; zero secrets/local paths |
| **USER** | the janitor's fixed plugin-data memory dir (`~/.claude/plugins/data/ai-maestro-janitor-ai-maestro-plugins/memory/`) | never in a repo | knowledge true across ALL projects |

`<slug>` is the project's absolute path with every non-alphanumeric char
replaced by `-` — the same slug the LOCAL *design/TRDD* corpus uses.

**Write-side gate** (used by `/janitor-memory-write`, not by this
recall-only skill, but worth knowing before you act on what you find): ask
*"would this fact be TRUE and USEFUL for a stranger who clones this repo on
a different machine?"* — no ⇒ LOCAL, yes ⇒ PROJECT, true everywhere ⇒ USER.
**Unsure → LOCAL** (the safe default; promoting LOCAL→PROJECT later is a
deliberate act, a leaked machine-private PROJECT note already isn't).

On a conflict between scopes, the more specific one wins: **LOCAL > PROJECT
> USER**.

---

## Use Cases with Examples

### 1. Recall before debugging a recurring problem

```bash
memgrep recall "rotator failed had to log in manually" "${ROOTS[@]}"
```

### 2. Recall, filtered to recent notes, sorted by last-modified

```bash
memgrep recall "rotator" "${ROOTS[@]}" --since 2026-06-01 --sort lmd
```

### 3. Exact AND/exclude keyword search

```bash
memgrep find "+rotator +keychain -widget" "${ROOTS[@]}"
```

### 4. Mandatory phrase + optional ranking term

```bash
memgrep find '+"old approach" retry' "${ROOTS[@]}"
```

### 5. Search only the lessons-learned (not the fact bodies)

```bash
memgrep find "+max_retries" "${ROOTS[@]}" --only-notes
```

### 6. Refresh the index after a batch of memory edits

```bash
memgrep reindex "${ROOTS[@]}"
```

### 7. Regenerate the human-browsable index doc

```bash
memgrep index --markdown --write "${ROOTS[@]}"
```

---

## Combined Search Pattern

For complete context on a topic, combine this skill with the code-structure
tools. (The former `docs-search` and `graph-query` skills are gone: the AI
Maestro docs-indexing backend and the CozoDB graph backend were both retired
permanently. Use the **tldr CLI** for code structure and the **codegraph MCP
tools** for graph queries.)

```bash
# 1. What did we LEARN about this? (curated notes — this skill)
memgrep recall "authentication flow" "${ROOTS[@]}"

# 2. What IS the code, structurally? (tldr-code skill)
tldr search "authentication" src/

# 3. What did we SAY in chat about it? (Claude Code's own conversation memory —
#    there is no separate transcript-search backend anymore)
```

---

## Troubleshooting

### `memgrep` not found

```bash
which memgrep      # CORE ships no installer — memgrep comes from the ai-maestro-janitor
```

If every install path fails, degrade to `grep -rliE "<symptom>" "${ROOTS[@]}"`
— never block on a missing binary.

### No results found

1. Recall ranks on `description + title + tags`, not full body text — try
   different wording or `find` with a broader/optional term.
2. Increase recency scope: drop `--since`, or widen the date range.
3. A genuinely new topic returning zero results is valid information, not a
   failure — write it up after you solve it.

### Results look stale

```bash
memgrep reindex "${ROOTS[@]}"   # rebuild .memgrep/index.db (git-incremental)
memgrep reindex "${ROOTS[@]}" --full  # or force a full rebuild from scratch
```

### No memory directory exists yet for this project

Run `/janitor-memory-bootstrap` (needs the `ai-maestro-janitor` plugin) to
stand up the project's wikimem hub page, or just start writing notes with
`/janitor-memory-write` — the directories are created on first write.

### `/janitor-memory-*` skills unavailable

The `ai-maestro-janitor` plugin isn't installed. `memgrep recall`/`find`
still work standalone against any directory of markdown notes — point
`ROOTS` at whatever directory holds them.

---

## Installation

**CORE does not install memgrep and ships no crate.** Ownership belongs to the
**ai-maestro-janitor** (`Emasoft/ai-maestro#106`), which publishes prebuilt
binaries for darwin arm64/x64 and linux arm64/x64. CORE declares the janitor as
a plugin dependency, so on a normal install memgrep is already present.

Do NOT re-introduce a CORE-side installer or crate. The removed copy was a strict
subset — no `validate`, `lint`, `new-page`, `add-atom`, `add-lesson` — published
under the same binary name and the same `version = "0.1.0"`, so whichever build
landed last silently decided whether the memory protocol in
`~/.claude/rules/markdown-memory-recall.md` (which MANDATES those verbs after
every edit) could run at all.

If every path fails, the script exits non-zero but the recall protocol
still works — it degrades to plain `grep` over the notes. Degrade, never
break.
