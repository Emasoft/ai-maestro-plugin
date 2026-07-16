---
trdd-id: LEMJMCAQ
title: Vendor dev-browser under Emasoft and pin it as a core-plugin dependency
column: completed
created: 2026-07-15T09:51:47+0200
updated: 2026-07-16T12:20:00+0200
current-owner: ai-maestro-plugin (core)
task-type: infra
relevant-rules: [how-to-fix-issues-of-other-projects]
implementation-commits: [df585b9, a088f7a-on-ai-maestro-plugins]
---

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative; supersedes the body) — 2026-07-16

**Why this exists:** issue #19 asked to declare `dev-browser` as a core-plugin
dependency, PINNED (supply-chain safety — a compromised third-party upstream HEAD
must not auto-propagate to every agent). USER decision (2026-07-15): **vendor/fork
under Emasoft, then pin**.

**DONE (verified, not assumed):**
- Forked `SawyerHood/dev-browser` → **`Emasoft/dev-browser`**; resolver tag
  **`dev-browser--v1.0.0` → `b549fb0ecf9fa339100419d597ba4d04cda3e016`** (upstream
  v1.0.0 release commit).
- **Registered in the hub** (2026-07-16): `Emasoft/ai-maestro-plugins` PR #11
  MERGED — entry hosts dev-browser IN the same marketplace, `source: {github,
  Emasoft/dev-browser, sha: b549fb0…}` (**sha-pinned source** — stronger than the
  tag alone; a sha cannot be force-moved), `strict: false` +
  `skills: ["./skills/dev-browser"]` mirroring the upstream self-referential entry
  (the repo ships NO plugin.json at that commit), entry `version: "1.0.0"`.
- **Dep added** to `.claude-plugin/plugin.json`:
  `{name: dev-browser, marketplace: ai-maestro-plugins, version: "1.0.0"}`.
- **Pin verified live**: clean-dir `claude plugin install
  dev-browser@ai-maestro-plugins` (after `marketplace update`) → cache checkout
  `git rev-parse HEAD` = `b549fb0…` exactly, SKILL.md present.

**COMPLETED (2026-07-16, v2.10.0):** shipped via `publish.py`; post-publish
transitive verification PASSED — clean-dir `claude plugin install
ai-maestro-plugin@ai-maestro-plugins` resolved 2.10.0 and reported
`(+ 1 dependency: dev-browser)`; the dep cache checkout is exactly `b549fb0`.
Issue #19 closed. ONLY the standing fork-security-rot reconciliation EHT
survives this TRDD (periodic upstream reconcile + tag/sha bump on
`Emasoft/dev-browser`).

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
