---
trdd-id: ZNGTF0FG
title: MANAGER/COS unblock capability — CORE's half (teach the verbs, extend the hook state)
column: dev
created: 2026-08-06T12:15:13+0200
updated: 2026-08-06T14:05:00+0200
current-owner: core-session
task-type: feature
relevant-rules: []
---

# MANAGER/COS unblock capability — CORE's half

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative; supersedes the body) — 2026-08-06

USER directive (2026-08-06, quoted VERBATIM in `ai-maestro#128` — read it there first):
MANAGER and CHIEF-OF-STAFF must detect a session blocked by an AskUser question, by the
prompt-input-field state, or by client error banners (rate limit / API error / retry — the
red text), READ the terminal text to understand why, and INJECT the right answer to resume
it. **Blocked-work is the ONLY case where MANAGER/COS may send direct terminal commands;
everything else goes via AMP per the R6 communication graph.** This is a NEW R42 exception
the server must author spec-first (R42.7 is the template).

UNBLOCKED 2026-08-06 by the USER's follow-up directive ("continue working with ai-maestro
claude on this. be sure to make the skills powerful enough to guarantee the continuity of
the work by the MANAGER and CHIEF-OF-STAFF interventions") — active work, no idle waiting.

**DONE (this session):**

1. ✅ **Skill `skills/ama-unblock/SKILL.md` AUTHORED** (v1.0.0) — the MANAGER/COS
   continuity workflow: authority gate (WHO=MANAGER any / COS own-team, WHEN=classified
   blocked + both-evidence agreement, WHAT=class-legal action only), the 8-class taxonomy
   with the per-class decision table (rate_limited→wait-only, trust_prompt→human-only,
   unknown→escalate), the DETECT→DIAGNOSE→DECIDE→ACT→VERIFY→NOTIFY loop, feature
   detection (`why-blocked --help` probe → full vs interim mode), the tmux-fallback
   PROHIBITION (no verb ⇒ exception not in force), anti-patterns, error table.
   Cross-linked from `ama-session` (Scope + Use also); README count 28→29 + table row.
2. ✅ **Verb contract PROPOSED on `ai-maestro#128`** (comment of 2026-08-06): `why-blocked`
   JSON shape, `unblock --option|--text|--nudge|--wait` with 5 server preconditions
   (title, live classification, class-legality, evidence agreement, cooldown), ledger,
   the read-path question (are cross-agent state/read-prompt reads 403 today?), and the
   NOTIFY-the-target requirement (AMP note so the resumed agent knows the answer's
   provenance — R41). Server reply pending (0 comments at time of writing).

**REMAINING — NEXT ACTION: poll `ai-maestro#128` for the server's reply**, then:

1. Reconcile the skill's verb shapes with whatever the server actually ships (the skill
   is feature-detected, so drift is cheap until the verbs land).
2. Extend `scripts/ai-maestro-hook.cjs` state output with the fields the server's
   classifier requests from inside the harness (they will name them on #128).
3. After the governance catalog gains the R42 exception clause (spec-first, R42.7
   template): re-run the contradiction sweep (ATOM-GFBT-KR76) on the new rule text vs
   CORE skills — including the new ama-unblock — then re-sync the mirror.
4. At next publish: expect skillaudit A2A_* findings on ama-unblock's cross-agent
   wording; route the false-positive rows through `.cpv-audit-consent.json` (full-line
   sha256 recipe — ATOM-GSVC-UQT2), never by weakening the teaching.

Gotchas: injection false-positives are the R42 harm — the teaching requires the
classifier's evidence before any action; rate-limit blocks want WAIT, not text; a
blocked agent cannot read AMP (that is WHY the exception exists — put this in any future
debate about widening it). Hook starting point already shipped: idle_prompt /
permission_prompt notifications, PermissionRequest events, 8-state broadcast,
`~/.aimaestro/chat-state/<cwd-hash>.json`.

**SUPERSEDED — do NOT carry forward:** "wait for the server to ship the verbs" as the
next action (the USER ordered active work); `column: blocked` / `blocked-by:
[ai-maestro#128]` (dropped — the skill work was never server-blocked, only step 2's hook
fields and step 3's sweep are).
