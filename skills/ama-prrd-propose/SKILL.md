---
name: ama-prrd-propose
description: "File a PRRD-change proposal for MANAGER (or USER) review without mutating the PRRD. This is the path EVERY non-MANAGER role uses to request a rule change, and the path for ANY GOLDEN-rule change (which is USER-only). Proposals are non-binding — they queue for approval. Use when an agent thinks a project rule should be added/reworded/removed but lacks the authority to do it directly. Trigger with /ama-prrd-propose or 'propose a rule change', 'suggest revising rule N'. The PROPOSAL pillar of the AI-Maestro PRRD; direct mutation (MANAGER, SILVER) is /ama-prrd-edit, reading is /ama-prrd-get."
allowed-tools: "Bash(python3:*), Bash(sh:*), Bash(prrd-edit.py:*), Bash(resolve_pillar_scripts.sh:*), Read, Grep, Glob"
metadata:
  author: "Emasoft"
  version: "1.0.0"
---

# ama-prrd-propose — propose a PRRD change (no authority needed)

## Overview

`ama-prrd-propose` writes a non-binding proposal that the MANAGER (or, for GOLDEN
changes, the USER) reviews and either accepts (then the MANAGER runs the actual
mutation) or rejects. It is the governance-safe way for an agent that lacks
mutation authority to still influence the rules. Anyone may propose — the
proposal does NOT change the PRRD.

## Permission (this skill's matrix row)

| Op | MANAGER | ORCH | ARCH | INT | COS | MEMBER | AUTON | MAINT |
|---|---|---|---|---|---|---|---|---|
| **propose PRRD change** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ (via COS) | ✅ | ✅ |

Proposing is allowed for **every** role. Routing:

- **Team-internal agents** (ORCH / ARCH / INT / MEMBER) route the proposal
  through their **CHIEF-OF-STAFF** (R6 v3 — COS is the sole team entry point).
  Set `--routed-via <cos-session>`.
- **AUTONOMOUS / MAINTAINER** propose directly to MANAGER.
- **A GOLDEN-rule change** is USER-only: propose it (kind `golden`); the MANAGER
  escalates to the USER. No agent ever edits GOLDEN directly.

## Prerequisites

- The project has a `design/` tree (the PRRD at `design/requirements/PRRD.md` and
  a `design/requirements/proposals/` folder the proposal is written into).
  Bootstrap with `get-prrd.py --init` (or `bootstrap_design.py`) if absent.
- Python 3.10+ on PATH. The pillar scripts live at
  `${CLAUDE_PLUGIN_ROOT}/scripts/prrd-trdd/` and are resolved at runtime via
  `resolve_pillar_scripts.sh` (works from the core plugin OR any role plugin).
- You know your governance ROLE (MANAGER / ORCH / ARCH / INT / COS / MEMBER /
  AUTONOMOUS / MAINTAINER) — it decides your routing (team-internal agents file
  via their COS; AUTONOMOUS / MAINTAINER propose directly to MANAGER).

## Instructions

1. Resolve the pillar-scripts directory:

   ```bash
   DIR="$(sh "$CLAUDE_PLUGIN_ROOT/scripts/prrd-trdd/resolve_pillar_scripts.sh")" || exit 1
   ```

2. File the proposal (writes to `design/requirements/proposals/`, does NOT touch
   the PRRD):

   ```bash
   # Revise an existing SILVER rule (target its number):
   python3 "$DIR/prrd-edit.py" propose silver "new wording for rule 70" \
       --target 70 --proposed-by "$MY_SESSION" --routed-via cos-myteam

   # Propose a brand-new rule (no --target):
   python3 "$DIR/prrd-edit.py" propose silver "Every script MUST accept --help" \
       --proposed-by "$MY_SESSION" --routed-via cos-myteam

   # Propose a GOLDEN change (USER decides; MANAGER escalates):
   python3 "$DIR/prrd-edit.py" propose golden "<rule text>" \
       --proposed-by "$MY_SESSION" --routed-via cos-myteam
   ```

3. Tell the COS (or MANAGER) the proposal is filed; keep working — approval is
   asynchronous and never blocks your other work.

## Output

The path of the written proposal file on STDOUT; errors on STDERR; exit 0 on
success. The proposal is git-tracked under `design/requirements/proposals/`.

## Examples

<example>
A MEMBER thinks rule 12 should be reworded.
→ resolve DIR, `prrd-edit.py propose silver "<new wording>" --target 12 \
   --proposed-by member-frontend --routed-via cos-website`. The COS forwards to MANAGER.
</example>

<example>
AUTONOMOUS wants a new dependency-pinning rule.
→ `prrd-edit.py propose silver "Pin all third-party GitHub Actions to a SHA" \
   --proposed-by autonomous-1` (no COS — proposes directly to MANAGER).
</example>

## Scope

Writes a proposal ONLY — never mutates the PRRD. The MANAGER (SILVER) or USER
(GOLDEN) decides; on accept the MANAGER runs `ama-prrd-edit`. Reading is
`ama-prrd-get`; MANAGER direct SILVER mutation is `ama-prrd-edit`.

## Error Handling

On non-zero exit the message is on STDERR; the agent adjusts. Exit 2 = a
precondition failed (PRRD/TRDD missing — run the bootstrap / `--init`); exit 3 =
rule/TRDD not found (check the id/number). If `resolve_pillar_scripts.sh` exits
1, the ai-maestro-plugin base is not installed — set
`$AI_MAESTRO_PRRD_SCRIPTS_DIR` or install the base. This skill never mutates on
a partial failure.

## Resources

- `${CLAUDE_PLUGIN_ROOT}/rules/prrd-design-rules.md` — canonical PRRD format + the proposal queue.
- [../ama-trdd-transition/references/cos-delegation-authority.md](../ama-trdd-transition/references/cos-delegation-authority.md) — the COS two-tier filter (who escalates what).
  > The two-tier model · How escalation composes with presence (the full chain) · COS-AUTONOMOUS — the COS decides, no upstream · COS-ESCALATE — forward to MANAGER · Consolidation — the COS batches, it doesn't flood · The COS escalation message (to MANAGER) · User-presence — where it lives, and the janitor fallback · Why this exists · Relationship to exempt-operations.md
- `/ama-prrd-edit` — the MANAGER direct-mutation path (SILVER only).
- [../ama-trdd-transition/references/scripts-usage.md](../ama-trdd-transition/references/scripts-usage.md) — full script usage + exit codes.
  > resolve_pillar_scripts.sh — locate the scripts from any plugin (delivery mechanism) · get-prrd.py — read PRRD rules · prrd-edit.py — mutate the PRRD (MANAGER-only for direct mutation) · findprrd.py — search PRRD rules · findtrdd.py — find TRDDs · kanban.py — render the board (READ-ONLY) · bootstrap_design.py — create the 4-zone design/ folders · amama_proposal_approvals.py — batch proposal approvals (list/approve/refuse/archive) · Authoring a new TRDD (canonical skeleton) · Exit codes · Per-role quick examples
