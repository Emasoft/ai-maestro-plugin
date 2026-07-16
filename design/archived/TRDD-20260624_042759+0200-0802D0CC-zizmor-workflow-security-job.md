---
trdd-id: 0802D0CC
title: Add a zizmor workflow-security job to ci.yml — CPV canon dropped it (core#13 landmine 1)
column: dev
created: 2026-06-24T04:27:59+0200
updated: 2026-07-15T10:04:48+0200
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

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative; supersedes the body) — 2026-07-15

**Unparked from `backburner` → `dev` while executing core#13's CPV canonical-pipeline
upgrade (branch `fix/open-issues-sweep`). Implementation is DONE in the working tree and
LOCALLY VERIFIED green; it is NOT yet committed/pushed (this session had no push/publish
authorization).**

- **Job added.** `.github/workflows/ci.yml` now carries an advisory `workflow-security`
  job (name "Workflow security (zizmor)") — SHA-pinned `actions/checkout@df4cb1c… v6.0.3`
  + `zizmorcore/zizmor-action@192e21d… v0.5.7`, `contents: read` + `security-events: write`,
  `timeout-minutes: 10`, `persist-credentials: false`. It is NON-required (its own name),
  so the `Lint`/`Validate`/`Test` required-context contract is unchanged.
- **All 11 findings FIXED** (were 5 HIGH + 6 MEDIUM, zizmor exit 14; now `zizmor --offline
  --persona regular` = 0 findings, exit 0; `actionlint` clean):
  - `unpinned-uses` ×3 → SHA-pinned: release.yml checkouts `@v4`→`@df4cb1c… v6.0.3` (aligned
    to ci.yml), and `actions/attest-build-provenance@v4`→`@0f67c3f4856b2e3261c31976d6725780e5e4c373 # v4.1.1`.
  - `artipacked` ×6 → `persist-credentials: false` on all 4 ci.yml checkouts + BOTH release.yml
    checkouts. VERIFIED both release jobs publish via `gh`/`GH_TOKEN` and never `git push`, so
    dropping the persisted token is safe (resolves the TRDD's "verify before touching" caveat).
  - `cache-poisoning` ×2 (release.yml setup-uv + actions/cache) → JUSTIFIED
    `# zizmor: ignore[cache-poisoning]` (NOT a blanket suppress): release fires only on an
    owner `v*.*.*` tag push — no fork-PR writer path — and the CPV cache is required (#114
    cold-timeout). Matches the TRDD's cache-poisoning decision exactly.

**NEXT ACTION (needs the orchestrator's commit + push authorization):** commit these changes,
`publish.py` (or push a branch), watch the CI `Workflow security (zizmor)` job go green, confirm
SARIF lands in the code-scanning tab, then post the `from → to` row on `Emasoft/ai-maestro#44`
and close core#13. Nothing further is locally verifiable.

**Load-bearing facts:** SARIF upload + the action's fail-on-findings behavior are the ONLY
parts not locally checkable (they need a real CI run). Everything else is verified green.

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

- [x] `zizmorcore/zizmor-action@v0.5.7` action.yml + README read; SARIF/upload
      behavior confirmed (`advanced-security: true` default → SARIF to the security tab;
      no separate codeql upload-sarif step needed)
- [x] `workflow-security` job added to ci.yml, SHA-pinned, `security-events: write`
- [x] Job is ADVISORY — does NOT alter the required `Lint`/`Validate`/`Test` contexts
      (distinct job name "Workflow security (zizmor)")
- [x] Decided: do NOT mirror into release.yml — the security scan belongs to CI, not the
      release path; release.yml's own findings were fixed but no zizmor job was added there
- [ ] Pushed on a branch via publish.py; CI run watched green; SARIF appears in
      the code-scanning tab (or the advisory job passes) — BLOCKED this session (no push auth)
- [ ] Post the `from → to` row on `Emasoft/ai-maestro#44` + request MANAGER tally
- [ ] Close core#13 on the MANAGER tally

## Coordination

- MANAGER pre-authorized the zizmor job via core#13 landmine #1 — no separate
  proposal needed; this TRDD documents the plan.
- The SBOM/provenance landmine (#13 landmine #4) is explicitly defer-able per the
  issue ("does not block acceptance") — out of scope here.

## Zizmor scan findings (run LOCALLY 2026-06-24 — `zizmor 1.25.2 --offline --persona regular`)

Both `zizmor` AND `actionlint` are installed locally (`/opt/homebrew/bin`), so the
implementer CAN pre-validate to green before any push. Confirmed the action's real
contract from `zizmorcore/zizmor-action@v0.5.7` action.yml: `advanced-security: true`
is the DEFAULT (SARIF → repo security tab, needs `security-events: write`); the
recommended job = `actions/checkout` + `zizmorcore/zizmor-action@<sha>`, no extra inputs.

**The scan of the EXISTING workflows is NOT clean — 22 findings, 11 non-suppressed
(5 HIGH + 6 MEDIUM), zizmor exit 14.** So a bare "add the job" would ship a permanently
RED advisory check. The real work is fixing the findings; each needs a deliberate
decision (NOT a blanket auto-fix):

| Rule (sev) | Locations | Decision |
|---|---|---|
| `unpinned-uses` (HIGH ×3) | release.yml:15 + :202 `actions/checkout@v4`, :244 `actions/attest-build-provenance@v4` | **FIX (safe): SHA-pin.** Note release.yml's checkout is an OUTDATED `@v4` vs ci.yml's pinned `@df4cb1c… v6.0.3` — align them. Release-path change → CI-verify on push. |
| `artipacked` (MED ×6) | ci.yml:39/81/102/195 + release.yml:15/202 (checkout `persist-credentials` defaults true) | **FIX the CI checkouts** (`persist-credentials: false` — Lint/Validate/Test never push). **release.yml's checkout MAY need creds** (its job tags/pushes/releases) → verify before touching; do NOT blanket-apply. |
| `cache-poisoning` (MED ×2, Low-confidence) | release.yml:28 `setup-uv enable-cache`, :46 `actions/cache` | **CONFLICT — do NOT blindly remove.** release.yml NEEDS that `~/.cache/cpv` cache to avoid the CPV cold-install timeout (memory `ci-cpv-validate-step-stall`; CPV ≤2.126 cold build 12-20 min). Resolve with a SCOPED mitigation (read-only / tightly-keyed cache) or a JUSTIFIED `# zizmor: ignore[cache-poisoning]` — never a security-relaxing blanket suppress. |

**Refined plan (supersedes the simple "add the job" framing above):** the JOB itself is
trivial; the FINDINGS fixes are the substance, and they touch the RELEASE path + collide
with a known fix — so they MUST be done deliberately and CI-verified. Run `zizmor` locally
to confirm green BEFORE pushing; the only parts NOT locally checkable are the SARIF→
code-scanning upload and the action's fail-on-findings behavior, which the first CI run
resolves. This is exactly why the task stays BACKBURNER rather than bundled into the
verified-green publish batch — the local scan confirmed the deferral was correct, and now
carries a concrete worklist.
