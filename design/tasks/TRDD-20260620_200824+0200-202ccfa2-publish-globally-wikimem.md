---
trdd-id: 202ccfa2-4883-46af-9a1c-64e5305d6d0f
title: publish-globally — cross-project visibility for PROJECT-scope wikimem via memgrep
column: planned
created: 2026-06-20T20:08:24+0200
updated: 2026-06-20T20:11:22+0200
current-owner: ai-maestro-plugin
assignee: ai-maestro-plugin
priority: 3
severity: MEDIUM
effort: L
labels: [memgrep, memory, wikimem, cross-project, privacy]
task-type: feature
parent-trdd: null
npt: []
eht: []
blocked-by: []
relevant-rules: []
release-via: publish
delivery: direct-push
target-branch: main
must-pass-tests-before-merge: true
publish-target: ai-maestro-plugins
test-requirements: [unit, integration]
audit-requirements: []
review-requirements: [human-review]
impacts: [public-api]
runtime-targets: [macos, linux]
external-refs: []
---

# publish-globally — cross-project visibility for PROJECT-scope wikimem via memgrep

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative; supersedes the body) — 2026-06-20

**Goal:** let a PROJECT-scope wikimem note opt into being visible from EVERY project
(solves "many Claudes want some project memories accessible globally"), with **zero
path-or-id leakage into any committed/pushed file**, and keeping the note editable ONLY
by its owning project.

**🔒 PRIVACY INVARIANT (user, 2026-06-20 — load-bearing):** the ONLY change committed to
the git-tracked PROJECT file is the bare boolean `publish-globally: true`. **No slug, no
id, no path** — not the dashed-CWD slug, not even the `owner/repo` — is ever written to a
committed/pushed artifact. Every path/id needed for resolution is DERIVED machine-locally
at sync time and lives ONLY in the machine-local USER memdir (never committed).

**Design LOCKED (user-approved 2026-06-20):**
- **D1 link origin (boolean-only committed):** committed frontmatter carries ONLY
  `publish-globally: true`. The owning project's slug (`owner/repo`) is DERIVED at
  `publish-sync` time from the project's git remote (machine-local), used ONLY for the
  machine-local `published/<slug>/` subdir name + as a query handle, and NEVER committed.
  Link resolution rides the symlink's **realpath** to the owning project's memdir. (This
  SUPERSEDES the earlier "store `project: <stable-id>` in frontmatter" idea — see
  SUPERSEDED below.)
- **D2 publish form:** a LIVE **symlink** at `<USER-memdir>/published/<slug>/<name>.md`
  → realpath of the real PROJECT file. `<slug>` = fs-safe `owner__repo` derived at sync.
  `memgrep publish-sync` creates/refreshes/prunes (danglers + de-published).
- **D3 discoverability** ("hard to find") — OUT OF SCOPE here; SEPARATE janitor issue.
- **EDIT-AUTHORITY caveat (user):** a globally-published note is **read-only from any
  foreign project**. Editable ONLY by (a) the owning project's Claude, (b) the janitor in
  the owning project's context. Enforced three ways — see §4.

**SUPERSEDED — do NOT carry forward:**
- ✗ "store `project: <stable-id>` (owner/repo) in the committed frontmatter" — REJECTED
  (user, 2026-06-20): any committed slug/id is unwanted. Committed state = boolean only;
  slug derived machine-locally at sync. The `project:`/`link:` QUERY syntax still exists,
  but its slug is the machine-local published-subdir name, not a committed field.

**Cross-repo split (HARD constraint — `how-to-fix-issues-of-other-projects.md`):**
- THIS repo (`ai-maestro-plugin`) HOSTS memgrep (`scripts/memgrep/`) → all ENGINE work here.
- `ai-maestro-janitor` owns the wikimem schema doc, the write/update skills, the
  heartbeat, and the recall-protocol rule → COORDINATION ISSUE on the janitor.

