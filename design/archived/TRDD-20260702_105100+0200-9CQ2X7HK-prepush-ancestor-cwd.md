---
trdd-id: 9CQ2X7HK
title: pre-push gate — resolve ancestor script token against the ancestor's cwd, not the hook's
column: published
created: 2026-07-02T10:51:00+0200
updated: 2026-07-03T19:33:44+0200
current-owner: ai-maestro-plugin
task-type: security
parent-trdd: TRDD-4b298890
relevant-rules: []
test-requirements: [unit]
release-via: publish
implementation-commits: [bce9d1e]
published-version: 2.8.0
published-at: 2026-07-02T12:50:15+0200
---

# TRDD-9CQ2X7HK — pre-push gate: resolve ancestor script against the ANCESTOR's cwd

## ⏵ STATE — READ FIRST
- SHIPPED in v2.8.0 — fix `bce9d1e` (ancestor of tag `v2.8.0` @ 2026-07-02).
  column: published. Record reconciled 2026-07-03 (was stale at `testing`).
- FIX DONE + 8/8 `tests/test_pre_push_gate.py` pass; hook re-pinned
  (`.githooks/pre-push.sha256`); proven under publish.py G4 (real ancestor).

## The hole (real, narrow, pre-ship)
`.githooks/pre-push` accepts a push when a python/uv ancestor's first positional
realpaths to `<git_root>/scripts/publish.py`. The real publish is launched as
`uv run python scripts/publish.py` — a **relative** token. `canon_path` resolved
it with `realpath` against the **hook's cwd**, not the ancestor's. So a FOREIGN
or STALE `python scripts/publish.py` ancestor (a *different* repo's publish still
live in the process ancestry) false-matched THIS repo — because the hook's cwd
holds a same-named path — silently authorizing an ungated direct `git push`.

Masking: it only manifests when a real publish.py is an ancestor. Standalone
`pytest` has none, so `test_spoof_bash_c_echo_denies` passed there but FAILED
under `publish.py` G4 (the gate caught its own defect before shipping; the hole
was in the unpushed batch commit f6c6d6d).

## The fix
Pass the ancestor pid into `ancestor_is_publish`; add `ancestor_cwd()`
(Linux `/proc/<pid>/cwd`, macOS/BSD `lsof -a -p <pid> -d cwd`). Resolve a
RELATIVE script token against the ancestor's cwd; absolute tokens used directly;
undeterminable cwd → fail closed (never guess against the hook's cwd). Strictly
narrows matching → no spoof regression; genuine-admit tests use ABSOLUTE paths
(absolute branch, no lsof dependency) so publishing cannot brick on lsof.

## Notes and lessons learned
[^1]: a sub-agent concluded "no change — 162/162 pass" by running pytest
  STANDALONE; the bug only reproduces UNDER a publish.py ancestor. Lesson: verify
  an ancestry-dependent gate in the SAME ancestry the failure occurred in.
