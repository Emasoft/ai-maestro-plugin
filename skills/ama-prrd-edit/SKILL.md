---
name: ama-prrd-edit
description: "Mutate a project's PRRD rules — add/revise/delete a SILVER rule, or promote/demote between SILVER and GOLDEN. GATED: direct mutation is MANAGER-only (enforced by the script's AID_AUTH check); GOLDEN edits and promote/demote are USER-only; a non-MANAGER agent routes to /ama-prrd-propose instead. Use when a MANAGER (or solo USER) decides to change a SILVER rule. Trigger with /ama-prrd-edit, 'add/revise/delete a project rule', or 'promote rule N to golden'. The WRITE pillar of the AI-Maestro PRRD; proposing is /ama-prrd-propose, reading is /ama-prrd-get."
allowed-tools: "Bash(python3:*), Bash(sh:*), Bash(prrd-edit.py:*), Bash(resolve_pillar_scripts.sh:*), Read, Grep, Glob"
metadata:
  author: "Emasoft"
  version: "1.0.0"
---

# ama-prrd-edit — mutate the PRRD (GATED)

## Overview

`ama-prrd-edit` changes the project's authoritative rules: add / revise / delete
a SILVER rule, or promote/demote a rule between SILVER and GOLDEN. It is the most
governance-sensitive pillar operation, so it is **double-gated** — by your role
(self-check below) AND by the script's hard `caller_is_manager()` authority
check.

## Permission (this skill's matrix row) — SELF-CHECK BEFORE RUNNING

| Op | MANAGER | ORCH | ARCH | INT | COS | MEMBER | AUTON | MAINT |
|---|---|---|---|---|---|---|---|---|
| **edit SILVER PRRD** | ✅ direct | propose | propose | propose | relay | propose-via-COS | propose | propose |
| **edit GOLDEN PRRD** | ❌ USER-only | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

**The routing rule (do this BEFORE invoking the script):**

- **You are MANAGER (or the solo USER)** → you may directly `add/revise/delete`
  a SILVER rule. Use `--user` only when working solo without an AI Maestro server.
- **You are ANY other role and want to change a SILVER rule** → STOP. Do NOT run
  this skill. Instead invoke **`ama-prrd-propose`** to file a proposal (team-internal
  agents route via their COS). The change happens only after the MANAGER approves.
- **The rule is GOLDEN (or you want promote/demote)** → this is **USER-only**.
  No agent — not even MANAGER — may do it. File an `ama-prrd-propose` proposal and
  the MANAGER escalates to the USER.

The two-layer guarantee: even if a non-MANAGER agent ignores the routing rule and
invokes the script anyway, the script's `prrd_lib.caller_is_manager()` check
(reads `$AID_AUTH` against the AI Maestro server) **refuses** the mutation with
exit 4 unless the caller is a verified MANAGER or passes `--user`. Governance
cannot be bypassed by calling the skill directly.

## Prerequisites

- The project has a `design/` tree with a PRRD at `design/requirements/PRRD.md`
  to mutate. Bootstrap with `get-prrd.py --init` (or `bootstrap_design.py`) if
  absent.
- Python 3.10+ on PATH. The pillar scripts live at
  `${CLAUDE_PLUGIN_ROOT}/scripts/prrd-trdd/` and are resolved at runtime via
  `resolve_pillar_scripts.sh` (works from the core plugin OR any role plugin).
- You know your governance ROLE (MANAGER / ORCH / ARCH / INT / COS / MEMBER /
  AUTONOMOUS / MAINTAINER) — this skill's permission matrix is keyed on it, and
  direct mutation requires the MANAGER role (or the solo USER via `--user`).

## Instructions

1. Resolve the pillar-scripts directory:

   ```bash
   DIR="$(sh "$CLAUDE_PLUGIN_ROOT/scripts/prrd-trdd/resolve_pillar_scripts.sh")" || exit 1
   ```

2. Mutate (MANAGER, SILVER only — or solo USER with `--user`):

   ```bash
   python3 "$DIR/prrd-edit.py" add silver "Use AID auth for all API calls"   # next free number, v1
   python3 "$DIR/prrd-edit.py" revise 70 "new rule text"                     # bumps S70.3 -> S70.4
   python3 "$DIR/prrd-edit.py" delete 70                                     # number retires forever
   ```

3. USER-only (will refuse for any agent; only the human runs these, with `--user`):

   ```bash
   python3 "$DIR/prrd-edit.py" --user promote 70    # SILVER -> GOLDEN
   python3 "$DIR/prrd-edit.py" --user demote 70     # GOLDEN -> SILVER
   ```

4. If the script exits 4 (authority refused), that is the gate working — switch
   to `ama-prrd-propose` instead of retrying.

## Output

The mutation summary on STDOUT (e.g. "Rule 70 revised: S70.3 → S70.4"); errors on
STDERR. Exit 4 = authority refused (use `ama-prrd-propose`). A successful mutation
bumps the PRRD's `prrd-version:` and `updated:`.

## Examples

<example>
User (acting as MANAGER): add a silver rule that all scripts must accept --help
→ resolve DIR, `prrd-edit.py add silver "Every script MUST accept --help"`.
</example>

<example>
A MEMBER agent wants rule 12 reworded.
→ DO NOT run ama-prrd-edit. Run /ama-prrd-propose silver "<new wording>" --target 12,
  routed via the team COS; the MANAGER approves it.
</example>

## Scope

Mutates SILVER PRRD rules (MANAGER) or, for the USER only, promotes/demotes. Never
touches GOLDEN content for any agent. Non-MANAGER role → use `ama-prrd-propose`.
Reading is `ama-prrd-get`.

## Error Handling

On non-zero exit the message is on STDERR. **Exit 4 = authority refused** — the
script's `caller_is_manager()` gate rejected a non-MANAGER mutation; this is the
gate working as designed. Do NOT retry with `--user` unless you ARE the solo
USER; instead route per the permission matrix (propose / escalate). Exit 2 = a
precondition failed (PRRD/TRDD missing — bootstrap first); exit 3 = not found.
If `resolve_pillar_scripts.sh` exits 1, the ai-maestro-plugin base is not
installed — set `$AI_MAESTRO_PRRD_SCRIPTS_DIR` or install the base.

## Resources

- `${CLAUDE_PLUGIN_ROOT}/rules/prrd-design-rules.md` — canonical PRRD format, mutation-authority table, GOLDEN/SILVER.
- [../ama-trdd-transition/references/prrd-design-rules.md](../ama-trdd-transition/references/prrd-design-rules.md) — the one fact every ama-prrd-* skill enforces (pointer).
  > Why this is a pointer, not a copy · The one fact every `ama-prrd-*` skill enforces
- `/ama-prrd-propose` — the proposal path for every non-MANAGER (and for GOLDEN changes).
- [../ama-trdd-transition/references/scripts-usage.md](../ama-trdd-transition/references/scripts-usage.md) — full script usage + exit codes.
  > resolve_pillar_scripts.sh — locate the scripts from any plugin (delivery mechanism) · get-prrd.py — read PRRD rules · prrd-edit.py — mutate the PRRD (MANAGER-only for direct mutation) · findprrd.py — search PRRD rules · findtrdd.py — find TRDDs · kanban.py — render the board (READ-ONLY) · bootstrap_design.py — create the 4-zone design/ folders · amama_proposal_approvals.py — batch proposal approvals (list/approve/refuse/archive) · Authoring a new TRDD (canonical skeleton) · Exit codes · Per-role quick examples
