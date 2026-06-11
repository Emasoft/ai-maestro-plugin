---
trdd-id: 9f10ed97-cd63-4160-adf4-48362f1015e2
title: Expand team-governance Examples section
column: backburner
created: 2026-05-08T00:00:00+0200
updated: 2026-06-11T11:35:00+0200
current-owner: null
task-type: docs
severity: HIGH
relevant-rules: []
---

# TRDD-9f10ed97-cd63-4160-adf4-48362f1015e2 — Expand team-governance Examples section

**Filename:** `design/tasks/TRDD-9f10ed97-cd63-4160-adf4-48362f1015e2-team-governance-examples-thin.md`
**Tracked in:** this repo (design/tasks/ is git-tracked)
**Source audit:** `reports/v258-pre-publish-audit/skill-content-audit.md` (A11.1)
**Severity:** HIGH (UX / discoverability)
**Status:** Not started
**Filed:** 2026-05-08

## Problem

`skills/team-governance/SKILL.md` Examples section (lines 86-88) is one
sentence:

```
## Examples
/team-governance create a closed team — see REFERENCE.md for full flows.
```

For a 4976-char SKILL.md (24 chars below the 5000-char CPV ceiling) this
returns very little discoverable signal to a user (or to an LLM that
loaded the skill via auto-trigger). Common operations should each have
a one-line worked curl example.

## Design

### Approach 1 — Reclaim chars elsewhere, expand inline

Tighten the existing 26-entry "Resources / Bundled Mirror TOC" (lines
113-139) to 5-8 top-level groupings (matches the recommendation in
`skill-content-audit.md` §A3.4 and §A11.6). The freed budget gives
~600-800 chars for examples.

Target Examples section (~400 chars):

```
## Examples

```bash
# List teams
curl -s "http://localhost:23000/api/governance/teams" | jq .

# Create a closed team with a chief-of-staff
curl -X POST "http://localhost:23000/api/governance/teams" \
  -H "Content-Type: application/json" \
  -d '{"name":"backend","type":"closed","chiefOfStaff":"alice"}'

# Broadcast to a team
amp-send "@team:backend" "Standup" "Daily 10am SLT"
```
```

### Approach 2 — Move examples to references/EXAMPLES.md

Add 1-line in SKILL.md: "See [worked examples](references/EXAMPLES.md)."
Move the bulk into a new reference file. Pro: SKILL.md stays compact
forever. Con: needs an extra file read for the LLM during auto-trigger,
and the audit prefers inline Examples for governance skills (governance
is the highest-stakes skill; examples should be visible at first load).

## Recommendation

**Approach 1** (inline, after compressing Resources TOC). Aligns with
audit recommendation A3.4/A11.6 to compress deep TOCs across the whole
plugin — kills two birds. Approach 2 is a fallback if compressing the
TOC turns out to break some other consumer of the SKILL file.

## Acceptance criteria

- [ ] team-governance/SKILL.md Examples section contains at least 3
  worked examples covering: list teams, create team with COS,
  broadcast to a team
- [ ] team-governance/SKILL.md remains within 5000-char CPV ceiling
- [ ] Resources / Bundled Mirror TOC compressed to 5-8 top-level entries
  (vs current 26)
- [ ] CPV strict still PASS (380+ checks, 0 issues)

## Dependencies

- None blocking. Loosely related to `skill-content-audit.md` §A3.4 and
  §A11.6 (deep-TOC compression) — same plugin-wide cleanup.

## Out of scope

- Adding a Examples section to every governance-tier SKILL.md (this
  TRDD covers team-governance only; sibling skills already have
  adequate examples)
- Cross-skill consistency rewrites (separate TRDD if desired)
