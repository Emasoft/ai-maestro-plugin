# TRDD-71a2239a-4d06-42af-b083-588954385fdc — Hash-pin the pre-push hook template

**TRDD ID:** `71a2239a-4d06-42af-b083-588954385fdc`
**Filename:** `design/tasks/TRDD-71a2239a-4d06-42af-b083-588954385fdc-aegis-pre-push-hook-integrity.md`
**Tracked in:** this repo (design/tasks/ is git-tracked)
**Source audit:** `reports/v258-pre-publish-audit/aegis-security.md` (HIGH-05)
**Severity:** HIGH (silent gate weakening)
**Status:** Not started
**Filed:** 2026-05-08

## Problem

`scripts/publish.py:74-170` (`PRE_PUSH_HOOK_TEMPLATE` constant +
`ensure_pre_push_hook`) is the **single source of truth** for what gates
git push on every developer's machine. publish.py writes this template
to `.githooks/pre-push` on every run and runs `git config core.hooksPath
.githooks` on every run.

There is no signature, no hash, no commit-pinning. Anyone who can land a
commit that modifies `PRE_PUSH_HOOK_TEMPLATE` silently weakens (or
removes) the hook for every clone the next time they run `publish.py`.
The self-integrity check at lines 1146-1215 only flags forbidden
*string patterns* (`--skip-tests`, etc.) — it does not protect the hook
template itself. A future commit can add a single line `exit 0` at the
top of `PRE_PUSH_HOOK_TEMPLATE` and the next `publish.py` run will
silently install the broken hook.

Combined with HIGH-02 (TRDD-4b298890-…), a compromised maintainer
commit can permanently disable the gate.

## Design

### Layer 1 — Hash file in the repo

Add `.githooks/pre-push.sha256` containing the SHA-256 of
`PRE_PUSH_HOOK_TEMPLATE` after rendering. `ensure_pre_push_hook` must:

1. Compute the SHA-256 of the rendered template.
2. Read the expected hash from `.githooks/pre-push.sha256`.
3. Refuse to write the hook if they differ — print a clear message
   asking the maintainer to update the hash file in the same commit.

Rotating the hook then requires updating BOTH the template constant
AND the hash file in the same commit, which makes the change visible
in code review.

### Layer 2 — CI verification

Add a CI job on the default branch that:

1. Renders `PRE_PUSH_HOOK_TEMPLATE` to stdout via a tiny helper script.
2. Computes its SHA-256.
3. Compares against `.githooks/pre-push.sha256`.
4. Compares against the SHA-256 of the literal `.githooks/pre-push`
   file in the repo (the committed copy must also match the template).
5. Fails the build on any mismatch.

### Layer 3 — `ensure_pre_push_hook` no-op for read-only review

When publish.py is invoked with `--dry-run` (already supported), it
must NOT rewrite `.githooks/pre-push`, even if the file is missing or
stale. This lets reviewers run publish.py in a clean checkout to
verify the pipeline without mutating the hook.

## Acceptance criteria

- [ ] `.githooks/pre-push.sha256` exists and matches both the template
  constant and the on-disk `.githooks/pre-push`
- [ ] CI job verifies all three are in lockstep on every push to default
- [ ] Modifying `PRE_PUSH_HOOK_TEMPLATE` without updating the hash file
  causes the next publish.py run to abort with a clear message
- [ ] Modifying `.githooks/pre-push` directly (out-of-band edit) is
  detected by the next publish.py run and reverted (or aborted with
  a clear message; whichever a reviewer prefers)
- [ ] HIGH-02 (TRDD-4b298890-…) is filed and resolved IN THE SAME
  RELEASE — both hardenings are needed together

## Dependencies

- **HIGH-02 (TRDD-4b298890-…):** without HIGH-05's hash-pin, an
  attacker rolls back HIGH-02's nonce/Layer-1 changes in
  `PRE_PUSH_HOOK_TEMPLATE`. Without HIGH-02, HIGH-05 protects the
  wrong version of the template. Land both together.

## Out of scope

- GPG signing of the hook template — heavier UX cost, and the
  hash-pin already gates the risky path through PR review
- Vendoring the hook into a separate repo — adds a sync chore
- Auto-generating the hash file from a build step — invites accidental
  desync; manual update in the rotating commit is the point
