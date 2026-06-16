---
name: ama-proposal-approvals
description: "Batch-approve, refuse, or archive TRDD proposals — move them between the four design/ zones (proposals/ to tasks/ on approve; to refused/ on refuse; to archived/ on complete/cancel/supersede). GATED: only a MANAGER (or solo USER) may approve/refuse/archive; the COS relays but does not approve; list is open to all. Use when a MANAGER drains the proposal queue or archives a finished/cancelled/superseded TRDD. Trigger with /ama-proposal-approvals, 'list pending proposals', or 'approve proposals 4,6'. Column moves within tasks/ are /ama-trdd-transition."
allowed-tools: "Bash(python3:*), Bash(sh:*), Bash(amama_proposal_approvals.py:*), Bash(resolve_pillar_scripts.sh:*), Bash(git:*), Read, Grep, Glob"
metadata:
  author: "Emasoft"
  version: "1.0.0"
---

# ama-proposal-approvals — batch proposal approvals (GATED)

## Overview

`ama-proposal-approvals` operationalizes the four zone-moving decisions on a
TRDD's lifecycle: **approve** (`proposals/` → `tasks/`, sets `column: planned`),
**refuse** (→ `refused/`), and **archive** (→ `archived/` as
`completed`/`cancelled`/`superseded`). Each decision appends an `## Approval log`
line and `git mv`s the file (never deletes — RULE 0). It is the choke-point for
proposal gating, double-gated by your role AND the script's authority check.

## Permission (this skill's matrix row) — SELF-CHECK BEFORE RUNNING

| Op | MANAGER | ORCH | ARCH | INT | COS | MEMBER | AUTON | MAINT |
|---|---|---|---|---|---|---|---|---|
| **list proposals** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **approve / refuse / archive** | ✅ | ❌ | ❌ | ❌ | relay-only | ❌ | →MANAGER | →MANAGER |

**The routing rule (do this BEFORE the decision):**

- **List** is open to every role (read-only) — anyone can see the pending queue.
- **approve / refuse / archive** is **MANAGER-only** (the approver). Use `--user`
  only when working solo without an AI Maestro server.
