---
prrd-version: 1.5
updated: "2026-06-11T11:29:10+0200"
project: ai-maestro-plugin
project-id: ai-maestro-plugin
canonical-source: design/requirements/PRRD.md
mirrors: []
---

# Project Requirements & Rules — ai-maestro-plugin

Umbrella core plugin — shared skills, AMP messaging, governance, kanban, and the PRRD/TRDD/Kanban universal workflow.

## §0. Canonical source + copies

| Path | Role | Update strategy |
|---|---|---|
| `design/requirements/PRRD.md` | **CANONICAL** for this project | Edit first. Bump `prrd-version:`. Update `updated:`. |

## §I. How to read this document

Rule citation form: `PRRD G<n>.<v>` (golden, user-set) or `PRRD S<n>.<v>`
(silver, manager-mutable). Rule numbers are globally unique across G/S;
promote/demote flips the letter without changing the number. The
`get-prrd.py <n>` script returns a rule's text by bare number. Full
spec: `~/.claude/rules/prrd-design-rules.md`.

## 🥇 GOLDEN — set by the USER (immutable to MANAGER)

- **G1.1** — Every agent that writes to GitHub (issue, issue comment, PR, PR comment, PR review, discussion, release note) MUST begin the body with a one-line self-identification of which agent/role/plugin authored it, because all AI Maestro agents share the single human-owner GitHub identity (the owner's gh CLI auth). Recommended leading line: _Posted by the Claude developing **<plugin-or-role>** (via the shared @owner gh auth)._ Commit messages SHOULD carry an `Agent: <role>` trailer.

## 🥈 SILVER — MANAGER-mutable (agents propose via COS)

- **S2.1** — Every skill, command, and hook ships real (no-mock) tests, and the bundled test runner exits 0 on all-pass and non-zero on any failure
- **S3.1** — Bundled governance and rules references are MIRRORS of their canonical sources (the team-governance GOVERNANCE-RULES doc and the user-level ~/.claude/rules); when a canonical source changes, the bundled copy is re-synced in the same release
- **S4.1** — The PRRD/TRDD/Kanban pillar scripts are Python-stdlib-only (no third-party runtime dependency) so they run wherever Python 3.10+ is present
- **S5.1** — A role plugin reaches the base pillar scripts through resolve_pillar_scripts.sh (or the AI_MAESTRO_PRRD_SCRIPTS_DIR override), never a hard-coded plugin-cache path
- **S6.1** — The README skill/command/script counts and the Built-at date reflect the actual repository tree at publish time