**NEXT ACTION:** Phase 1 — read `scripts/memgrep/` to map CLI dispatch, frontmatter parser,
recall walk, link handling; implement §3. Await user "go" before writing Rust
(plan-and-build-separate).

**Load-bearing facts / gotchas:**
- USER memdir = `~/.claude/plugins/data/ai-maestro-janitor-ai-maestro-plugins/memory/`
  (machine-local, never git-pushed → a symlink + a derived slug subdir there leak nothing).
- PROJECT memdir = `<repo>/.claude/project/memory/` (git-tracked + PUSHED → only the bare
  `publish-globally: true` boolean may be added).
- memgrep must FOLLOW symlinks during the recall walk (verify the Rust walker default —
  likely `follow_links(true)` only for the USER memdir).
- Dedup: inside the OWNING project a published note appears as PROJECT (real) AND USER
  (symlink) — dedup by realpath.
- No git remote → derive slug from PRRD `project-id`, else dir basename, else a realpath
  hash. All machine-local; still never committed.

**Durable artifacts to read before acting:** this TRDD; `scripts/memgrep/SKILL.md`;
`~/.claude/rules/markdown-memory-recall.md` (scope model + roots).

---

## 1. Problem

Two fleet-wide complaints:
- **A — discoverability:** "the memory system is not easily discoverable." (→ separate
  janitor issue; not designed here.)
- **B — cross-project reach:** Claudes want certain PROJECT-scope memories visible from
  ALL projects. Today PROJECT memory is recalled only within its own repo.

This TRDD designs **B**: an opt-in `publish-globally` flag surfacing a PROJECT note in the
USER scope (visible everywhere), single-source-of-truth, owning-project-only edits, and
**no committed path/id leakage**.

## 2. User proposal (verbatim intent) + refinements

User: a frontmatter flag `publish-globally: true|false`; when true a **symlink** is
auto-created in the plugin's USER-scope memory folder; links keep working because memgrep
can resolve a linked file by the project slug — example
`memgrep project:<slug> link:<relpath>#<memory-id>`.

Refinements accepted by the user (2026-06-20):
- **No slug/id/path committed** — committed change is the bare boolean only; the slug is
  derived machine-locally at sync from the git remote (🔒 PRIVACY INVARIANT above).
- Link resolution primarily via the **symlink realpath**; the `project:`/`link:` query
  slug is the machine-local published-subdir handle.
- Filename collisions across projects handled by a per-project `published/<slug>/` subtree.
- Symlink (live), not copy.

## 3. memgrep engine spec (THIS repo — `scripts/memgrep/`)

1. **Frontmatter:** parse the bare boolean `publish-globally`. (No `project:` field is read
   from committed frontmatter — the slug is derived, not stored.)
2. **`memgrep publish-sync <project-memdir> [--user-memdir <dir>]`:**
   - scan `<project-memdir>` for `publish-globally: true`;
   - derive the owning slug machine-locally: `git -C <project-root> remote get-url origin`
     → `owner/repo` → fs-safe `owner__repo`; fallbacks: PRRD `project-id` → dir basename →
     realpath hash (all machine-local, none committed);
   - create/refresh symlink `<user-memdir>/published/<slug>/<name>.md` → realpath of the
     source note;
   - PRUNE symlinks under `published/<slug>/` whose source is gone or no longer
     `publish-globally: true` (dangling / de-published);
   - idempotent; print created/refreshed/pruned counts.
3. **Link / project resolution (query handle = machine-local published-subdir slug):**
   - `memgrep link <slug>:<note-name-or-relpath>#<memory-id>` → resolve within the owning
     project's memdir located via the symlink **realpath**; return the target note (+ the
     `[^memory-id]` lesson if given).
   - Accept the user's `memgrep project:<slug> link:<relpath>#<id>` spelling as an alias.
   - The slug here is the LOCAL `published/<slug>/` name — never sourced from committed data.
