---
trdd-id: 546UDAZF
title: Remediate the CORE v2.10.0 full-audit findings
column: backburner
created: 2026-07-25T00:10:42+0200
updated: 2026-07-28T19:18:00+0200
current-owner: ai-maestro-plugin (core)
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

**NEXT ACTION — none autonomously. Four decisions are the USER's** (each changes
CORE's public surface, so they were deliberately NOT taken):

| # | Decision | Why it needs a human |
|---|---|---|
| D1 | MAJOR-3 + MAJOR-4 (one coupled edit): delete the RETIRED `docs-search` + `graph-query` skills, then regenerate the README skills table (`/cpv-refresh-readme`) | removes two shipped capability rows — a consumer-visible deletion |
| D2 | MAJOR-2: reconcile 13 skills whose description promises `/<name>` while `user-invocable: false` and no `commands/<name>.md` exists | three valid fixes per skill (flip the flag / add the wrapper / reword to a natural-language trigger) — needs ONE policy choice, not 13 ad-hoc ones |
| D3 | MAJOR-5 (= warning #20, highest-value): add a push/PR smoke job that builds ONE memgrep target and runs the staged binary `--version` | a CI change; the payoff is ecosystem-wide |
| D4 | warning #28: replace `.markdownlint.json`'s `{"default": false}` with canon's explicit per-rule opt-out list | flipping linting on surfaces a backlog of existing violations — expect CI churn before green |

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
and `release.yml`'s `> file 2>&1` + trailing `cat` replaced with `| tee` + **`set -o pipefail`**.
That pipefail is load-bearing: GitHub's default `run:` shell is `bash -e {0}` **without** it, so
after a pipe the captured status is `tee`'s (~always 0) and the gate would have reported success
for **every failed validation**.

**Trap hit while doing it, worth keeping:** the first draft of those `tee` comments used markdown
backticks, and backticks are command-substitution syntax to a shell — CPV's scanner flagged a
**comment** as `CMD_INJECTION` and `--strict` turned that NIT into a red gate (exit 4). Proven mine,
not the version's, by re-running `v3.22.3` against the pre-edit workflows: **exit 0**. Never write
backticks inside a `run:` block, comments included. Same class as the blockquote-`>`-read-as-redirect
false positive noted below.

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
· ~~13 terminal TRDDs parked in `design/tasks/`~~ **the count is WRONG — 6, not 13, and
the move is BLOCKED** on the archival-vocabulary ruling (`Emasoft/ai-maestro#93`); see
the conflict analysis there
· ~~no `.github/dependabot.yml`~~ **DONE 2026-07-25** (`886778d`) — github-actions +
cargo + uv; it immediately opened 10 PRs, 4 of them cargo
· stale tracked `validation-report.md` + `fix-log.md` (2026-04-10, ship to every consumer)
· 15 skills carry the retired `Loaded by …` description suffix.

NIT: untracked `.bak` clutter · empty `agents/` dir · root `.DS_Store` · thin
skill-level test coverage (9 test files, 180 tests passing, well-aimed at the risky
surfaces — the gap is skill behaviour).

## Verified clean (do not re-audit without cause)

Schema `CRITICAL=0 MAJOR=0 MINOR=0 NIT=0` · cache discipline clean · version
4-way consistent (`plugin.json` = tag = CHANGELOG = marketplace @ 2.10.0) · both
dependencies resolve · **zero** dangling cross-references · zero name collisions ·
100% of GitHub Actions SHA-pinned with per-job timeouts and scoped permissions ·
168 files scanned by trufflehog/semgrep/gitleaks/cc-audit/tirith → 0 genuine
findings · ruff, `mypy scripts/ --ignore-missing-imports`, pytest (180 pass),
jscpd all green.
