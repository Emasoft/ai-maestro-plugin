# ai-maestro-plugin — project instructions

The umbrella core plugin for the AI Maestro ecosystem: shared skills, AMP
inter-agent messaging, AID Ed25519 identity, governance, kanban, the universal
PRRD/TRDD/Kanban workflow every role plugin inherits, and the `memgrep`
markdown-recall engine hosted for the ecosystem.

## PROACTIVE MEMORY CONTRACT (wiki-memory — adopt the janitor's global system)

This project USES the janitor's global wiki-memory system. Do NOT use any
per-plugin memory skill — the canonical legs are the **global** janitor skills
`/janitor-memory-recall`, `/janitor-memory-write`, and `/janitor-memory-update`
(governed by `~/.claude/rules/markdown-memory-recall.md`). The contract below is
binding on the orchestrator AND every sub-agent (sub-agents inherit nothing —
the contract is repeated in each `agents/` prompt for that reason).

1. **RECALL BEFORE ACTING — unprompted.** Before debugging a recurring problem,
   making a design decision, acting on a recurring alert, or editing a file in an
   area you haven't loaded, run `/janitor-memory-recall` (or memgrep directly)
   FIRST, indexed by the **SYMPTOM** (the user's words / the error text), never
   the answer's jargon. Skipping recall means re-deriving — usually worse — what a
   past session already solved.

2. **WRITE / UPDATE AFTER SOLVING — unprompted.** After solving a non-trivial
   problem, fixing a bug, or making a decision that isn't derivable from the code,
   capture it with `/janitor-memory-write` (MEMORIZE) or `/janitor-memory-update`
   — recall first so you ADD to the owning page rather than duplicate. Use the
   clean-the-fact-in-place + demote-the-error-to-a-`[^N]`-lesson correction
   protocol.

3. **MAINTAIN THE WIKIMEM.** Keep the PROJECT-scope pages current as you work —
   the architecture hub, key-solution component pages, the publish/deploy pipeline
   page — so the knowledge is git-tracked and shared. Pages are wiki nodes (hub /
   aspect / component) with bidirectional links, not loose notes; the model lives
   in the janitor write skill's `references/wikimem-model.md`.

### Scope routing (decide the scope BEFORE authoring)

| Scope | Root | Contains |
|---|---|---|
| **LOCAL** | `~/.claude/projects/<slug>/memory/` (slug = project path, dashed) | machine-private: local paths, usernames, hostnames, secret hints, per-instance facts |
| **PROJECT** | `<repo>/.claude/project/memory/` (git-tracked + pushed) | project knowledge any dev needs — architecture, gotchas, lessons. NO secrets / local paths |
| **USER** | the janitor's global host (`~/.claude/plugins/data/ai-maestro-janitor-ai-maestro-plugins/memory/`) | cross-project knowledge: user preferences, machine-independent lessons |

Routing rule: machine-private → **LOCAL**; project-shared-with-no-secrets →
**PROJECT**; true across all projects → **USER**; **UNSURE → LOCAL** (the safe
scope). On conflicting facts the more specific scope wins: **LOCAL > PROJECT >
USER**.

### Recall — the FIXED array-form (zsh-safe; NEVER the space-joined string)

zsh (the macOS default shell) does NOT word-split an unquoted `$ROOTS`, so a
space-joined string passes all roots as ONE bogus path → silent 0 results.
Always build an ARRAY and expand it as `"${ROOTS[@]}"` (works in bash AND zsh):

```bash
LOCAL="$HOME/.claude/projects/$(pwd | sed 's#/#-#g')/memory"                       # machine-private
PROJECT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)/.claude/project/memory"  # git-tracked, in-repo
USER="$HOME/.claude/plugins/data/ai-maestro-janitor-ai-maestro-plugins/memory"     # janitor's FIXED global host
ROOTS=(); for d in "$LOCAL" "$PROJECT" "$USER"; do [ -d "$d" ] && ROOTS+=("$d"); done
SYMPTOM="the user's words / the error / the symptom"   # NOT the answer's jargon
if command -v memgrep >/dev/null 2>&1; then
  memgrep recall "$SYMPTOM" "${ROOTS[@]}"        # pages ranked best-first: path — description
else
  grep -rliE "$SYMPTOM" "${ROOTS[@]}" 2>/dev/null  # fallback: degrade, never break
fi
```

`recall`/`find` resolve and APPEND each page's `[^N]` lessons-learned by default,
so one call yields the facts AND every WHY. Read the page WHOLE (facts + its
linked lessons) before acting.

### Wiki-memory recall — one curated corpus, two entry points

There is ONE memory system that matters here: the curated, symptom-indexed
markdown **wiki-memory** corpus, queried by the `memgrep` engine. The old AI
Maestro conversation-transcript RAG backend that `/memory-search` used to hit was
**permanently removed in v2.9.0 (#27)** — no replacement CLI, none planned. Both
skills below now read the SAME wiki corpus; they are entry points, not rival
systems:

| Surface | Role | Question it answers |
|---|---|---|
| `/memory-search` (this plugin) | RECALL-side entry: builds the LOCAL/PROJECT/USER roots and runs `memgrep recall`/`find` (degrades to `grep`) | "what did we LEARN that must not be re-derived?" |
| `/janitor-memory-{recall,write,update,bootstrap}` (janitor global) | the AUTHORING/maintenance layer on top of `memgrep` | write / update / stand up the same corpus |

For "what did we SAY / decide in chat?" there is no transcript-search backend
anymore — use Claude Code's own conversation history and project `CLAUDE.md`. The
`memgrep` engine that powers recall is owned and published by the
**ai-maestro-janitor**, NOT by this plugin (ownership ruling: `Emasoft/ai-maestro#106`).
CORE only CONSUMES it; recall degrades to plain `grep` when memgrep is absent.

CORE once vendored its own copy and shipped rival binaries. Do NOT re-add one:
that crate was a strict subset missing `validate`, `lint`, `new-page`, `add-atom`
and `add-lesson`, under the SAME binary name and the SAME `version = "0.1.0"`, so
whichever build won `cargo install` last silently decided whether the memory
protocol in `~/.claude/rules/markdown-memory-recall.md` — which MANDATES those
verbs after every memory edit — could run at all. `tests/test_memory_protocol_components.py`
fails if the crate, the installer, or the release job comes back.
