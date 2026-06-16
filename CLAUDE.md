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

### Two memory systems — transcripts vs curated notes (COMPLEMENTARY)

This plugin still ships `memory-search` (conversation-transcript search) — a
DIFFERENT system from the wiki-memory notes. They answer different questions:

| System | Surface | Corpus | Question it answers |
|---|---|---|---|
| Conversation memory | `/memory-search` (this plugin; AI Maestro server) | indexed conversation transcripts across sessions | "what did we SAY / discuss / decide in chat?" |
| Wiki note memory | `/janitor-memory-{recall,write,update}` (janitor global) | curated, symptom-indexed wiki pages | "what did we LEARN that must not be re-derived?" |

A debugging session often uses BOTH: recall the wiki page for the known gotcha,
search the transcript for the discussion that produced it. The `memgrep` engine
that powers wiki recall is hosted by THIS plugin (`scripts/memgrep/`, installer
`scripts/install-memgrep.sh`, prebuilt release-asset binaries) and consumed
across the ecosystem; recall degrades to plain `grep` when memgrep is absent.
