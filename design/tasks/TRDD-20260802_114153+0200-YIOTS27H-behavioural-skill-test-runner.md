---
trdd-id: YIOTS27H
title: Design a behavioural test runner for skills and commands — structural contracts cannot catch a skill that teaches the wrong thing
column: dev
created: 2026-08-02T11:41:53+0200
updated: 2026-08-02T11:58:00+0200
current-owner: core-session
task-type: spike
min-approval-requirement: none
npt: []
eht: []
---

# Behavioural test runner for skills and commands

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative; supersedes the body) — 2026-08-02

**Shipped and green.** `tests/test_skill_cli_contracts.py` — 15 tests, suite **267** passing,
ruff clean, both contracts falsified by mutation. Three of four acceptance boxes are met as
written; the second is met **with two recorded deviations** (read "Deviations" — the boxes
alone will mislead you).

**NEXT ACTION — one decision, not code:** answer whether `AIMAESTRO_CLI_REQUIRED=1` should
convert the environment skips into hard failures for local/pre-push runs. CI cannot ever hard-
fail these (no AI Maestro on the runner). Until that is answered the card stays in `dev`.

**Load-bearing gotchas, in the order they will bite you:**
- The extractor's `lstrip()` on fences is **not cosmetic** — anchoring at column 0 makes an
  indented fence invisible and the contracts pass VACUOUSLY. `test_the_extractor_actually_
  extracts` is the only thing that catches it; never weaken it.
- `$(...)` is stripped before flags are read. Removing that makes the suite report undeclared
  flags on *correct* skills.
- The frozen CLIs advertise flags **inline inside a usage block**. Any future "improvement"
  that parses a flag list instead of substring-matching `--help` will produce false negatives
  on 2 of 3 CLIs (measured).

**SUPERSEDED — do NOT carry forward:**
- The body's proposed *"extract fenced bash blocks"* shape — replaced by D1 (dual extraction).
- The `# test: runnable` opt-in marker — **never implement it**; D3 dissolved the need.
- The body's check (4) *"blocks marked read-only actually run"* — dropped with the marker.
- The body's check (3) *"exit codes reachable"* — undecidable from `--help`; replaced by the
  subcommand check.

**Artifacts to read first:** `tests/test_skill_cli_contracts.py` module docstring (carries
D1/D2/D3 with the numbers), then the Deviations section below.

## Why this card exists at all

The gap was real and tracked **only** in `.janitor/state/agent-handoff.md` — a gitignored,
machine-local file. Any other contributor cloning this repo could not see it, and it would
have died with this machine. That invisibility is the defect this card fixes first; the
runner is the work it makes visible.

## The gap, stated precisely

`tests/test_skill_and_command_contracts.py` (`ed95526`, 78 tests) covers all 28 skills and
14 commands **structurally**: frontmatter parses, `name:` matches its directory, a `/name`
promise is backed by a real surface, the README table agrees with disk in both directions,
and `allowed-tools` permits the script each frozen-CLI wrapper teaches.

Every one of those checks reads the file as **data**. None of them execute what the skill
**instructs**. So the entire class of defect that matters most is invisible to the suite:

