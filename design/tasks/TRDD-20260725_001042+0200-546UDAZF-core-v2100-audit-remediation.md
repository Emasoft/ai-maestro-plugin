---
trdd-id: 546UDAZF
title: Remediate the CORE v2.10.0 full-audit findings
column: backburner
created: 2026-07-25T00:10:42+0200
updated: 2026-07-26T06:50:27+0200
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

**OPEN DEFECT found while publishing v2.11.0 (2026-07-26) — CI `Validate` intermittently
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

**Load-bearing facts / gotchas:**

- **The 9 security findings are ALL false positives** — verified line-by-line. Eight
  are inverted-polarity (a security *guard* flagged for the pattern it *blocks*);
  one is a markdown blockquote `>` read as a shell redirect. **`directory-guard.cjs`'s
  detector regexes are LOAD-BEARING runtime code — flag, never devitalize.**
  Allowlist them so future scans stop re-litigating.
- **Warnings #23 / #24 are false positives that must NOT be "fixed"** — the validator
  itself says `ci.yml` / `release.yml` carry hardening the canonical template lacks.
  Aligning them to canon would be a **downgrade**.
- **Warning #19** (memgrep compile source shipping in-tree) is a **deliberate,
  accepted architectural deviation** — CORE hosts the memgrep engine for the whole
  ecosystem. Decide it once here rather than re-triaging it every release.
- Warning counts: **28 triaged → 9 genuine · 13 false-positive · 6 cosmetic.**

**SUPERSEDED — do NOT carry forward:**

- "27 warnings" — the brief cited 27; the audit run observed **28**. Use 28.
- Any plan to fix MAJOR-1: it is done (`2df4829`). Do not re-edit README Requirements.
- Any reading of the audit's "unpushed commits" / "missing `rules/` dir" as defects —
  both were confirmed **expected state** (CORE reaches the remote only via
  `publish.py`; governance rules were deliberately retired to the janitor IND bases
  + ai-maestro DEP overlays).

## Lower-severity backlog (from the same audit)

MINOR: stray `scripts/memgrep/SKILL.md` with no frontmatter (rename to `README.md`)
· 13 terminal TRDDs parked in `design/tasks/` instead of `design/archived/`
· no `.github/dependabot.yml` (100% SHA-pinned actions with no update channel = pins rot)
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
