---
trdd-id: 2FIE5SFU
title: plugin.json description advertises code graph and docs search which no longer ship
column: ai_review
created: 2026-08-18T19:52:30+0200
updated: 2026-08-18T19:58:00+0200
current-owner: ai-maestro-plugin-session
task-type: docs
priority: normal
approval-tier: 0
labels: [phase2, plugin-self-audit]
---

# Drop "code graph" and "docs search" from the marketplace description

Phase-2 card for Phase-1 audit finding 1 (BRRJK57P program; evidence in
`reports/plugin-self-audit/20260816_165645+0200-axis1-missing-features.md`).

`.claude-plugin/plugin.json`'s `description` — the string every user reads in the
marketplace listing BEFORE installing — still advertises "code graph" and "docs search".
Both skills were removed (the plugin's own
`skills/memory-search/references/REFERENCE.md:159` documents the removal); 30 skill dirs
exist, 0 match either name. The skills array entry was deleted in commit `2057f12` but the
human-facing description was never edited.

## Fix

Remove ", code graph, docs search" from the `description` string. Nothing else changes.
Sweep for the same stale phrases in README.md and any skill prose while at it
(`check-all-files-after-breaking-change` rule).

## Acceptance

- [x] `plugin.json` description no longer names a capability absent from `skills/`
      (verified: `json.load` parses; description reads "…memory search, task planning,…";
      the stale `graph` keyword dropped too).
- [x] Repo-wide grep for "code graph" / "docs search" over `.claude-plugin/ README.md
      skills/ commands/` returns only REFERENCE.md:159's removal note. Targeted tests:
      96 passed.
