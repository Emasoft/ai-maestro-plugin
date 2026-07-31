---
trdd-id: 0d9453a9-aa39-488b-a404-ccea7fa005fc
title: Fleet-readiness governance gaps — close M1-M13 audit findings (GH issue #5)
column: published
created: 2026-06-11T11:15:04+0200
updated: 2026-06-11T12:10:00+0200
current-owner: ai-maestro-plugin
assignee: ai-maestro-plugin
priority: 1
severity: HIGH
effort: XL
labels: [governance, docs, audit]
task-type: feature
parent-trdd: null
relevant-rules: [1]
release-via: publish
delivery: direct-push
target-branch: main
test-requirements: [unit, lint]
review-requirements: [human-review]
runtime-targets: [macos, linux]
impacts: [public-api]
published-version: 2.7.0
published-at: 2026-06-11T12:08:00+0200
implementation-commits: [93373fd, d67370c, 3db0ef0, 5f96859, d6ab99d, 2a58501]
external-refs: ["github.com/Emasoft/ai-maestro-plugin/issues/5"]
---

# TRDD-0d9453a9 — Fleet-readiness governance gaps (GH issue #5)

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative; supersedes the body) — 2026-06-11

**DONE — published as v2.7.0** (release: https://github.com/Emasoft/ai-maestro-plugin/releases/tag/v2.7.0).
All M1-M13 ✗/PARTIAL findings addressed; CPV `--strict` exits 0 (0 blocking,
12 advisory WARNINGs); 93 tests pass. CI runs for 2a58501 being monitored to green.
**Remaining:** reply on issue #5 with the per-finding resolution + published version
(once CI confirmed green). Cosmetic carry-forward: local commit 84a56b7 syncs
uv.lock editable→2.7.0, lands on next publish (pre-push hook needs publish.py ancestry).

**Source work order:** GitHub issue #5 (MANAGER fleet-readiness audit). The user
explicitly authorized "read the github issues and implement/fix all pending."

**Verified state of the repo (2026-06-11, all audit claims re-checked against files):**
- M7 ✗ CRITICAL — ZERO dialog loops in `skills/prrd-trdd-kanban/`. CONFIRMED.
- M3 — 4-zone folder model (proposals/tasks/refused/archived) absent from all
  bundled refs; the 7 TRDDs in `design/tasks/` are PRE-frontmatter (markdown-bold
  `**Status:**` keys, no YAML `column:`). CONFIRMED.
- M5 — `approval-tier:` field + `proposal` column + Tier 0/1/2/3 ladder absent.
  `exempt-operations.md` has EXEMPT/NON-EXEMPT only. CONFIRMED.
- M1 — `amama_proposal_approvals.py` ABSENT from `scripts/prrd-trdd/`; no
  cross-plugin script-delivery mechanism documented. CONFIRMED.
- M2 — `design/requirements/PRRD.md` has no `project-id:`; SILVER section empty.
  CONFIRMED.
- M4 — no anti-split-brain rule reconciling team-kanban vs prrd-trdd-kanban.
- M10 — agent-messaging SKILL has "Priority Levels" but no inbox-first STOP rule
  and no self-id line in the AMP body template.
- M11 — README says "Skills: 11" (actual 15), table lists 13, dated 2026-03-30;
  stale feature-branch GOVERNANCE-RULES URL at
  `skills/team-governance/references/GOVERNANCE-RULES.md:47`.
- M9 — single-writer-per-domain not codified (`current-owner:` write-lock exists).
- M6 ✓, M8 ✓, M13 ✓ — no action.

**NEXT ACTION:** execute the phase plan below in order. Author core governance
content inline (consistency-critical); delegate mechanical TRDD migration + tests
to agents. All git handled by orchestrator only.

**Load-bearing facts:**
- Canonical source rules already in session context: `~/.claude/rules/trdd-approval-tiers.md`
  (4-zone + tier ladder + approval-tier + proposal column + watchdog), `manager-approval-defaults.md`,
  `trdd-design-tasks.md`, `prrd-design-rules.md`. Distill, don't reinvent.
- Pre-push hook routes every push through `scripts/publish.py` (never bypass).
- Version currently 2.6.1; publish.py auto-bumps via conventional commits.

## Phase plan

1. **Core governance refs (M7, M3, M5, M9)** — NEW `dialog-loops.md`,
   NEW `approval-tiers-and-zones.md`; edit `trdd-design-tasks.md` (column enum +
   zones), `trdd-frontmatter-schema.md` (approval-tier + single-writer),
   `column-transitions.md` (INT-owns-completed + pre-PR gate), `SKILL.md` (pointers).
2. **Scripts + delivery (M1)** — NEW `amama_proposal_approvals.py`,
   NEW design-zone bootstrap helper, cross-plugin delivery doc + plugin.json note.
3. **PRRD + single-board + AMP + README (M2, M4, M10, M11)**.
4. **Migrate 7 v1 TRDDs to v2 `column:`** (M3) — delegated, mechanical.
5. **Tests for pillar scripts + runner (M12)** — delegated.
6. **Validate (CPV), version bump, publish, reply on issue #5.**

## Acceptance criteria (from issue #5)
Every ✗/PARTIAL addressed or justified in a reply; no legacy doc versions kept;
real tests (no mocks); version bumped + published; reply with the published version.
