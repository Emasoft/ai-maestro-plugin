---
trdd-id: 4b298890-2cf2-4828-a06f-46c4a8580c82
title: Strengthen pre-push gate against bash -c / exec -a ancestor spoofing
column: backburner
created: 2026-05-08T00:00:00+0200
updated: 2026-06-11T11:35:00+0200
current-owner: null
task-type: security
severity: HIGH
relevant-rules: []
---

# TRDD-4b298890-2cf2-4828-a06f-46c4a8580c82 — Strengthen pre-push gate against `bash -c` / `exec -a` ancestor spoofing

**Filename:** `design/tasks/TRDD-4b298890-2cf2-4828-a06f-46c4a8580c82-aegis-pre-push-gate-bash-c-bypass.md`
**Tracked in:** this repo (design/tasks/ is git-tracked)
**Source audit:** `reports/v258-pre-publish-audit/aegis-security.md` (HIGH-02)
**Severity:** HIGH (publish-policy bypass)
**Status:** Not started
**Filed:** 2026-05-08

## Problem

`.githooks/pre-push:16-46` walks the parent-process tree looking for an
ancestor whose `ps -o command=` contains `python*scripts/publish.py`.
The matcher accepts **any** string containing both substrings, in any
combination — letting an attacker synthesize the magic ancestor without
ever running publish.py:

```bash
# Bypass 1 — wrapper command names the file but doesn't run it
bash -c 'echo "running python scripts/publish.py preview"; git push origin v9.9.9'

# Bypass 2 — python interpreter exec'd with publish.py in argv but stops before push
python -c 'import sys; sys.argv=["python","scripts/publish.py"]; import subprocess; subprocess.run(["git","push","origin","--force","v9.9.9"])'

# Bypass 3 — exec into shell whose argv contains the magic string
exec -a "python scripts/publish.py" bash
git push origin v9.9.9
```

A maintainer (or an attacker who has compromised a maintainer's machine)
can bypass the no-skip publish policy and push an unsigned, unvalidated
tag — the very scenario the policy was added in 2.5.1 to prevent.

## Design

Two layers, applied together:

### Layer 1 — Match by executable path, not command-line text

Use `ps -o pid,ppid,comm,command=` and verify:

1. The ancestor's `comm` (binary name) is exactly `python`, `python3`, or `uv`.
2. `command` starts with that binary path.
3. The first script-file argument resolves to `<git_root>/scripts/publish.py`
   (via `realpath`).

Reject ancestors whose `comm` is `bash`/`zsh`/`sh` even if their `command`
contains `publish.py` literally as text (that's a shell, not a python interp).
Reject `exec -a` ancestors via the same `comm`-vs-`command[0]` mismatch check.

### Layer 2 — Nonce file

publish.py writes a short-lived nonce file at the start of its run:

```
<git_root>/.git/PUBLISH_NONCE
  mode 0600
  contents = sha256(PID || start_time || hostname)
```

The pre-push hook checks:

- File exists.
- File mtime is within the last 600 seconds.
- File is owned by the current UID.
- The PID embedded in the nonce is still alive AND its `comm` matches Layer 1.

publish.py deletes the nonce on exit (success or failure, in a `finally`
block). A stale nonce from a crashed publish run is auto-rejected by the
mtime check.

### Layer 3 — Defence-in-depth

If both Layer 1 and Layer 2 pass but the `git push` is for a tag
matching `v[0-9]+\.[0-9]+\.[0-9]+` AND the local branch is not the
default branch, refuse and log to `.git/PUBLISH_REJECTIONS.log` with the
ancestor chain. (Also helps detect attempted bypasses retroactively.)

## Acceptance criteria

- [ ] All 3 bypass payloads in the problem statement return EXIT 1 from the hook
- [ ] Legitimate `python scripts/publish.py --patch` runs continue to pass
- [ ] Legitimate `uv run scripts/publish.py --patch` runs continue to pass
- [ ] Stale nonce (>600s old) rejected with clear error
- [ ] Nonce auto-deleted on publish.py exit (test: kill -9 publish.py mid-run, next run cleans up)
- [ ] HIGH-05 (hook integrity) is filed and resolved IN THE SAME RELEASE — both hardenings are needed together to prevent rollback

## Dependencies

- **HIGH-05 (TRDD-71a2239a-…):** the nonce/Layer-1 changes go in
  `PRE_PUSH_HOOK_TEMPLATE` inside publish.py. Without HIGH-05's
  hash-pin, an attacker can simply roll back the template. Land both
  in the same release.

## Out of scope

- Hardware-backed attestation (TPM, Apple Secure Enclave) — overkill for
  a developer-machine policy gate
- CI-side signature verification on the tag — separate, complementary
  TRDD; useful but does not replace the local pre-push gate
