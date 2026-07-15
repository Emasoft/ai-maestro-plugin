---
trdd-id: LEMJMCAQ
title: Vendor dev-browser under Emasoft and pin it as a core-plugin dependency
column: dev
created: 2026-07-15T09:51:47+0200
updated: 2026-07-15T10:49:58+0200
current-owner: ai-maestro-plugin (core)
task-type: infra
relevant-rules: [how-to-fix-issues-of-other-projects]
implementation-commits: []
---

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative; supersedes the body) — 2026-07-15

**Why this exists:** issue #19 asked to declare `dev-browser` as a core-plugin
dependency, PINNED (supply-chain safety — a compromised third-party upstream HEAD
must not auto-propagate to every agent). USER decision (2026-07-15): **vendor/fork
under Emasoft, then pin** (chosen over "ship floating" and "hold out"). "Pin to a
commit" is NOT expressible in `plugin.json` — CC deps support only
`name`/`version`/`marketplace`, and `version` resolves against `{name}--v{version}`
git tags. Third-party `sawyerhood/dev-browser` has only plain `vX.Y.Z` tags and its
marketplace declares no version, so an owner-controlled fork with the right tag is
the only real pin.

**DONE (this session, verified on GitHub):**
- Forked `SawyerHood/dev-browser` → **`Emasoft/dev-browser`** (`gh repo fork`, default branch `main`).
- Created resolver tag **`dev-browser--v1.0.0` → commit `b549fb0ecf9fa339100419d597ba4d04cda3e016`**
  (the upstream `v1.0.0` release commit) in the fork, verified it resolves.

**NEXT ACTION (cross-repo — do in the marketplace hub's own context, NOT from the plugin session):**
1. Register `Emasoft/dev-browser` in the Emasoft marketplace the core plugin ships from
   (`Emasoft/ai-maestro-plugins`, `.claude-plugin/marketplace.json`): add a `dev-browser`
   plugin entry with `source: {source: "github", repo: "Emasoft/dev-browser"}`. Decide
   whether to host it IN `ai-maestro-plugins` (then the dep is same-marketplace) or keep it
   cross-marketplace and repoint `allowCrossMarketplaceDependenciesOn` from
   `dev-browser-marketplace` (sawyerhood) to the Emasoft fork's marketplace.
2. Only AFTER step 1 exists, add to THIS repo's `.claude-plugin/plugin.json`:
   `"dependencies": [{ "name": "dev-browser", "marketplace": "<emasoft-mkt>", "version": "1.0.0" }]`
   — do NOT add it before step 1 or every fresh install 404s on the unresolved dep.
3. Verify: clean-dir `claude plugin install ai-maestro-plugin ai-maestro-plugins` pulls
   `dev-browser` transitively at commit `b549fb0` (the version string should carry that sha).
4. Bump version, ship via `publish.py`.

**STANDING OBLIGATION (EHT — do not forget):** a pinned fork FREEZES at `b549fb0`
and no longer inherits upstream SECURITY fixes. `Emasoft/dev-browser` must be
periodically reconciled with `SawyerHood/dev-browser` HEAD and its resolver tag
bumped when a security patch lands, or the pin silently rots into a stale-vuln.
Carry this as a recurring EHT on the fork. Source: USER-memory note
`fleet-third-party-plugin-dep-fork-pin-pattern.md` (the ratified fleet pattern
this task instantiates).

**SUPERSEDED — do NOT carry forward:** the issue-#19 floating shape
`{name: dev-browser, marketplace: dev-browser-marketplace}` (tracks sawyerhood HEAD, no
pin) — rejected by the USER in favor of the fork+pin above.

**Cross-repo constraint:** step 1 edits `Emasoft/ai-maestro-plugins` (a different repo).
Per `~/.claude/rules/how-to-fix-issues-of-other-projects.md`, do it in that repo's own
session / via a PR, not from the plugin working tree.

## Background

See issue #19 (Emasoft/ai-maestro-plugin) and its supply-chain note. The marketplace
already allowlisted `dev-browser-marketplace` (sawyerhood) via the earlier
web-scenario-tester work; this task replaces that third-party trust with an
Emasoft-controlled, version-pinned fork.
