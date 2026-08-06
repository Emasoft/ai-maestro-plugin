---
trdd-id: ZNGTF0FG
title: MANAGER/COS unblock capability — CORE's half (teach the verbs, extend the hook state)
column: dev
created: 2026-08-06T12:15:13+0200
updated: 2026-08-06T14:18:26+0200
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

**DONE (second pass, 2026-08-06 — the server had ALREADY SHIPPED; CORE's proposal was moot):**

3. ✅ **The capability is DEPLOYED and the rule is R42.8** (USER grant 2026-08-05,
   `ai-maestro#125`, catalog v5.3.0–5.3.2). CORE's proposed verbs do NOT exist. Shipped:
   `block-state [--match]` (terminal read, the AUTHORITY), `read-prompt` (hook hint),
   `answer`. **`inject`/`slash`/`queue` are excluded from the exception** — they carry an
   arbitrary command = the CALLER's decision = R42.1; server 403s them cross-agent. The
   5.3.1 pass records that earlier wording named them and a MANAGER obeying it would have
   been 403'd — build the enforcement BEFORE writing the rule.
4. ✅ **ama-unblock rewritten to the deployed surface** (commit after `1f21d6f`): R42.8's
   8 constraints, the 7-reason taxonomy (`ask_user|permission|rate_limited|api_error|
   idle|active|unknown`), never-an-ASSISTANT, identity-prompts-escalate, read-before-
   answer, 409-on-not-blocked. My `--nudge` action is GONE (a nudge is a keystroke).
5. ✅ **Sweep found 2 more contradictions, fixed**: `session-reference.md` listed `answer`
   among self-only send-command-class verbs (now a 2-column matrix); `ama-panel` claimed
   R42.2 grants MANAGER/COS no exemption at all (now: exactly one power, R42.8, and no
   panel verb is in it). `ama-continuity` verified clean (self-only by construction).
6. ✅ **Hook #59 fixed — the question was CLOBBERED, not missing.** `PreToolUse` recorded
   it; `Notification(permission_prompt)` (Claude Code emits it for AskUserQuestion too)
   rebuilt state from a whitelist keeping only a recent `permission_request`, dropping
   `questions` and downgrading the type. **NO age bound on the new carry-through** — a
   blocked agent stays blocked for HOURS (17h observed), so a 10s window re-loses the
   question in exactly the case that matters (my first attempt had it and a slow test
   exposed it). `options` normalized to `{key,label}`. 
7. ✅ **Hook #58: durable `lastError {type,message,at}`** carried through like
   `subagentCount`, surviving SessionStart. 7 new real-subprocess tests, 18 pass.

**REMAINING — NEXT ACTION: nothing runnable; two waits.**

1. **Mirror sync BLOCKED and correctly so** — pushed `governance-rules` is still v5.2.0
   (blob `824812218`, byte-identical to CORE's mirror). R42.8 lives only in an UNPUSHED
   local commit of `~/ai-maestro`. Syncing would embed unverifiable text. Verify with
   `git ls-remote` + read the PUSHED blob's version, never the local working copy.
   When it lands: verbatim body replace → wrapper regen → re-embed both TOCs →
   **regenerate `.cpv-audit-consent.json`** (R42.1/R42.2 line TEXT changed, so the
   full-line sha256 invalidates — ATOM-GSVC-UQT2).
2. Awaiting server answers on #58 (should the WS broadcast carry `questions`/`lastError`
   too? want the red-state regex exported as generated JSON instead of a copied literal?)
   and #128 (the autonomous agent's ADV-03 fixture — answered: stays REFUSE on TWO
   grounds, wrong actor AND wrong verb).
3. At next publish: expect skillaudit A2A_* findings on ama-unblock's cross-agent
   wording; route false-positive rows through `.cpv-audit-consent.json`, never by
   weakening the teaching.

Gotchas: injection false-positives are the R42 harm — the teaching requires the
classifier's evidence before any action; rate-limit blocks want WAIT, not text; a
blocked agent cannot read AMP (that is WHY the exception exists — put this in any future
debate about widening it). Hook starting point already shipped: idle_prompt /
permission_prompt notifications, PermissionRequest events, 8-state broadcast,
`~/.aimaestro/chat-state/<cwd-hash>.json`.

**SUPERSEDED — do NOT carry forward:** "wait for the server to ship the verbs" (it had
already shipped — CHECK THE DEPLOYED CLI's `help` before designing a contract for it);
`column: blocked` / `blocked-by: [ai-maestro#128]`; CORE's proposed verb names
`why-blocked` / `unblock --option|--text|--nudge|--wait` (**none exist** — the real ones
are `block-state`/`read-prompt`/`answer`, and `--nudge` was rejected on principle, not
by oversight); the earlier claim that the exception verbs include `inject`/`queue`; and
the plan to sync the mirror this session (the catalog is unpushed).