4. **Recall:** follow symlinks under the USER memdir so published notes are recalled
   everywhere; **dedup by realpath** (owning project must not see the note twice). Mark
   USER-scope entries whose realpath is OUTSIDE the current project as **foreign/published**.
5. **Read-only guard (edit-authority §4):** recall/print tags a foreign published note
   read-only; any memgrep write-ish path refuses to mutate a symlinked-foreign note (realpath
   outside the current project root).

## 4. EDIT-AUTHORITY invariant (user caveat, 2026-06-20)

Editable ONLY by (a) the owning project's Claude, (b) the janitor in the owning project's
context. Read-only from any foreign project. Enforced:
1. **Cross-project rule (already binding):** the symlink's real target is project A's
   git-tracked file; editing it from project B is editing another project's tree —
   forbidden by `~/.claude/rules/how-to-fix-issues-of-other-projects.md`.
2. **Recall-protocol rule (janitor, to add):** "published-foreign notes are read-only
   here — recall only."
3. **memgrep mechanical guard:** refuse write/update on a foreign symlinked note.

## 5. Cross-repo split + coordination

| Part | Owner | Vehicle |
|---|---|---|
| `publish-sync`, `link`/`project:` resolver, symlink-aware recall + dedup, foreign read-only guard, derive-slug-from-git-remote, bare-boolean frontmatter read | THIS repo (memgrep) | implement here (Phase 1) |
| `publish-globally` (bare boolean) in the wikimem frontmatter schema (`wikimem-model.md`) — and explicitly NO committed slug/id | ai-maestro-janitor | coordination issue (Phase 2) |
| `/janitor-memory-write` + `-update`: offer/set the flag (with a privacy WARN), then call `memgrep publish-sync` | ai-maestro-janitor | coordination issue |
| heartbeat: periodic `memgrep publish-sync` across project memdirs (the "automatic" part) | ai-maestro-janitor | coordination issue |
| recall-protocol rule: document the feature + 🔒 privacy invariant + edit-authority + read-only-foreign | ai-maestro-janitor | coordination issue |
| scope-leak detector: published content is now globally visible (wider blast radius) | ai-maestro-janitor | coordination issue |
| discoverability (complaint A) | ai-maestro-janitor | SEPARATE issue |

## 6. Phased plan

- **Phase 1 (this repo, code):** explore `scripts/memgrep/`; implement §3.1–§3.5; unit +
  integration tests (publish-sync create/refresh/prune; slug-derivation incl. no-remote
  fallbacks; link resolution; recall dedup; foreign read-only guard; **assert nothing but
  the boolean is written to the source file**); update memgrep docs for the new verbs.
  Commit. (Await user "go" before Rust.)
- **Phase 2 (coordination):** file the janitor coordination issue (§5 janitor items + §4
  invariant + 🔒 privacy invariant); self-identify per R22/G1.1.
- **Phase 3:** file the SEPARATE discoverability issue on the janitor (complaint A).

## 7. Derived tasks / risks

- Verify memgrep's recall walker follows symlinks (Rust `ignore`/`walkdir` default does NOT
  follow — needs `follow_links(true)` for the USER memdir walk only).
- Dedup correctness (realpath key) so the owning project doesn't double-count.
- Dangling-symlink prune every sync (repo moved/deleted, note de-published).
- **Privacy regression guard (load-bearing):** a test must assert `publish-sync` writes
  NOTHING but the boolean back to the source, and that no derived slug/path is persisted
  anywhere git-tracked. The slug lives only under the USER memdir.
- No-git-remote projects: slug falls back to PRRD project-id → basename → realpath hash
  (all machine-local; USER scope is machine-local anyway).
- Security: `publish-globally: true` widens content exposure to all projects; the write
  skill must WARN on set; the scope-leak detector still applies (wider blast radius). Never
  auto-publish; opt-in only.
- LOCAL-scope notes are NOT publishable (machine-private) — `publish-sync` ignores anything
  outside a PROJECT memdir.
