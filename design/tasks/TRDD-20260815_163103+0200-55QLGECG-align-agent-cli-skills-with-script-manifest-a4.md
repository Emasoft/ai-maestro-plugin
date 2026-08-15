---
trdd-id: 55QLGECG
title: align agent-CLI skills with SCRIPT-MANIFEST f97d3e23 (A4 delivery — self literal, deployment contract, exit trichotomy)
column: complete
created: 2026-08-15T16:31:03+0200
updated: 2026-08-15T16:31:03+0200
current-owner: ai-maestro-plugin-session
task-type: docs
priority: normal
external-refs: [ai-maestro#116]
npt: []
eht: []
---

# Align agent-CLI skills with SCRIPT-MANIFEST.md (A4)

**Trigger:** hub (ai-maestro-a7) A4 delivery, hub card `TRDD-1ZMEXD9X` — the manifest at
`~/ai-maestro/docs/SCRIPT-MANIFEST.md` (fork tip `f97d3e23`) is the authoritative contract
for plugin-shipped skills. Delivery record: the hub's cross-session message of 2026-08-15.

## Verification (first-hand, per verify-cross-repo-cited-sha lesson)

- `f97d3e23` is a real commit and IS the fork tip; the file exists (44KB).
- `self`/`<self>` literal verified in CODE: `scripts/shell-helpers/common.sh:337` →
  `GET /api/agents/me` via `get_auth_args` (TRDD-COOLOZ1N ruling 2). Note: the manifest's
  §agent-lifecycle does not yet call the literal out (only continuity's `<self>` rows) —
  the code is the evidence.
- Exit trichotomy (0 clean · 1 findings · 2 could-not-run; `tool || fallback` always a bug):
  manifest §Pillar/governance tooling. CORE's `ama-trdd-find` ALREADY teaches it verbatim —
  no change needed there.
- `prrdgrep`/`specgrep` are `.mjs` run inside the server repo (yarn / `node --import tsx`),
  NOT installed to `~/.local/bin` — deliberately NOT added to CORE's PRRD skills, which
  drive the python pillar scripts on agent hosts.

## Changes landed

- `skills/ai-maestro-agents-management/SKILL.md` step 2: `self`/`<self>` literal contract +
  manifest named as the frozen verb/flag contract (never `~/.local/bin` residue, R23.7).
- `skills/ai-maestro-agents-management/references/REFERENCE.md` (hibernation §): the #116
  partial answer — deployment = repo → `~/.local/bin` via `install-agent-cli.sh`,
  `INSTALLED_FILES` = shipping list, manifest = citable contract.

## Approval log

- 2026-08-15T16:31:03+0200 — Tier 0 (docs, own scope, additive). Authored directly as
  planned/dev and completed same session; suite green.
