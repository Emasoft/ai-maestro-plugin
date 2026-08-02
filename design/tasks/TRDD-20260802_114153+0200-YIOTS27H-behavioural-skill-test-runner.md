---
trdd-id: YIOTS27H
title: Design a behavioural test runner for skills and commands — structural contracts cannot catch a skill that teaches the wrong thing
column: todo
created: 2026-08-02T11:41:53+0200
updated: 2026-08-02T11:41:53+0200
current-owner: core-session
task-type: spike
min-approval-requirement: none
npt: []
eht: []
---

# Behavioural test runner for skills and commands

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

## Acceptance

- [ ] A written decision on the block-selection mechanism, with the alternative rejected and why
- [ ] (1)–(3) implemented for the six frozen-CLI wrappers, failing loudly when a CLI is absent
      rather than skipping silently — a skipped check is a green that means nothing
- [ ] A deliberate mutation (rename a taught flag) is shown to REDDEN the suite before the
      card closes — an unfalsified guard is not a guard
- [ ] `reports/` stays gitignored; no report committed

## Notes

- The CLIs are **frozen**, so (2) is stable rather than churn-prone; that is what makes this
  worth automating instead of re-reading by hand.
- Contract-test provenance and the `user-invocable`-defaults-to-TRUE near-miss are recorded
  in the test module's own docstring — read it before extending the file.