- **COS relays** proposals to the MANAGER and forwards the MANAGER's verdict
  back to the team — the COS does NOT itself approve (Tier-1 team-internal
  coordination it handles is a different surface; PRRD/TRDD approval is MANAGER's).
- **Any other role** must NOT approve. Surface the request to the MANAGER (via
  COS for team-internal agents).

Hard backstop: `require_manager()` in the script calls
`prrd_lib.caller_is_manager()` (`$AID_AUTH` → server). A non-MANAGER `approve` /
`refuse` / `archive` without `--user` is refused with exit 4.

## Prerequisites

- The project has a 4-zone `design/` tree (`proposals/`, `tasks/`, `refused/`,
  `archived/`) with the proposals/TRDDs you intend to move. Bootstrap with
  `bootstrap_design.py` / `get-prrd.py --init` if absent.
- Python 3.10+ on PATH. The pillar scripts live at
  `${CLAUDE_PLUGIN_ROOT}/scripts/prrd-trdd/` and are resolved at runtime via
  `resolve_pillar_scripts.sh` (works from the core plugin OR any role plugin).
- You know your governance ROLE (MANAGER / ORCH / ARCH / INT / COS / MEMBER /
  AUTONOMOUS / MAINTAINER) — this skill's permission matrix is keyed on it.

## Instructions

1. Resolve the pillar-scripts directory:

   ```bash
   DIR="$(sh "$CLAUDE_PLUGIN_ROOT/scripts/prrd-trdd/resolve_pillar_scripts.sh")" || exit 1
   ```

2. List (any role), then decide (MANAGER):

   ```bash
   python3 "$DIR/amama_proposal_approvals.py" list                     # numbered table; records a number->id manifest
   python3 "$DIR/amama_proposal_approvals.py" approve 4,6 --user       # approve EXACTLY those (rest stay pending)
   python3 "$DIR/amama_proposal_approvals.py" refuse 7,8 --approve-rest --user   # refuse named, APPROVE the rest
   python3 "$DIR/amama_proposal_approvals.py" archive 9a8aba94 --state completed --user
   python3 "$DIR/amama_proposal_approvals.py" archive 9a8aba94 --cancel --user   # alias for --state cancelled
   ```

   A selector is a list-NUMBER (resolved against the most recent `list`, by
   stable `trdd-id`) OR an 8-char id / full uuid. **Batch verbs:** `approve: 4,6`
   approves exactly those (conservative — silence = still pending); `refuse: 7,8`
   with `--approve-rest` refuses the named few and approves everything else (the
   bulk path — use only after reviewing the whole list).

## Output

A per-decision summary on STDOUT (each move logged + `git mv`-ed); errors on
STDERR. Exit 4 = authority refused (you are not MANAGER — escalate). Exit 0 on
success.

## Examples

<example>
A MANAGER drains the queue: approve most, refuse two.
→ `amama_proposal_approvals.py list`, then
  `amama_proposal_approvals.py refuse 12,15 --approve-rest --user`.
</example>

<example>
A finished TRDD needs archiving as completed.
→ `amama_proposal_approvals.py archive 485a04ad --state completed --user`.
</example>

<example>
An ORCH agent wants to approve a proposal.
→ DO NOT. ORCH cannot approve. Surface it to the MANAGER (via COS); only the MANAGER runs approve.
</example>

## Scope

Moves TRDDs between the four design/ zones (proposal approval / refusal /
archival). MANAGER-gated for the decisions; list is open. Column moves WITHIN
`tasks/` (e.g. `dev → testing`) are a different op — use `ama-trdd-transition`.

## Error Handling

On non-zero exit the message is on STDERR. **Exit 4 = authority refused** — the
script's `caller_is_manager()` gate rejected a non-MANAGER mutation; this is the
gate working as designed. Do NOT retry with `--user` unless you ARE the solo
USER; instead route per the permission matrix (propose / escalate). Exit 2 = a
precondition failed (PRRD/TRDD missing — bootstrap first); exit 3 = not found.
If `resolve_pillar_scripts.sh` exits 1, the ai-maestro-plugin base is not
installed — set `$AI_MAESTRO_PRRD_SCRIPTS_DIR` or install the base.

## Resources

- [../ama-trdd-transition/references/scripts-usage.md](../ama-trdd-transition/references/scripts-usage.md) — full usage of ALL pillar scripts + the canonical TRDD skeleton + exit codes + per-role examples.
  > Contents · resolve_pillar_scripts.sh — locate the scripts from any plugin (delivery mechanism) · get-prrd.py — read PRRD rules · prrd-edit.py — mutate the PRRD (MANAGER-only for direct mutation) · findprrd.py — search PRRD rules · findtrdd.py — find TRDDs · kanban.py — render the board (READ-ONLY) · bootstrap_design.py — create the 4-zone design/ folders · amama_proposal_approvals.py — batch proposal approvals (list/approve/refuse/archive) · Authoring a new TRDD (canonical skeleton) · Exit codes · Per-role quick examples
- [../ama-trdd-transition/references/pillar-scripts-delivery.md](../ama-trdd-transition/references/pillar-scripts-delivery.md) — how a role plugin reaches the base's pillar scripts at runtime (the resolver, env override, depend-vs-bundle).
  > Contents · Two supported delivery models · Why a resolver, not a hard-coded path
- [../ama-trdd-transition/references/approval-tiers-and-zones.md](../ama-trdd-transition/references/approval-tiers-and-zones.md) — the four zones + `proposal → planned` lifecycle + Tier 0/1/2/3 ladder + batch-approval syntax.
  > Contents · A. The four design zones · B. The `proposal → planned` lifecycle · C. The four-tier approval ladder · The objective tier-floor (mechanical, greppable) · Asynchronous enforcement (never block) · D. Single-writer-per-domain (collision avoidance) · Batch approval syntax (the fast path)
- [../ama-trdd-transition/references/cos-delegation-authority.md](../ama-trdd-transition/references/cos-delegation-authority.md) — the COS relay/escalation model.
  > Contents · The two-tier model · How escalation composes with presence (the full chain) · COS-AUTONOMOUS — the COS decides, no upstream · Category CA-A — Intra-team task coordination · Category CA-B — Approving EXEMPT-tier operations · Category CA-C — Team health & lifecycle · Category CA-D — Information & triage · COS-ESCALATE — forward to MANAGER · Category CE-X — MANAGER hard-floor · Category CE-Y — NON-EXEMPT operations · Category CE-Z — Resource / composition changes · Category CE-W — Governance / PRRD / baseline · Category CE-V — Cross-team · Category CE-U — Unresolvable in-team · Category CE-T — Conservative default · Consolidation — the COS batches, it doesn't flood · The COS escalation message (to MANAGER) · User-presence — where it lives, and the janitor fallback · Why this exists · Relationship to exempt-operations.md
