---
trdd-id: 8ZVAPMSQ
title: Pre-push hook contributor path — allow non-default-branch pushes without publish.py ancestry
column: proposal
created: 2026-07-16T11:43:11+0200
updated: 2026-07-16T11:43:11+0200
current-owner: ai-maestro-plugin (core)
task-type: infra
min-approval-requirement: manager
relevant-rules: [how-to-fix-issues-of-other-projects]
parent-trdd:
blocked-by: []
npt: []
eht: []
---

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative; supersedes the body) — 2026-07-16

**Status: PROPOSAL awaiting MANAGER approval.** The MANAGER pre-committed on
core#26 ("Pick (a) or (b), file the TRDD, and I will approve it") and put the
deadlock on the launch gate list (ai-maestro#63). CORE recommends **(a)**.
Once approved: move to `design/tasks/`, `column: planned`, then implement.

## The problem (MANAGER ruling, core#26)

Verified deadlock, launch-blocking:

- `.githooks/pre-push` requires EVERY push to descend from a genuine
  `python scripts/publish.py` process (ancestry walk, not env-var gated).
  It is not scoped to a branch or to tags.
- `publish.py` refuses to run off the default branch (MED-06).
- The `baseline-pr-and-checks` ruleset (active) requires a PR.

⇒ A hook-installed clone cannot push a feature branch; no feature branch ⇒ no
PR; the ruleset requires a PR; the only way in is the admin bypass. The fleet's
`how-to-fix-issues-of-other-projects` rule tells every contributing agent to
use fork → PR — at launch, the first MAINTAINER agent that tries hits this wall.

## Decision: option (a) — a contributor path IN the hook

Chosen over (b) ("contributors don't install the hook") because (b) makes the
protection opt-in and silently absent exactly where mistakes happen; (a) keeps
enforcement always-on while admitting the one legitimate non-publish flow.

**New hook contract** (everything not listed stays exactly as today):

| Push shape (from the pre-push stdin refspecs) | Verdict |
|---|---|
| ALL remote refs are `refs/heads/*` AND none is the default branch AND none is `refs/tags/*` | **ALLOW** (no ancestry required) — the contributor path: create/update/delete a feature branch |
| ANY remote ref is the default branch (`refs/heads/main`) | require `publish.py` ancestry (unchanged) |
| ANY remote ref is `refs/tags/*` | require `publish.py` ancestry (unchanged) |
| Anything else (`refs/notes/*`, unknown namespaces) | require `publish.py` ancestry (fail-closed default) |

Invariants preserved: you still cannot move `main`, ship a release, or forge a
tag without going through `publish.py`. The ancestry hardening (anti-spoof
`find_publish_ancestor`) is untouched. `publish.py` MED-06 stays. The
`baseline-pr-and-checks` ruleset is NOT modified — this change makes the PR
requirement *satisfiable*, which is the point.

**The default branch is resolved dynamically** (`git symbolic-ref
refs/remotes/origin/HEAD`, falling back to `main`) — never hardcoded to a name
that can drift.

## Derived tasks (execute with the implementation)

1. **Update the hook's sha256 pin in the SAME commit** — the hook is a static
   committed file whose hash is CI-verified (TRDD-71a2239a). A hook edit
   without the pin move turns CI red and, worse, a pin-less window would let a
   tampered hook pass unnoticed.
2. **Tests**: extend the hook's test coverage with the four verdict rows above
   (feature-branch push allowed; main push refused; tag push refused; mixed
   push refused) — real invocations of the hook with synthetic stdin, no mocks.
3. **Docs**: update the hook header comment + CONTRIBUTING notes so the
   contributor flow (fork → branch → PR) is documented as now actually possible.
4. **Report back**: post the landed commit on core#26 and notify the MANAGER
   so the ai-maestro#63 launch-gate row can be closed.

## Approval log

- 2026-07-16 — filed as proposal; MANAGER approval requested on core#26
  (MANAGER pre-committed to approve option (a) or (b) on 2026-07-15).

## Notes and lessons learned
