---
trdd-id: 4Y2LKKSZ
title: directory-guard — allow /dev/null sinks and replace the > string scan with a quote-aware redirect tokenizer
column: human_review
created: 2026-08-15T01:13:40+0200
updated: 2026-08-15T21:35:00+0200
current-owner: ai-maestro-plugin-session
task-type: bugfix
priority: high
external-refs: [ai-maestro#123]
npt: []
eht: []
---

# directory-guard: /dev/null allowance + quote-aware redirect tokenizer

**Spec is the MANAGER durable work order** `ai-maestro#123` (comment `5198192106`,
2026-08-05) — read it verbatim before starting; this card summarizes, the comment governs.
Hub tracking card: `TRDD-N1F0QY77` (blocked on this).

## The two defects (verified 2026-08-15 against the working tree: 0 occurrences of `/dev/null` in `scripts/directory-guard.cjs`)

- **(a)** `/dev/null` (and `/dev/stderr`, `/dev/stdout`, `/dev/fd/*`) treated as forbidden
  write targets — `cmd >/dev/null 2>&1` is unusable, and the workaround (redirect to /tmp)
  turns discards into real writes.
- **(b)** redirect detection is a bare `>` string scan with no shell-quoting awareness —
  `echo "text with /Users/<owner>/agents/frank"` is blocked as a write to `/agents/frank`.
  The trigger is the character, not the path.

## The directive (verbatim intent)

Replace the string scan with a real tokenizer whose notion of a redirect is the shell's —
single quotes, double quotes, backslash escapes, heredoc bodies. **Audit the false-NEGATIVE
direction of the old scan BEFORE removing it; route any finding through the security
process, never the public issue.** Blocked-command errors must name the offending token AND
the reason (real out-of-sandbox write vs parser-thought-this-was-a-redirect).

## Acceptance (from the order — drive as REAL commands through the guard, asserting exit status and whether the command ran, never message text alone; include ≥1 true-positive in the same run)

- [ ] `echo hi >/dev/null` succeeds
- [ ] `cmd >/dev/null 2>&1; echo $?` succeeds, exit code preserved
- [ ] `echo "text with /Users/<owner>/agents/frank"` succeeds
- [ ] heredoc body containing `<placeholder>` succeeds when targeting an allowed path
- [ ] genuine out-of-sandbox write still blocked (true-positive regression in same run)
- [ ] quoting contexts each covered: single, double, heredoc body, escaped `\>`, real
      redirect adjacent to a quoted `>` in one command

## Non-goals

Do not widen allowed write roots. Do not publish or exercise any bypass.

## Notes

Advisor consult REQUIRED before implementation (guard rewrite = architectural). On landing,
reply on `ai-maestro#123` with the release version so the hub watch card can verify.

## Approval log

- 2026-08-15T21:35:00+0200 — ai_review PASSED (session self-review, mono-agent mode): advisor consult pre-implementation, premise re-verified first-hand, 53 pre-existing guard pins unmodified, 17 new acceptance tests (70/70 in file), full suite 399 passed / 2 skipped. Moved ai_review -> human_review; USER is the approver.
