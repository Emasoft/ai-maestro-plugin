---
trdd-id: 546UDAZF
title: Remediate the CORE v2.10.0 full-audit findings
column: published
implementation-commits: [2ebabc4, fbe7670, f1b1d40, e8a5315, 6cceb62, c3dc41b]
created: 2026-07-25T00:10:42+0200
updated: 2026-08-07T12:02:40+0200
current-owner: ai-maestro-plugin (core)
assignee: ai-maestro-plugin (core)
task-type: refactor
min-approval-requirement: none
release-via: publish
priority: 3
---

# Remediate the CORE v2.10.0 full-audit findings

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative; supersedes the body) — 2026-07-25

**Where this came from.** A read-only CPV full audit of CORE v2.10.0 ran on
2026-07-24 (schema validator + D1–D9 design recipes + 5 external security
scanners + staleness + cross-reference integrity). Verdict: **ship-safe, 0
CRITICAL**, but 5 MAJOR. The report is EVIDENCE and lives in the **gitignored**
tree — it will not survive. This TRDD is the durable record of the DECISIONS it
produced.

Report: `reports/cpv-doctor-agent/20260724_213106+0200-core-full-audit.md`
(security validator side-report: `reports/security/20260724_212825+0200-ai-maestro-plugin.md`)

**Already DONE — do not redo:**

- **MAJOR-1 — Node.js undocumented hard dependency → FIXED**, commit `2df4829`.
  Every `hooks/hooks.json` entry runs `scripts/ai-maestro-hook.cjs` under `node`,
  but `node` appeared **zero** times in `README.md` / `CLAUDE.md`. README
  Requirements now states it explicitly. This was the only finding that was a live
  silent-failure risk (hooks fail quietly; `directory-guard.cjs` fails **open**).

**ALL FOUR DECISIONS ARE RESOLVED (2026-08-02).** D1, D2 and D4 were decided on
measurement and executed; D3 was amended and then dissolved when `ai-maestro#106`
moved memgrep ownership to the janitor, taking the thing D3's gate would have built.
Decided under the USER's standing authority ("decide on your own, base your decisions
on verified facts").

**What is left on this card is NOT a decision — it is the lower-severity backlog below**
(§ the MINOR/NIT list), most of which is already struck as done or explicitly
do-not-fix. Nothing here is blocked on a human.

