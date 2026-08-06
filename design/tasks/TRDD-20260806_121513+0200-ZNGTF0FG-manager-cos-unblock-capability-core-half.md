---
trdd-id: ZNGTF0FG
title: MANAGER/COS unblock capability — CORE's half (teach the verbs, extend the hook state)
column: blocked
pre-block-column: todo
blocked-by: [ai-maestro#128]
created: 2026-08-06T12:15:13+0200
updated: 2026-08-06T12:15:13+0200
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

**The server's half** (detection heuristic, tmux capture-pane + regex classifier, a
read-only `why-blocked` query verb, a gated blocked-only injection verb, ledger audit) is
asked in `ai-maestro#128`. **NEXT ACTION: wait for the server to ship the verbs**, then:

1. Teach the new frozen-CLI verbs in the MANAGER/COS-facing skills (feature-detected, per
   the hibernation pattern in `ai-maestro-agents-management` §8a) with the governance
   constraints INLINE: blocked-only, both-evidence-required, everything else AMP.
2. Extend `scripts/ai-maestro-hook.cjs` state output with whatever the server's heuristic
   asks for from inside the harness (they will name it on #128).
3. After the governance catalog gains the exception clause: re-run the contradiction sweep
   method (ATOM-GFBT-KR76) on the new rule text vs CORE skills, then re-sync the mirror.

Gotchas: injection false-positives are the R42 harm — CORE's teaching must require the
classifier's evidence before any injection; rate-limit blocks usually want WAIT, not text.
Starting point already shipped: the hook's idle_prompt / permission_prompt notifications,
PermissionRequest events, 8-state broadcast, `~/.aimaestro/chat-state/<cwd-hash>.json`.
