---
trdd-id: Z6QFP8MM
title: Re-sync the governance-rules mirror after the upstream restructure
column: complete
created: 2026-08-25T17:28:22+0200
updated: 2026-08-25T18:20:00+0200
current-owner: ai-maestro-plugin (core)
task-type: docs
min-approval-requirement: none
blocked-by: []
npt: []
eht: []
---

## ⏵ STATE — READ THIS FIRST ON RESUME — 2026-08-25

**NEXT ACTION:** locate the CURRENT canonical home of the R-numbered governance corpus on
`Emasoft/ai-maestro@governance-rules` (ask the hub session — they directed the re-stamp — or
list `rules/` and `design/specs/` at the branch head), then re-mirror content + stamp together.

## The problem (all facts verified 2026-08-25 against the remote)

`skills/team-governance/references/GOVERNANCE-RULES.md` is CORE's mirror of the ai-maestro
R-ruleset, stamped `version: 5.3.3`, `synced-blob: a13bed73fa9e`, `synced-at: 2026-08-08`.
Hub session ai-maestro-e5 directed (2026-08-25): "re-stamp governance version pins vs the
published blobs" at `governance-rules` head `c8b0e9cb`.

Measured: upstream `rules/aimaestro/aimaestro-agent-rules.md` at `c8b0e9cb` is blob
`83de54de3910`, **2,268 bytes** — a compact "installed-dep operating rules" file (Boundaries /
Failure / Truth / Work sections), NOT the large R-numbered corpus the 5.3.3 mirror carries.
The upstream RESTRUCTURED; a mechanical re-stamp would declare a sync that did not happen —
exactly the failure the mirror's own §0 note warns about ("incorporation must NOT copy this
stamp: declaring a version it does not have").

## Scope

1. Find where the R-rules live now (`rules/aimaestro/` has 5 files; the R-corpus may be
   split, or superseded by the 3.0.0 spec + PRRD).
2. Re-mirror CONTENT and stamp (`version`, `synced-blob`, `synced-at`) in the same edit.
3. If the R-corpus was retired upstream, the mirror needs a supersession note instead of a
   sync — do not delete it (RULE 0); mark what replaced it.
4. Re-run the governance-scenario tests that cite mirror rule numbers.

## Approval log

- 2026-08-25T17:28:22+0200 — authored directly as Tier-0 (`min-approval-requirement: none`):
  in-scope docs sync, reversible, no baseline deviation. Deliberately NOT executed as a
  drive-by during the kanban 3.0.0 migration: the restructure makes source-of-truth location
  a judgment call, and a wrong guess produces a lying stamp.
- 2026-08-25T18:20:00+0200 — **COMPLETED same session.** Hub answered the open question first-hand: canonical
  corpus = `docs/GOVERNANCE-RULES.md` @ 5.5.0, blob 44be10d5d351 (lead re-verified via gh api:
  blob + size 249063 match). Mirror re-synced by worker, then lead-verified on disk: stamp
  version 5.5.0 / synced-blob 44be10d5d351 / synced-at 2026-08-25; R42.9 present WITH the
  same-day correction (a `permissions.deny` for SendMessage is FORBIDDEN — matches what CORE's
  own governance files already state); size 217885B consistent with the mirror's standing
  exclusion of upstream's changelog block (prior 5.3.3 sync: 216002B). Full suite after sync:
  403 passed / 6 skipped (lead run). Scope item 3 (supersession) moot — corpus not retired.
