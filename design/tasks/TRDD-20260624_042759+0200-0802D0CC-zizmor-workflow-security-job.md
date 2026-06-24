---
trdd-id: 0802D0CC
title: Add a zizmor workflow-security job to ci.yml — CPV canon dropped it (core#13 landmine 1)
column: backburner
created: 2026-06-24T04:27:59+0200
updated: 2026-06-24T04:27:59+0200
current-owner: ai-maestro-plugin
assignee: ai-maestro-plugin
priority: 3
severity: MEDIUM
effort: S
task-type: security
labels: [ci, security, zizmor, fleet-readiness]
relevant-rules: []
release-via: publish
test-requirements: [lint]
review-requirements: []
impacts: [ci-pipeline]
external-refs: ["Emasoft/ai-maestro-plugin#13", "Emasoft/ai-maestro#44"]
---

# TRDD-0802D0CC — zizmor workflow-security job for ci.yml (core#13 landmine 1)

## Problem (verified)

core#13 (CPV-canonical-pipeline upgrade) lists as **landmine #1**: the canonical
CPV `ci.yml` template ships **no** zizmor step, so a plugin adopting canon loses
(or never gains) static GitHub-Actions security analysis. The MANAGER's #13
acceptance is explicit: *"re-add it as a `workflow-security` job (zizmor → SARIF
→ code-scanning)."*

Verified on this repo (2026-06-24): `git log -S 'zizmor' -- .github/workflows/`
is **empty** and `grep -c zizmor .github/workflows/ci.yml` = **0** — zizmor was
never in this plugin's tracked workflows, so this is an **add**, not a restore.
The current ci.yml does run `rhysd/actionlint` (workflow-syntax lint) but not
zizmor (security audit — template-injection, excessive permissions, unpinned
actions, etc.).

## Design (the exact job to add)

Add an advisory `workflow-security` job to `.github/workflows/ci.yml`:

```yaml
  workflow-security:
    name: Workflow security (zizmor)
    runs-on: ubuntu-latest
    timeout-minutes: 10
    permissions:
      contents: read
      security-events: write   # upload SARIF to the code-scanning tab
    steps:
      - uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10 # v6.0.3
      - uses: zizmorcore/zizmor-action@192e21d79ab29983730a13d1382995c2307fbcaa # v0.5.7
```

Verified facts for the implementation:
- `zizmorcore/zizmor-action` latest = **v0.5.7**, commit
  `192e21d79ab29983730a13d1382995c2307fbcaa` (SHA-pin per `gh-actions.md`:
  third-party actions outside `actions/`/`github/` pin to a full SHA).
- Reuse the SAME `actions/checkout` SHA the repo already pins (`df4cb1c…` v6.0.3)
  for consistency with the other jobs.
- **CONFIRM BEFORE WRITING** (not yet verified — the action.yml inputs grep came
  back empty): exactly how zizmor-action emits + uploads SARIF, and whether the
  SARIF upload is built-in (default) or needs `github/codeql-action/upload-sarif`
  as a second step. Read `zizmorcore/zizmor-action@v0.5.7` action.yml + README
  first; do NOT guess inputs.

## Why this is BACKBURNER (deferred, not done now)

1. **Not locally testable.** A GitHub-Actions job only really runs on push; the
   publish.py gates (G2 ruff / G3 CPV / G4 pytest) are local and do NOT exercise
   the workflow. Bundling an unverified new job into the current verified-green
   11-commit batch risks a red CI job on the release with no pre-merge signal.
   Better as a focused PR with its own CI feedback loop.
2. **Contracted canonical workflow.** ci.yml carries a required-context contract
   (`Lint`/`Validate`/`Test`, tied to `setup_branch_rules.DEFAULT_PLUGIN_CHECK_CONTEXTS`).
   The new job must be an **advisory** (non-required) context so it does not
   change that contract — verify it doesn't accidentally become a required check.
3. **#13 won't close on this alone.** #13 also requires posting the `from → to`
   row on `Emasoft/ai-maestro#44` and a MANAGER verify+tally (ai-maestro#44's
   latest tally still lists core among "Remaining 4 (no row yet)"). So the zizmor
   job is necessary-not-sufficient.

## Acceptance criteria

- [ ] `zizmorcore/zizmor-action@v0.5.7` action.yml + README read; SARIF/upload
      behavior confirmed (built-in vs needs a codeql upload-sarif step)
- [ ] `workflow-security` job added to ci.yml, SHA-pinned, `security-events: write`
- [ ] Job is ADVISORY — does NOT alter the required `Lint`/`Validate`/`Test` contexts
- [ ] Mirror into release.yml only if CI/Release parity requires it (it likely does
      NOT — security scan belongs to CI, not the release path); decide explicitly
- [ ] Pushed on a branch via publish.py; CI run watched green; SARIF appears in
      the code-scanning tab (or the advisory job passes)
- [ ] Post the `from → to` row on `Emasoft/ai-maestro#44` + request MANAGER tally
- [ ] Close core#13 on the MANAGER tally

## Coordination

- MANAGER pre-authorized the zizmor job via core#13 landmine #1 — no separate
  proposal needed; this TRDD documents the plan.
- The SBOM/provenance landmine (#13 landmine #4) is explicitly defer-able per the
  issue ("does not block acceptance") — out of scope here.
