---
name: ama-prrd-find
description: "Search a project's PRRD rules by content or metadata — find rules whose text matches a keyword, list all GOLDEN or SILVER rules, find which rules a TRDD cites, find unused rules, or get rule-count stats. Use when an agent asks 'which rule covers X', 'are there rules about credentials/auth/deploys', 'what rules does this TRDD reference', 'which rules are never cited'. Searching is allowed for EVERY role. Trigger with /ama-prrd-find. The SEARCH pillar of the AI-Maestro PRRD; to read one rule by number use /ama-prrd-get, to mutate use /ama-prrd-edit (gated) or /ama-prrd-propose."
allowed-tools: "Bash(python3:*), Bash(sh:*), Bash(findprrd.py:*), Bash(resolve_pillar_scripts.sh:*), Read, Grep, Glob"
metadata:
  author: "Emasoft"
  version: "1.0.0"
---

# ama-prrd-find — search PRRD rules

## Overview

`ama-prrd-find` searches the project's PRRD by content or metadata: by keyword,
by kind (golden/silver), by citation (which TRDDs reference a rule), or to find
rules never cited. It is READ-ONLY — it never mutates the PRRD.

## Permission (this skill's matrix row)

| Op | MANAGER | ORCH | ARCH | INT | COS | MEMBER | AUTON | MAINT |
|---|---|---|---|---|---|---|---|---|
| **search PRRD** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

Searching is allowed for **every** role — no gate, no approval.

## Prerequisites

- The project has a `design/` tree with a PRRD at `design/requirements/PRRD.md`
  to search (and `design/tasks/` TRDDs for `--cited-in` / `--unused`). Bootstrap
  with `get-prrd.py --init` (or `bootstrap_design.py`) if absent.
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

2. Search:

   ```bash
   python3 "$DIR/findprrd.py" --kind golden          # all GOLDEN rules
   python3 "$DIR/findprrd.py" --kind silver          # all SILVER rules
   python3 "$DIR/findprrd.py" --grep "credentials"   # rules whose text matches
   python3 "$DIR/findprrd.py" --cited-in design/tasks/   # rules any TRDD cites
   python3 "$DIR/findprrd.py" --unused               # rules NOT cited by any TRDD
   python3 "$DIR/findprrd.py" --count                # summary stats
   ```

## Output

Matching rules / counts on STDOUT; errors on STDERR; exit 0 on success.

## Examples

<example>
User: is there a project rule about API authentication?
→ resolve DIR, then `findprrd.py --grep "auth"` → lists matching rules; read one with /ama-prrd-get.
</example>

<example>
User: which rules does nobody cite anymore?
→ `findprrd.py --unused` → candidates for review/cleanup (propose changes via /ama-prrd-propose).
</example>

## Scope

READ-ONLY. To read one rule's full text: `ama-prrd-get`. To change a rule:
`ama-prrd-edit` (gated) or `ama-prrd-propose`.

## Error Handling

On non-zero exit the message is on STDERR; the agent adjusts. Exit 2 = a
precondition failed (PRRD/TRDD missing — run the bootstrap / `--init`); exit 3 =
rule/TRDD not found (check the id/number). If `resolve_pillar_scripts.sh` exits
1, the ai-maestro-plugin base is not installed — set
`$AI_MAESTRO_PRRD_SCRIPTS_DIR` or install the base. This skill never mutates on
a partial failure.

## Resources

- `${CLAUDE_PLUGIN_ROOT}/rules/prrd-design-rules.md` — canonical PRRD format + citation grammar.
- [../ama-trdd-transition/references/scripts-usage.md](../ama-trdd-transition/references/scripts-usage.md)
  — full script usage + exit codes.
  > resolve_pillar_scripts.sh — locate the scripts from any plugin (delivery mechanism) · get-prrd.py — read PRRD rules · prrd-edit.py — mutate the PRRD (MANAGER-only for direct mutation) · findprrd.py — search PRRD rules · findtrdd.py — find TRDDs · kanban.py — render the board (READ-ONLY) · bootstrap_design.py — create the 4-zone design/ folders · amama_proposal_approvals.py — batch proposal approvals (list/approve/refuse/archive) · Authoring a new TRDD (canonical skeleton) · Exit codes · Per-role quick examples