| Defect class | Caught structurally? |
|---|---|
| `name:`/dir drift, empty description, broken README row | ✅ yes |
| wrapper omits its own CLI from `allowed-tools` (core#51) | ✅ yes |
| a skill teaches a **command that does not exist** | ❌ no |
| a taught command's **flags have changed** upstream | ❌ no |
| a taught exit-code contract is **wrong** (the `0`/`1`/`2` trichotomies) | ❌ no |
| a worked example's commands **do not run** | ❌ no |

The last four are exactly the failures the frozen-CLI wrappers exist to prevent, and they
are the ones that reach an agent as "the tool is missing" or, worse, as a silently wrong
authorization decision (`ama-portfolio`'s `verify` trichotomy).

## What is NOT wanted

- **More structural sweeps.** They are done; adding assertions to that file does not touch
  this gap and will read like progress.
- **Mocking the CLIs.** A mocked `aimaestro-portfolio.sh` proves the skill agrees with the
  mock, which is worth nothing. If a live service is needed, ask the owner to start it.
- **Executing a skill's prose with an LLM in CI.** Non-deterministic and unaffordable as a
  gate.

## The shape worth exploring first

Extract the **fenced `bash` blocks** from each SKILL.md and assert facts about them that do
not require running destructive commands:

1. every command word resolves (`command -v`) — catches "teaches a CLI that does not exist";
2. every long flag taught appears in that CLI's own `--help` — catches upstream flag drift;
3. every documented exit code is reachable per the CLI's `--help`/usage — catches a wrong
   trichotomy;
4. blocks marked read-only actually run and exit as documented.

(1)–(3) are static against a live `--help`, need no service, and are cheap. (4) needs a
per-block opt-in marker so a destructive example is never executed by the suite.

**Open question the spike must answer:** how blocks opt in/out. A comment marker
(`# test: runnable`) is the obvious candidate but adds syntax to 28 skills — verify against
the shipped files before committing to it.

## DECISION (2026-08-02) — measured against the shipped files, as this card demanded

The measurement overturned the shape proposed above. Three decisions, each with the
rejected alternative and the number that killed it.

### D1 — Select by SHAPE, not by fence. (Rejects the `# test: runnable` marker entirely.)

| where the 6 frozen CLIs are mentioned | count |
|---|---|
| inside fenced code blocks | **42** |
| outside fenced code blocks | **38** |

Fence-based selection misses ~47% of mentions. The misses are not noise: `<example>`
sections teach real invocations **with flags** as inline code spans, e.g.
`skills/ama-portfolio/SKILL.md:126` → `aimaestro-portfolio.sh verify --subject … --binds …`.
Those carry flags, so they are exactly the lines most likely to drift.

**Chosen:** extract anything matching `<known-cli> <subcommand> [--flags]` from BOTH fenced
code and inline code spans. **Rejected:** fence-only + an opt-in comment marker — it would
have added syntax to 28 skills *and* covered less.

### D2 — Check flags by SUBSTRING PRESENCE in `--help`, never by parsing a flag list.

A line-anchored parse (`^\s*--[a-z-]+`) reported **"no flags advertised"** for
`aimaestro-continuity.sh` and `aimaestro-settings.sh`, and found only 6 of portfolio's
flags. All of that was false — the CLIs advertise their flags *inline* inside a usage block:

```
set <path> --key <dot.path> --value <json-or-string> [--no-create]
restart-self [--force]
```

Re-tested as plain substring presence, **all 7** flags `ama-portfolio` teaches
(`--subject --token --binds --binds-team --scope --ttl --json`) are PRESENT. **Rejected:**
structured flag parsing — it manufactured two false "unimplementable" verdicts out of three
CLIs. This is the third time in one session that a freshly-written check indicted working
code (`id:ATOM-FP3O-ZGLD`); the shipped artifact was right every time.

### D3 — Execute NOTHING that a skill teaches. (Drops the card's check (4).)

Checks (1)–(3) are static against a live `--help`. Since nothing from a SKILL.md is ever
run, the destructive-block problem and the opt-in marker both **dissolve** rather than
needing a solution — 4 of the 24 fenced blocks contain `revoke`/`delete`/`git commit`/`mint`
and must never auto-run. **Dropped:** check (4) ("blocks marked read-only actually run") —
it was the sole reason a marker was needed, and it buys little over (1)–(3).

**Consequence for `--help`:** the runner must FAIL, not skip, when a CLI is absent from
`PATH` — a skipped check is a green that means nothing (already in Acceptance).

## Acceptance

- [x] A written decision on the block-selection mechanism, with the alternative rejected and why
      — see DECISION above (D1/D2/D3), each backed by a measurement against the shipped files
- [x] (1)–(3) implemented for the six frozen-CLI wrappers — `tests/test_skill_cli_contracts.py`,
      15 tests, suite 252 → **267**. **TWO DEVIATIONS from this criterion's wording, recorded
      rather than quietly satisfied — see "Deviations" below.**
- [x] A deliberate mutation is shown to REDDEN the suite — mutated `mint`→`mintx` and
      `--ttl`→`--ttlx` in `ama-portfolio`: exactly the flag contract and the subcommand
      contract went red (2 failed / 13 passed), `git checkout --` restored byte-exact,
      15 passed again.
- [x] `reports/` stays gitignored; no report committed — `.gitignore:38-39`, `git ls-files
      reports/ reports_dev/` = 0

## Deviations from the acceptance criteria (do NOT read the boxes above without these)

**1. "failing loudly when a CLI is absent" → implemented as SKIP with a named reason.**
CI (`ci.yml:223`, `release.yml:133`) runs `pytest tests/` on a runner with **no AI Maestro
install**, so a hard failure would redden every CI run permanently and be suppressed inside a
day — strictly worse than the skip it replaced. Implemented instead as the repo's existing
convention (`shutil.which(...) is None` → skip, matching `test_ai_maestro_hook.py:34`), with
the CLI **named** in the reason so it is never silent, PLUS
`test_the_extractor_actually_extracts` and the two leak tests, which **never skip** and fail
if the extractor stops finding known-shipped invocations. That closes the real hazard the
criterion was aimed at — a vacuous green — without the CI cost. **Open for the owner: should
a `AIMAESTRO_CLI_REQUIRED=1` env var turn the skips into hard failures for local/pre-push runs?**

**2. Check (3) "exit codes reachable" → implemented as SUBCOMMAND presence.**
"Every documented exit code is reachable per `--help`" is not decidable from `--help` text —
none of the six enumerate their exit codes there, so the check would have been unfalsifiable.
Substituted the check that is both decidable and higher-value: **every subcommand a skill
teaches must appear in `--help`**, which catches a renamed or removed subcommand — the loudest
way a frozen CLI can break a skill. The exit-code trichotomies (`ama-portfolio` 0/2/1,
`ama-trdd-find`) remain **unverified by machine**; they are prose-only and would need the CLI
to be invoked with a failing input, which D3 forbids.

## Two extractor bugs this work found — both in MY check, not in the skills

Recorded because the pattern repeated four times in one session (`id:ATOM-FP3O-ZGLD`), and the
next person to extend this file will hit it again:

1. **Indented fences were invisible.** `raw.startswith("```")` misses `   ```bash` inside a
   numbered list, which silently swallowed `ama-portfolio`'s entire `mint` example — the only
   place `--binds-team`/`--kind`/`--ttl` are taught. The contracts still PASSED, because an
   extractor that finds nothing asserts nothing. Caught only by the never-skipped guard.
2. **`$(...)` leaked inward.** The first real run reported `aimaestro-session.sh --cwd` as an
   undeclared flag. Both the skill and the CLI were correct: `--cwd` belongs to the
   `aimaestro-agent.sh resolve` nested in a command substitution. Had I "fixed" the skill, I
   would have deleted a correct flag from working documentation.

Both now have dedicated never-skipped regression tests.

## Notes

- The CLIs are **frozen**, so (2) is stable rather than churn-prone; that is what makes this
  worth automating instead of re-reading by hand.
- Contract-test provenance and the `user-invocable`-defaults-to-TRUE near-miss are recorded
  in the test module's own docstring — read it before extending the file.