| # | Outcome |
|---|---|
| **D1** | ✅ `e8a5315` — both RETIRED skills removed (staged via safe-delete batch `20260802_030400+0200`). The README table had drifted BOTH ways: 2 phantom rows, 3 missing skills, 1 stale row. Now an exact 24/24 match asserted in both directions. |
| **D2** | ✅ `fbe7670` — ONE policy, with a verifiable discriminator: *the description must match the declared surface*, and CORE's own docs decide which way. Docs promise `/name` → add the wrapper (2: `memory-search`, `team-governance`); they don't → `user-invocable:false` is the intent, drop the slash promise (9). 13 → 0. |
| **D3** | ✅ CLOSED as OBSOLETE-IN-CORE 2026-08-02 — amended first (`e9a4fdb`: `--version` cannot fail on the defect it exists for; must assert the `--help` SURFACE), then dissolved by `ai-maestro#106`. The gate was "build ONE memgrep target and assert it"; CORE no longer HAS a memgrep target (`6cceb62`), so there is nothing here to build. The need did not vanish — it MOVED to the janitor with the crate, and is carried there by `ai-maestro-janitor#164`. Do NOT implement a memgrep build gate in CORE; the regression guard CORE needs is the opposite one, `test_core_does_not_ship_a_rival_memgrep`, which already exists. |
| **D4** | ✅ `f1b1d40` — the "expect CI churn" premise was FALSE: nothing runs markdownlint here (CPV's warning compares the file, never executes the linter). Adopted canon's config; the real find was a table row whose unescaped `\|` silently dropped a governance rule's text. 47 cosmetic findings LEFT and counted, not swept. |

**Superseded — the original framing, kept because the reasoning is the durable part:**
~~NEXT ACTION — none autonomously. Four decisions are the USER's~~ (each changes
CORE's public surface, so they were deliberately NOT taken):

| # | Decision | Why it needs a human |
|---|---|---|
| D1 | MAJOR-3 + MAJOR-4 (one coupled edit): delete the RETIRED `docs-search` + `graph-query` skills, then regenerate the README skills table (`/cpv-refresh-readme`) | removes two shipped capability rows — a consumer-visible deletion |
| D2 | MAJOR-2: reconcile 13 skills whose description promises `/<name>` while `user-invocable: false` and no `commands/<name>.md` exists | three valid fixes per skill (flip the flag / add the wrapper / reword to a natural-language trigger) — needs ONE policy choice, not 13 ad-hoc ones |
| D3 | MAJOR-5 (= warning #20, highest-value): add a push/PR smoke job that builds ONE memgrep target and asserts the staged binary's **`--help` SURFACE** | a CI change; the payoff is ecosystem-wide. **AMENDED 2026-08-01 — `--version` is NOT sufficient**, see below |
| D4 | warning #28: replace `.markdownlint.json`'s `{"default": false}` with canon's explicit per-rule opt-out list | flipping linting on surfaces a backlog of existing violations — expect CI churn before green |

> **D3 AMENDED 2026-08-01 — the `--version` assertion would pass on a broken build.**
> Measured while investigating `core#52`: this repo's vendored `scripts/memgrep/`
> (4806 LOC) implements only `find`/`recall`/`reindex`, while the janitor's crate
> (12354 LOC) additionally implements `lint`, `validate`, `add-atom`, `add-lesson`,
> `new-page`, `overview`, `migrate` — and **both declare `version = "0.1.0"`**. Since
> `release.yml:272` builds the shipped assets from the vendored copy, CORE ships the
> subset on every release, and a `--version` smoke check reports `0.1.0` and goes green.
> D3 must therefore assert the **surface**: require the built binary's `--help` to list
> the verbs the memory skills actually invoke, and fail when one disappears. A gate that
> cannot fail on the defect it was written for is worse than no gate — it converts an
> unnoticed problem into an audited-and-approved one. Do NOT implement D3 as originally
> written. Root cause + the two-crate table: `core#52`.

**RESOLVED 2026-07-28 — root cause found upstream and CORE's pin bumped to `v3.22.3`.**
The CPV maintainer answered `claude-plugins-validation#180`: it was **never the linters**. It is
the markdown **dead-link checker**. `validate_md_urls` is called once *per markdown file* and its
per-host semaphores are scoped to a **single call**, so the throttling that would pace a burst
**resets on every file** and the phase grows with (files × URLs). Each request was bounded (8s +
bounded retries); their *sum* was bounded nowhere. That is the same "bounded per item, unbounded in
aggregate" defect CPV#162 fixed for REPO LINT — which is exactly why the `v3.5.0` pin already
carried the #162 remedy and it did not help: that remedy covered a different phase.
`v3.22.0` gives the phase **one deadline spanning every file** (300s, override
`PLUGIN_URL_CHECK_PHASE_TIMEOUT`); a URL past budget is reported **skipped, never dead**.
`v3.22.3` adds `PYTHONUNBUFFERED=1`.

> **This SUPERSEDES the "Do NOT bump the CPV pin" line below — but not the measurement behind it.**
> That measurement stands and was right: at the time, *no released version contained a fix*, so
> bumping was cargo-culting. What changed is not my confidence, it is the world — a version now
> exists that fixes this named defect. Bumping for a **named, causally-established fix** is a
> different act from bumping in hope. Do not read this as licence to bump the pin speculatively.

Measured here after the bump: cold `v3.22.3` = **19–36 s, exit 0**. Changes landed:
pins `v3.5.0 → v3.22.3` at all five sites (the three in `publish.py` collapsed into one `CPV_REF`
constant, because a bump that missed one would leave the local G3 gate and CI validating with
**different** validators while both reported "passed"); `PYTHONUNBUFFERED: "1"` in both workflows;
and `release.yml`'s `> file 2>&1` + trailing `cat` replaced with `| tee` + a
**`${PIPESTATUS[0]}`** read. That read is load-bearing: GitHub's default `run:` shell is
`bash -e {0}` **without** `-o pipefail`, so a bare `$?` after the pipe is `tee`'s status
(~always 0) and the gate would have reported success for **every failed validation**.

> **Superseded within the same day: my first implementation used `set -o pipefail`.** Upstream
> recommended `${PIPESTATUS[0]}` and was right — `pipefail` yields the **rightmost** non-zero
> status, so a `tee` write error masks CPV's real severity. Verified in bash rather than
> assumed: bare `$?` → **1** (tee's) · `pipefail` → **1** (masks cpv=4) · `PIPESTATUS[0]` → **4**
> (CPV's own verdict). `PIPESTATUS` must be captured as an array in ONE expansion — any later
> command, **including a plain assignment**, resets it (a sequential second read returns empty;
> also verified). `tee`'s own status is checked separately so a failed write cannot look like a
> clean validation. Fixed in `e40a688`.

**Trap hit while doing it, worth keeping:** the first draft of those `tee` comments used markdown
backticks, and backticks are command-substitution syntax to a shell — CPV's scanner flagged a
**comment** as `CMD_INJECTION` and `--strict` turned that NIT into a red gate (exit 4). Proven mine,
not the version's, by re-running `v3.22.3` against the pre-edit workflows: **exit 0**. Never write
backticks inside a `run:` block, comments included. Same class as the blockquote-`>`-read-as-redirect
false positive noted below.

**RESOLVED 2026-08-01 — `CPV#184` is fixed upstream and the publish gate is GREEN again; pin bumped
`v3.22.3` → `v4.2.1` in `2ebabc4`.** The maintainer reproduced my A/B at their HEAD (same bytes, one
variable) and confirmed the hypothesis I filed but deliberately did not assert as mechanism: the
exclusion was keyed on the **literal path `design/tasks`**, not on the lifecycle corpus. They had
nearly closed it unreproducible — a static read found the literal in four places, three
hash-anchored to CPV's own manifest and the fourth (`_DEV_SCRATCH_DIR_PARTS`) followed to
`check_tirith_scanner`, which governs only EXTERNAL scanner output, while my findings are in-process
skillaudit. Probing, not reading, settled it: `scan_content` fires identically in all five zones, so
the decision had to be in a downstream consumer —
`validate_plugin._run_skillaudit_native._should_skip`, which also calls `_is_dev_scratch_path`. All
four lifecycle zones now clear, and a non-lifecycle `design/notes/` control still fires all three
findings so the fix cannot decay into a blanket `design/` mute.

Measured HERE before bumping, not taken on trust: `v4.2.1 --strict` → **EXIT=0, NIT=0**
(`CRITICAL=0 MAJOR=0 MINOR=0`, `WARNING=28` unchanged and advisory; cache audit clean). Report:
`reports/cpv-pin-verify/20260801_060157+0200-cpv-v4.2.1-strict.txt`. Then ruff clean, mypy clean
(10 files), pytest **180 passed**. All three pin sites moved in one commit for the reason `CPV_REF`
exists — a partial bump leaves local G3 and CI on different validators while both report "passed".

> **Lesson — a filed hypothesis is worth more than a filed guess.** I wrote the A/B and the one-line
> suspicion ("*if the exclusion is keyed on a literal `design/tasks` rather than the corpus, that is
> the whole gap*") but did **not** claim the mechanism, because I could not see their source. The
> maintainer's reply says that is why it got fixed correctly rather than plausibly: my A/B survived
> their static reading, which had concluded *unreproducible*. **Report the reproduction you can
> prove and the hypothesis as a hypothesis; a confident wrong mechanism would have been argued
> with instead of tested.**

**Original diagnosis (2026-07-26), kept for the record — CI `Validate` intermittently
exceeds its 30-min cap.** MAJOR-5 stopped being hypothetical: the `v2.11.0` release run
timed out at 25 min on `Run full plugin validation (remote CPV, --strict)` and shipped a
release with **no memgrep binaries**; a re-run passed and attached all assets. `ci.yml`'s
`Validate` job then hit the same wall on `main` **twice** (30-min cap, both the original
run and a re-run), so CI on `main` is currently red at `85f7653` while the release itself
is complete and correct.

Do NOT re-test these two — both were measured and DISPROVEN:

| Hypothesis | Verdict |
|---|---|
| The `@v3.5.0` pin is stale/bad (CPV is at v3.19.1) | **WRONG.** `refs/tags/v3.5.0` exists (`3d8ea58`). Cold-cache locally: **v3.5.0 = 39 s exit 0**, v3.19.1 = 47 s exit 0. The version is not the variable. |
| A cold `uvx --from git+…` fetch/build stall (what the workflow comments claim) | **WRONG.** The CI log shows `Built claude-plugins-validation @ git+…` **4 seconds** after the step starts. The fetch is not the cost. |

Also not it: both `ci.yml` and `release.yml` already restore `cpv-scan-cache` **and** run
`setup-uv` with `enable-cache: true`, so a missing cache is not the difference.

What IS established: after CPV builds, the step runs 25-30 min and is killed. The apparent
"zero output" is a red herring — the step redirects with `> validation-report.txt 2>&1`, so
nothing reaches the log until `cat`. Remaining suspect: CPV installing its ~15 on-demand
linters on a fresh ubuntu runner (network-bound, variable) — which is the class of the CPV
issues the workflow comments already cite (**#90**, **#114**). Per
`~/.claude/rules/plugin-tests-are-the-plugins-job.md` the G3-validate gate is CPV-owned
infrastructure, so the fix likely belongs upstream, not in CORE's workflow. Next step is to
reproduce on a fresh ubuntu runner (not macOS) before filing.

**OPEN DEFECT (2026-07-28) — CORE publishes a memgrep that cannot index lesson atoms.**
Surfaced sideways, from three janitor `MEMGREP-004` tickets about `atoms` missing a `status`
column.

> **CORRECTION (2026-07-28, later) — the three tickets were FALSE POSITIVES, and my first
> reading of them here was wrong.** I wrote that "a migration failed" and that they were "the
> janitor's to fix … the janitor self-repairs". Two `janitor-repair-agent` runs
> (**T-7MTSGLOU**, **T-E0DR0WTS**) independently established that **no migration ever failed**:
> the index was a complete, integrity-clean **v5** DB that had simply not been write-opened
> since `~/.cargo/bin/memgrep` was rebuilt at `SCHEMA_VERSION = 6`. One `memgrep reindex`
> applied the v6 ladder cleanly. `.memgrep/self-heal.log` **does not exist** — proof no repair
> path was ever taken. Verified here: `user_version=6`, `atoms` carries `status` +
> `superseded_by`, `memgrep validate` exits 0.
>
> The real defect is **check ordering** in the janitor's `validate_db`
> (`scripts/memgrep/src/index.rs`): step 0 guards `ver > expect_version` (`MEMGREP-010`) but
> there is **no symmetric guard for `ver < expect_version`**, and the base-table shape check
> (`MEMGREP-004`, line 788) runs *before* the version stamp is read (`MEMGREP-006`, line 839).
> A DB one version behind necessarily lacks the column the pending step adds — so **every
> schema bump manufactures one critical ticket per not-yet-written corpus.**
> Cross-project ⇒ FLAGGED, not patched. Already filed upstream as
> **`Emasoft/ai-maestro-janitor#123`** by a sibling agent with a line-for-line matching
> diagnosis; **do not file a duplicate.** Reports:
> `reports/janitor-repair-agent/20260728_18{5920,5934}+0200-T-*.md`.
>
> Lesson: a critical *shape* complaint arriving right after a binary upgrade is version skew
> until the stamp is read. Do not infer damage from a shape check that runs before the version
> check — and do not follow a ticket's prescribed remedy ("repair the migration ladder, rebuild
> from the notes") when the ladder is correct: that edits a shipped immutable migration step
> and destroys the evidence. Both agents correctly refused.

**The CORE-side defect underneath them is unaffected by that correction and still stands** —
it is about a missing *table*, not a missing column, and was measured directly:

```
CORE  scripts/memgrep   Cargo.toml 0.1.0   creates: files, memories, notes          <- NO atoms
janitor scripts/memgrep Cargo.toml 0.1.0   creates: atoms, files, memories, notes
CORE  target/release/memgrep  7,664,496 B  creates: files, memories, notes
installed ~/.cargo/bin/memgrep 8,239,376 B creates: atoms, files, memories, notes
both binaries: `memgrep 0.1.0`
```

CORE's crate has **zero** references to `atoms` anywhere. So the prebuilt binaries CORE attaches
to every release (`memgrep-{darwin-arm64,darwin-x64,linux-x64}.tar.gz`, installed in preference
by `scripts/install-memgrep.sh`) create an index with **no `atoms` table at all** — wikimem lesson
recall then returns nothing, silently, with no error. That is worse than the missing-column bug
the tickets describe. The engine this machine actually runs is the **janitor's**.

Nothing can detect this: both crates say `0.1.0`, both binaries print `memgrep 0.1.0`. It is the
same shape as core#33/#35 — two copies of one artifact, the stale one still building, no way to
tell which is live — only with a Rust crate instead of rule files.

**REVISED 2026-07-28 (measured) — it is THREE copies at THREE schema levels, not two, and the
one that INSTALLS is stale:**

| source | lines | `SCHEMA_VERSION` | `atoms` refs |
|---|---|---|---|
| janitor **repo worktree** | 2288 | **6** | 90 |
| janitor **cached plugin `0.60.1`** — what an install actually gets | 1846 | **5** | 67 |
| **CORE** `scripts/memgrep` | 544 | *(no ladder)* | **0** |

`~/.cargo/bin/memgrep` creates `atoms` + knows `superseded_by` ⇒ built from the **v6** source.
All three crates say `0.1.0`. **This is the mechanical cause of the whole MEMGREP-004 ticket
cluster** — a v5-shipping plugin against a v6 binary on PATH is precisely the version skew that
`validate_db`'s check ordering (janitor#123) reports as a critical shape defect. Surfaced only
because two repair agents cited `index.rs:717/:773` while I had measured `:788/:839` for the same
defect: **a line-number disagreement about one file is evidence of more than one file.** Posted
to `janitor#122`; the version-discipline half (ship the crate the binary was built from; move
`--version` with `SCHEMA_VERSION`) is fixable upstream **without** deciding ownership.

**NOT fixed unilaterally; asked instead** (`Emasoft/ai-maestro-janitor#122`): who owns memgrep?
(a) the janitor owns it → CORE drops the crate + release assets and corrects its README hosting
claim; or (b) CORE owns it → CORE takes the current source and the janitor consumes CORE's
releases. Either way the version must move when the schema moves, and the retired copy must be
REMOVED rather than left building. Deleting or replacing CORE's crate is a cross-repo contract
change, not local cleanup — hence the question rather than a commit.

Do NOT "fix" this by re-vendoring the janitor's source into CORE before that answer lands; that
picks option (b) by accident and leaves two maintainers unaware.

**Load-bearing facts / gotchas:**

- **The 9 security findings are ALL false positives** — verified line-by-line. Eight
  are inverted-polarity (a security *guard* flagged for the pattern it *blocks*);
  one is a markdown blockquote `>` read as a shell redirect. **`directory-guard.cjs`'s
  detector regexes are LOAD-BEARING runtime code — flag, never devitalize.**
  Allowlist them so future scans stop re-litigating.
- **Warnings #23 / #24 are false positives that must NOT be "fixed"** — the validator
  itself says `ci.yml` / `release.yml` carry hardening the canonical template lacks.
  Aligning them to canon would be a **downgrade**.
- **Warning #19** (memgrep compile source shipping in-tree) was triaged on 2026-07-24 as a
  *deliberate, accepted architectural deviation* on the grounds that "CORE hosts the memgrep
  engine for the whole ecosystem". **That premise is now DISPROVEN** (see the 2026-07-28
  defect above): CORE hosts a memgrep that lacks the `atoms` table entirely, while the
  ecosystem runs the janitor's build. So #19 is no longer "accepted" — it is **pending**
  the ownership answer in `Emasoft/ai-maestro-janitor#122`, and under option (a) the crate
  leaves CORE and the warning disappears with it.
  **✅ RESOLVED 2026-08-02 exactly as predicted: option (a) happened.** `ai-maestro#106`
  ruled the janitor canonical, `6cceb62` removed the crate, and warning #19 disappeared
  with it — there is no in-tree compile source left to warn about. `janitor#122` (the
  ownership question this line was waiting on) is answered and closed. Note for the
  record: `ai-maestro#106` was a DUPLICATE of `#122` that I filed without checking the
  open one first; the ruling is sound, the process was not.
- Warning counts: **28 triaged → 9 genuine · 13 false-positive · 6 cosmetic.**

**SUPERSEDED — do NOT carry forward:**

- "27 warnings" — the brief cited 27; the audit run observed **28**. Use 28.
- Any plan to fix MAJOR-1: it is done (`2df4829`). Do not re-edit README Requirements.
- Any reading of the audit's "unpushed commits" / "missing `rules/` dir" as defects —
  both were confirmed **expected state** (CORE reaches the remote only via
  `publish.py`; governance rules were deliberately retired to the janitor IND bases
  + ai-maestro DEP overlays).

## Lower-severity backlog (from the same audit)

MINOR: ~~stray `scripts/memgrep/SKILL.md` with no frontmatter~~ **DONE 2026-07-27** —
renamed to `scripts/memgrep/README.md`, 2 referrers repointed
· ~~**13 terminal TRDDs parked in `design/tasks/`, and the move is GATED** on the
archival-vocabulary ruling (`Emasoft/ai-maestro#93`)~~ **DONE 2026-07-31, and it was
12 not 13** — `e499fe9`; the ruling and the off-by-one are recorded below.
· ~~stale tracked `validation-report.md` + `fix-log.md` (2026-04-10, ship to every consumer)~~
**DONE 2026-07-31** — `dee2bf3`; copies preserved at `reports/legacy-root-artifacts-20260410/`.

> **✅ RESOLVED 2026-08-01 — fixed upstream in CPV `v4.2.1`, pin bumped in `2ebabc4`, gate measured
> GREEN here (exit 0, NIT=0). Full account in the STATE block above.** The record below is kept
> because the REASONING is what mattered: it is why the gate was held honestly red for a day instead
> of being turned green by a suppression that would have hidden a real scope bug from every other
> plugin that ever archives a TRDD.
>
> **⚠ THE PUBLISH GATE IS RED, and archiving is what turned it red — `CPV#184` (2026-07-31).**
> Do NOT "fix" this by editing archived TRDD bodies or adding a suppression. **CPV `--strict`
> scans `design/archived/` but NOT `design/tasks/`.** Proved by A/B on one file, zero content
> change, one variable:
>
> ```
> design/archived/TRDD-899317b3-…-aegis-bash-analyzer-regex-gaps.md  → [NIT] FS_WRITE   NIT=3
> git mv → design/tasks/…                                           → not flagged      NIT=2
> git mv → design/archived/…  (restored)                            → flagged again    NIT=3
> ```
>
> So CORE went **exit 0 → exit 4 (NIT=3)** purely by obeying the `ai-maestro#93` archival
> ruling. All three findings are prose in design docs: the word *sudo* in a sentence; a table
> row **documenting a guard-bypass vector** (inverted polarity, same class as `CPV#170/#177/
> #178`); and prose defining what counts as executable. **There is no source fix — §12 freezes
> terminal TRDD bodies**, exactly the shape of `CPV#176` case 2 ("fixing the fixture mutates
> the input the tests parse; the scope is what's wrong"). `design/proposals/` and
> `design/refused/` share the property; `refused/` is empty here, which is the only reason this
> is 3 findings and not more.
>
> **Lesson: when a scope exclusion names ONE member of a set the ecosystem defines as a set,
> the excluded member is a coincidence and the rest are a latent gate failure** — armed the
> first time anyone follows the lifecycle to its end. Held honestly red rather than green by
> suppression; publish is gated until CPV scopes it.

> **⚠ THE PROTECTED STASH MOVED — identify it by MESSAGE, never by index (2026-07-31).** For six
> weeks the memgrep publish-globally WIP (`TRDD-202ccfa2`, `core#18/#45`) was `stash@{0}`, and
> every handoff said *"never drop `stash@{0}`"*. Today an `auto-backup-checkout-*` stash was
> created by a hook during a `git mv` and pushed the WIP to **`stash@{1}`**. That instruction is
> now not merely stale but **inverted**: followed literally it protects the throwaway and leaves
> the irreplaceable one looking like "the other stash". Resolve it before touching anything —
> `git stash list | grep -n 'memgrep publish-globally'`. **Lesson: a protection rule must name
> its object by CONTENT, never by POSITION in a mutable list** — the list reorders without
> announcing it, and the rule keeps reading as though it were still true. Same failure class as
> `kanban.py`'s `WORKING_COLUMNS` adjudicating terminality: an identifier that is really a
> coincidence of ordering.

> **Vocabulary note — do NOT "fix" this card to `column: blocked` (2026-07-29).** The
> `trdd-state-reconciliation` detector flagged TRDD-546UDAZF as a prose-frontmatter mismatch:
> *"prose says blocked; frontmatter column != blocked & blocked-by: []"*. The frontmatter is
> **correct** and the prose was the defect. Per the schema, `blocked-by` is
> **`list[trdd-ref]`** — TRDD references only — and column-transition **28** requires it
> non-empty to enter `blocked`. This card's gates are a USER decision (D1–D4) and rulings in
> **other repos** (`ai-maestro#93/#98`, `janitor#122/#135`); none is a TRDD, so `blocked-by:`
> cannot legally hold them and `blocked` is the wrong column. `backburner` — authored/parked,
> promoted to `todo` when it is next-up — is right. The single word "BLOCKED" above was
> describing the **other 13 cards'** archival move, not this card's own state; it is now
> "GATED" so the reserved term is not overloaded. **Lesson: `blocked` is a reserved column
> name, not an English adjective — in TRDD prose say gated/parked/awaiting unless you mean
> the state machine's `blocked`.**

> **I was wrong to "correct" this to 6, and the audit's original 13 was right (fixed
> 2026-07-29).** Measured: `design/tasks/` holds 15 files — **8 `complete` + 5 `published`**
> + 1 `planned` (TRDD-202ccfa2, the only genuinely open card) + 1 `backburner` (this one).
> 8 + 5 = **13 terminal**. My error was reasoning from `kanban.py`'s `WORKING_COLUMNS` — which
> governs **board rendering**, a different question — instead of from the governing text.
> `trdd-design-tasks` **§12** settles it: *"Terminal columns are frozen. Do not edit the body of
> a `complete` / `failed` / `superseded` / `published` / `live` TRDD."* `complete` and
> `published` are both named terminal. **Lesson: when a count disagrees with a spec, check which
> document actually governs the question before "correcting" the spec's number** — I overruled a
> correct audit finding with a rendering constant. The wrong figure reached
> `ai-maestro#93` and `#98`; corrected on-thread.
**2026-07-28 — premise CHALLENGED then RE-CONFIRMED; a fix is now drafted upstream.** The
janitor (`ai-maestro#98` §1) argued #93 might be arguing with a DEAD FILE: the
`trdd-approval-tiers.md` I cited carries no janitor provenance marker and is the retired
predecessor of ai-maestro's `aimaestro-trdd-approval.md` overlay. I verified rather than
accept it — **the archival protocol survived into the live overlay, so the ruling still
stands**, and the contradiction is now provably INTERNAL to that one file:
`~/ai-maestro/.claude/rules/aimaestro-trdd-approval.md` **:148** operationalizes archival as
`--state <completed|cancelled|superseded>` while **:787** treats `column ∈ {complete,
published, live}` as terminal. Line 148's only edit since (2026-07-16, ai-maestro#65 B2) was
a **skill rename**, not a vocabulary change. The janitor's `#98` §2.3 proposes exactly the
fix (archive-eligible terminal set = `completed|cancelled|superseded|published|live`); I
said I'd adopt it as written and have no competing proposal. Still parked until it lands —
a wrong mass-mutation of frozen TRDDs has no clean inverse.

**RESOLVED 2026-07-31 — the hub ruled, and the cards are archived (`e499fe9`).**
`ai-maestro#93` (2026-07-30): ***`published` and `live` archive AS THEMSELVES. Never rewrite
them to `completed`.*** The hub checked its own reference implementation rather than the prose —
`lib/trdd-doctor.ts::expectedZone` has returned `'archived'` for all **five** of
`completed|cancelled|superseded|published|live` all along, and `trdd-graph.ts::TERMINAL_DONE`
agrees. The IND base's three-value list was simply narrower than the semantics §12 already
asserted. *"A protocol that can only be obeyed by deleting information is the thing that is
wrong."* Filed as the janitor IND-base amendment `janitor#143`.

Executed here: **pure `git mv` of 12 cards into `design/archived/`, no content edit, every
`column:` untouched.** All 12 staged as `R` (rename, zero delta). `design/tasks/` now holds
exactly the 3 genuinely-open cards.

> **My "13" was itself off by one — the correct figure is 12 (2026-07-31).** The hub's own
> proposal text carries a qualifier its ruling did not restate: **`complete` is terminal only
> when `release-via: none`** (or absent). With `release-via: publish|deploy` a `complete` card
> still has its publish/deploy stage ahead, so it is legitimately OPEN. Measured:
> `TRDD-P83T33EN` is `complete` + `release-via: publish` → it **stays** in `design/tasks/`.
> Archived: 5 `published` + 7 `complete` (1 explicit `none`, 6 absent). **Lesson: a ruling's
> summary line is not its full text — when the authority's own proposal carries a qualifier
> the ruling omits, the qualifier still binds.** Third revision of this count (13 → 6 → 13 →
> 12); the first two were reasoning errors, this one is a rule I had not read closely enough.

> **WHY a pure rename and not the archival protocol's edit-then-move.** The ruling's step 2:
> a zone move stages the rename **from the blob already in the INDEX**, so an edit made
> before the `git mv` stays UNSTAGED at the new path — it has bitten the hub's corpus three
> times, which is why their `moveZone` re-stages. A pure `git mv` sidesteps it entirely, and
> it is also the only form that respects §12's freeze on terminal bodies. The archival act is
> recorded in the commit message; `updated:` was NOT bumped because a rename is not an edit.

> **NOT fixed, deliberately: three archived cards contradict themselves.** `TRDD-9a8aba94`,
> `9e80e484`, `9f10ed97` each carry `column: complete` (line 4) **and** `**Status:** Not
> started` (line 19). This is what fed the janitor's `trdd-drift` false positives — its v1
> fallback scanned the first 4 KiB (frontmatter **plus body**) for `^\*\*Status:\*\*`, so body
> prose outranked the column (fixed janitor-side in `0e0e07b`, `janitor#135` CLOSED). The
> janitor's own note: *"my fix only makes the janitor ignore it. A human still reads 'Not
> started' nineteen lines in."* §12 freezes those bodies, so correcting them needs its own
> card. The fleet-wide rule is `3P-TRDD-10` (one pipeline claim per card) tracked as
> ai-maestro `TRDD-FKGMNGJB`; 98 files across 13 corpora carry a body `**Status:**` line.

> **The amendment is shipped but NOT installed here — do not be surprised by a stale §12.**
> janitor `0.64.1`'s `rules/trdd-design-tasks.md` §12 already carries the five-value
> archive-eligible clause. The copy installed at `~/.claude/rules/trdd-design-tasks.md` on
> this machine is byte-identical to **0.60.1**, which stops at *"Terminal columns are
> frozen."* Cause: `janitor#141` — `install_rules` overwrites on any byte difference with no
> version comparison, so a session that loaded an OLDER plugin version rolls the user-scope
> rules **backward**. **General form, worth keeping: an IND-base amendment that any older
> session can silently revert is not deployed, however correct its text.**

**2026-07-31 — `ai-maestro#97` ANSWERED, and exercising the answer found a false green.**
The hub gave CORE the SPEC pointer and a change signal it asked for. Both respond. Together
they currently report "current" for a spec that is three minor versions stale:

| | value | measured |
|---|---|---|
| authority URL (`governance-rules` branch) | `spec-version: 1.1.1` | spec file last committed there `e3968343`, **2026-07-22** |
| hub's working copy | `spec-version: 1.4.0` | `updated: 2026-07-31T07:03` |
| the 3 commits carrying 1.2.0→1.4.0 | `532bfc2b` `0a02f6f9` `d255b52a` | **HTTP 422 "No commit found"** on the remote — committed, never pushed |

The signal the hub documented — `gh api repos/Emasoft/ai-maestro/commits/governance-rules
--jq .sha` — **did** move (`7b1a3e64` → `ea97c73c`). Its four commits are `docs(lessons)`,
`docs(pm2)`, `fix(oauth-rotator)` and a TRDD zone move: real, none governance. So a
conforming consumer polls, sees movement, refetches, gets the same 1.1.1, and records
"checked, current." `3P-TRDD-09/10/11` — the clauses the hub told the janitor to conform to
on `janitor#135`, citing `3P-CHK-03` — `grep` to **0** hits at the authority URL.

**Use this instead (verified before proposing it on the thread) — the blob sha, which moves
if and only if those bytes move, and unlike `spec-version:` also covers the unversioned
overlays:**

```bash
gh api "repos/Emasoft/ai-maestro/contents/design/specs/3-pillars-spec.md?ref=governance-rules" --jq .sha
gh api "repos/Emasoft/ai-maestro/contents/rules/aimaestro?ref=governance-rules" --jq '.[] | "\(.sha[0:12])  \(.name)"'
```

> **The pattern, three instances in one day — this is the durable part.** `janitor#141` (rule
> ships in 0.64.1, installs as 0.60.1) · `janitor#143` (§12 amended, the archival section a
> reader follows maybe not) · `#97` (spec at 1.4.0, authority serves 1.1.1). Same shape:
> **an amendment the designated authority does not serve is not published, however correct
> its text** — and in two of the three the consumer had a green check saying otherwise.
> **Lesson: a coarse change-signal is self-correcting only if the watched location is
> AUTHORITATIVE. If it can lag its own source, "diff and see nothing" confirms the mirror and
> reads as "source unchanged" — noise becomes a false GREEN.** Captured as
> `ATOM-OK89-R1S5` on the USER-scope `debugging-methodology-causal-attribution-and-design`
> page, qualifying an atom written the same day that called coarse signals merely "annoying".
**Related finding (CORE-side, not a defect):** CORE has **no `.claude/rules/` at all** — it is
not a registered agent workdir, so the DEP overlay was never seeded here (it exists in
`~/ai-maestro/` and other workdirs). CORE's skill refs to `.claude/rules/aimaestro-*.md` are
correct AT THE POINT OF USE (an agent in a seeded workdir resolves them), but CORE cannot
self-check its teaching against the live rule, and **this session is steered by the orphan**.
Also measured, and it guards a real hazard: `~/.claude/rules/` holds **32 files, only 8
janitor-MARKED** — the other 24 are the USER's own hand-authored rules. So "absent marker"
means *not janitor-installed*, NOT *orphan*; a sweep by marker-absence would delete 24 user
rules. The by-NAME sweep the janitor proposed is the correct mechanism.
· ~~no `.github/dependabot.yml`~~ **DONE 2026-07-25** (`886778d`) — github-actions +
cargo + uv; it immediately opened 10 PRs, 4 of them cargo
· ~~stale tracked `validation-report.md` + `fix-log.md` (2026-04-10, ship to every consumer)~~
**DONE 2026-07-31** — `dee2bf3`. (This was the SECOND listing of the same item; I struck only
the first and left this one reading as open work. **Lesson: after resolving a backlog line,
grep the document for the item — a backlog that lists a thing twice will report it undone
once.**)
· ~~15~~ **16 skills (verified 2026-07-28** — `grep -rl 'Loaded by' skills/*/SKILL.md`; the
audit's 15 was the second soft count it produced, after the "13 terminal TRDDs" that were 6)
carry the retired `Loaded by ai-maestro-plugin` description suffix. **Deliberately NOT swept.**
It is 16 files of consumer-visible metadata, the descriptions are what drive skill *triggering*,
and nothing forces it — CPV v3.22.3 validates **exit 0** with the suffix present. An unrequested
16-file description sweep buys a few tokens and risks shifting skill selection; it is backlog,
not autonomous work. Note two of the 16 (`graph-query`, `docs-search`) are the RETIRED skills
already inside **D1**'s scope — sweep them there or not at all, so the two edits do not collide.

NIT: ~~untracked `.bak` clutter · empty `agents/` dir · root `.DS_Store`~~ **NOT APPLICABLE
to the artifact — measured 2026-07-31, do not "fix" these.** The ship surface is the git
archive, which contains only TRACKED files. Measured: `.bak` tracked **0** (all 14 untracked
AND gitignored), `.DS_Store` tracked **0** (gitignored at `.gitignore:2`), `agents/` tracked
**0** (empty, and git does not track empty directories). So all three are local
working-directory clutter that no consumer ever receives. **Deleting them would be a RULE 0
violation** — every one is untracked, and two live in never-delete zones (`reports_dev/`,
`.trashcan/`). **Lesson: before actioning a housekeeping finding, ask whether the artifact
can even carry it — an auditor walking the worktree sees files the package never ships.**
· **Still open — thin skill-level test coverage, now MEASURED (2026-07-31) so it is scopeable
rather than a vibe.** The audit's wording was right; here are the numbers behind it.

| surface | count | behavioural tests |
|---|---|---|
| skills | **26** | 0 files target a named skill's behaviour |
| commands | **12** | 0 |
| hook entries (`hooks/hooks.json`) | **13** | covered only via `test_ai_maestro_hook.py` (the dispatcher, not each entry) |

The suite is **99 declared test functions → 180 collected** (10 `parametrize` decorators
account for the difference — not 180 independent cases). Its 9 files aim at *scripts, hooks
and governance logic*: `cpv_network_resilience` (17), `prrd_trdd_pillars` (32),
`ai_maestro_hook` (11), `pre_push_gate` (8), `directory_guard_bash` (7),
`memory_protocol_components` (8), `pre_push_hook_integrity` (5), `publish_dependency_tag` (5),
`publish_uv_lock_sync` (6). Three of them glob over directories, so some structural checks do
reach every skill; **none exercises a skill's behaviour.** 6 of 26 skills are so much as NAMED
in `tests/`.

**Why this is recorded and NOT started autonomously.** `~/.claude/rules/plugin-tests-are-the-
plugins-job.md` is unambiguous — *"a test file for every skill, command, hook … no skill is
exempt"* — so the obligation is real and this is a genuine gap, not a nitpick. But it is
~50 new test files; that is a scope decision, and the standing guidance is to specify the
number of tests up front rather than let a test-writer agent emit ~30 per function. **Needs
one policy call from the USER** (which surfaces first, how deep, how many per skill), then it
is a `python-test-writer` fan-out. **Lesson: "thin coverage" is not actionable; 26/12/13 with
zero behavioural files is.** Measuring cost nothing and converted a NIT into a decision.

## Verified clean (do not re-audit without cause)

Schema `CRITICAL=0 MAJOR=0 MINOR=0 NIT=0` · cache discipline clean · version
4-way consistent (`plugin.json` = tag = CHANGELOG = marketplace @ 2.10.0) · both
dependencies resolve · **zero** dangling cross-references · zero name collisions ·
100% of GitHub Actions SHA-pinned with per-job timeouts and scoped permissions ·
168 files scanned by trufflehog/semgrep/gitleaks/cc-audit/tirith → 0 genuine
findings · ruff, `mypy scripts/ --ignore-missing-imports`, pytest (180 pass),
jscpd all green.

## Approval log

- 2026-08-07T12:02:40+0200 — PUBLISHED + ARCHIVED. Work shipped: all six implementation-commits (2ebabc4, fbe7670, f1b1d40, e8a5315, 6cceb62, c3dc41b) are ancestors of main and rode out in released versions up to v3.0.5. The card had recorded `complete` but never advanced to its release-via terminal.
