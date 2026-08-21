---
trdd-id: 8ZVAPMSQ
title: Pre-push hook contributor path — allow non-default-branch pushes without publish.py ancestry
column: proposal
created: 2026-07-16T11:43:11+0200
updated: 2026-08-21T16:39:01+0200
approval-tier: 2
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

**RE-VERIFIED 2026-08-07 — the premise still holds; this has NOT gone moot.** Read
`.githooks/pre-push` at HEAD (active: `core.hooksPath=.githooks`): it consumes **no ref
lines at all** — no `refs/heads` read, no branch or tag scoping anywhere — and its only
decision is `if ! find_publish_ancestor "$$"; then … exit 1`. So **every** push without a
genuine `scripts/publish.py` ancestor is refused, on any branch. The deadlock this proposal
describes is unchanged and still launch-blocking. (Worth re-checking rather than assuming:
the sibling issue `#34` DID go moot while parked, so a stale proposal is a real risk here.)

**RE-VERIFIED AGAIN 2026-08-21 — hook premise HOLDS, but one of the three deadlock legs is
now GONE. Classified Tier 2. Approver is the USER.**

- **Leg 1 (hook) — STILL TRUE.** `.githooks/pre-push` at HEAD (213 lines, `core.hooksPath=.githooks`
  confirmed active) contains no `refs/heads` or `refs/tags` read anywhere; its only decision is
  `if ! find_publish_ancestor "$$"` (line 195) → `exit 1` (line 210). Unscoped, as described.
- **Leg 3 (ruleset requires a PR) — NO LONGER TRUE.** `baseline-pr-and-checks` (17715691) carries
  rules `[required_status_checks]` ONLY — no `pull_request` rule. Removed by USER ruling
  2026-08-13 (self-approval is impossible on a solo-owner repo, so a 1-approval gate was
  unsatisfiable). Verified live this session.

**What that changes:** the OWNER is no longer deadlocked — they can push `main` through
`publish.py` with no PR needed. What remains is narrower and still real: a CONTRIBUTOR who
installs the hook cannot push a feature branch at all, so the fork → branch → PR flow that
`how-to-fix-issues-of-other-projects` mandates is still impossible for them. Keep the proposal,
drop the "launch-blocking deadlock" framing.

**Ref pinned — the launch-gate row is `Emasoft/ai-maestro#63`, and the bare form is a trap.**
Verified 2026-08-21: `Emasoft/ai-maestro#63` is the OPEN launch issue ("MANAGER needs the launch
plan … go/no-go gates"), but `23blocks-OS/ai-maestro#63` is a MERGED PR about legacy host-id
migration. Same number, two repos, opposite status — so a bare `#63` read against the wrong
remote returns the OPPOSITE conclusion about whether this gate is still live. Always write the
`owner/repo#N` form here. The row IS live; re-check it before citing this card's urgency.

**TIER 2 — USER approval, not MANAGER, not self-mandate.** The change loosens a push gate that
every contributor is forced through: it converts "every push needs `publish.py` ancestry" into
"feature-branch pushes need none". That is a security-control relaxation on a forced path, which
is Tier 2 even though `.githooks/` is not `.github/` and no ruleset is touched. The card's own
`min-approval-requirement: manager` predates the current tier model; the hub session holds no
MANAGER title over this repo and has explicitly declined to rule on it. Conservative default
applies: when unsure, escalate one tier.

CORE still recommends **(a)**. On USER approval: `git mv` to `design/tasks/`, `column: planned`,
then implement with all four derived tasks below — the sha256 pin move in the SAME commit is
load-bearing, not optional.

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
- 2026-08-21T16:39:01+0200 — CLASSIFIED **Tier 2 (USER)**, still PENDING — no verdict rendered.
  Premise re-verified: hook leg holds at HEAD, ruleset leg is gone (see STATE). Routed to the
  USER rather than left implicit: this card had sat 36 days on an unasked question, which is the
  failure mode being corrected, not a queue that was simply slow. NOT self-approved as Tier 0
  despite living entirely in this repo — it relaxes a security gate on a path every contributor
  is forced through.

## Notes and lessons learned
