---
name: ama-prrd-get
description: "Read a PRRD rule by number from a project's design/requirements/PRRD.md. Use when an agent needs the exact text of a project rule it must comply with, wants to cite a rule (PRRD G64.134), list all rules, or bootstrap an empty PRRD. Reading is allowed for EVERY role. Trigger with /ama-prrd-get or 'what does PRRD rule N say', 'cite rule N', 'list the project rules', 'show the PRRD'. The READ pillar of the AI-Maestro PRRD; for searching by content use /ama-prrd-find, to mutate use /ama-prrd-edit (gated) or /ama-prrd-propose."
allowed-tools: "Bash(python3:*), Bash(sh:*), Bash(get-prrd.py:*), Bash(resolve_pillar_scripts.sh:*), Read, Grep, Glob"
metadata:
  author: "Emasoft"
  version: "1.0.0"
---

# ama-prrd-get — read a PRRD rule

## Overview

`ama-prrd-get` reads the project's authoritative rules document
(`design/requirements/PRRD.md`) — one rule by number, a formatted citation, or
the whole list. This is the READ half of the PRRD pillar; it never mutates.

## Permission (this skill's matrix row)

| Op | MANAGER | ORCH | ARCH | INT | COS | MEMBER | AUTON | MAINT |
|---|---|---|---|---|---|---|---|---|
| **read PRRD** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

Reading is allowed for **every** role — no gate, no approval. (Mutation is the
gated op; see `ama-prrd-edit` / `ama-prrd-propose`.)

## Prerequisites

- The project has a `design/` tree with a PRRD at `design/requirements/PRRD.md`
  to read from. Bootstrap with `get-prrd.py --init` (or `bootstrap_design.py`)
  if absent.
- Python 3.10+ on PATH. The pillar scripts live at
  `${CLAUDE_PLUGIN_ROOT}/scripts/prrd-trdd/` and are resolved at runtime via
  `resolve_pillar_scripts.sh` (works from the core plugin OR any role plugin).
- You know your governance ROLE (MANAGER / ORCH / ARCH / INT / COS / MEMBER /
  AUTONOMOUS / MAINTAINER) — this skill's permission matrix is keyed on it.

## Instructions

1. Resolve the pillar-scripts directory (works from the core plugin OR any role
   plugin — see the delivery reference):

   ```bash
   DIR="$(sh "$CLAUDE_PLUGIN_ROOT/scripts/prrd-trdd/resolve_pillar_scripts.sh")" || exit 1
   ```

2. Read the rule(s):

   ```bash
   python3 "$DIR/get-prrd.py" 70            # latest version of rule 70
   python3 "$DIR/get-prrd.py" 70.3          # a specific version
   python3 "$DIR/get-prrd.py" --cite 70.3   # "PRRD G70.3 — <text>" (G/S annotation)
   python3 "$DIR/get-prrd.py" --list                  # every rule, one per line
   python3 "$DIR/get-prrd.py" --list --kind silver    # only SILVER rules
   python3 "$DIR/get-prrd.py" --json 70.3   # JSON: {number, version, kind, text}
   python3 "$DIR/get-prrd.py" --init        # create an empty PRRD (no rules yet)
   ```

   The letter (G/S) in a reference is IGNORED on input — rules are identified by
   NUMBER alone; the letter is for the human reader. A pinned `70.3` is the rule
   as it existed at version 3; a bare `70` follows the latest version.

## Output

The rule text (or citation / JSON / list) on STDOUT; errors on STDERR; exit 0 on
success. Exit 3 = rule not found; exit 2 = PRRD file missing (run `--init`).

## Examples

<example>
User: what does PRRD rule 64 require?
→ resolve DIR, then `get-prrd.py 64` → prints rule 64's current text.
</example>

<example>
User: cite the credential rule in my TRDD
→ `get-prrd.py --cite 64.134` → "PRRD G64.134 — <text>", paste into the TRDD's body.
</example>

<example>
User: list all the golden rules
→ `get-prrd.py --list --kind golden`
</example>

## Scope

READ-ONLY. Never edits the PRRD. To change a rule: `ama-prrd-edit` (MANAGER, SILVER)
or `ama-prrd-propose` (anyone). To search rules by content: `ama-prrd-find`.

## Error Handling

On non-zero exit the message is on STDERR; the agent adjusts. Exit 2 = a
precondition failed (PRRD/TRDD missing — run the bootstrap / `--init`); exit 3 =
rule/TRDD not found (check the id/number). If `resolve_pillar_scripts.sh` exits
1, the ai-maestro-plugin base is not installed — set
`$AI_MAESTRO_PRRD_SCRIPTS_DIR` or install the base. This skill never mutates on
a partial failure.

## Resources

- `${CLAUDE_PLUGIN_ROOT}/rules/prrd-design-rules.md` — the canonical PRRD format,
  citation grammar, GOLDEN/SILVER split (auto-installed to `~/.claude/rules/` each session).
- [../ama-trdd-transition/references/scripts-usage.md](../ama-trdd-transition/references/scripts-usage.md)
  — full script usage + exit-code table + the cross-plugin resolver.
  > resolve_pillar_scripts.sh — locate the scripts from any plugin (delivery mechanism) · get-prrd.py — read PRRD rules · prrd-edit.py — mutate the PRRD (MANAGER-only for direct mutation) · findprrd.py — search PRRD rules · findtrdd.py — find TRDDs · kanban.py — render the board (READ-ONLY) · bootstrap_design.py — create the 4-zone design/ folders · amama_proposal_approvals.py — batch proposal approvals (list/approve/refuse/archive) · Authoring a new TRDD (canonical skeleton) · Exit codes · Per-role quick examples
