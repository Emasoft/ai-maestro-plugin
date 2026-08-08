---
trdd-id: ZNGTF0FG
title: MANAGER/COS unblock capability — CORE's half (teach the verbs, extend the hook state)
column: human_review
blocked-by: []
created: 2026-08-06T12:15:13+0200
updated: 2026-08-08T12:31:44+0200
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

3. ✅ **RE-REVERSED 2026-08-08 — R42.8 IS RATIFIED. The 2026-08-07 "NOT ratified"
   correction on this line was itself the error.** The original line was right and I
   overwrote it. `Explicit (USER — 2026-08-05, ai-maestro#125, TRDD-AODXPI5E)`, published
   in `docs/GOVERNANCE-RULES.md` **v5.3.3** on `Emasoft/ai-maestro@governance-rules`
   (blob `a13bed73fa9e`). The measurement behind the retraction was accurate — R42.8 was
   absent from every published copy on 2026-08-07 — and the inference was not: the grant
   was 2026-08-05 and only the **publication** lagged, landing 2026-08-08. **`ai-maestro#125`
   being OPEN is not evidence a rule is unratified**, and *"I cannot verify this"* is not
   *"this is not true"*. Cost: four role-plugins retracted CORRECT statements on my report.
   **For an absence, "true but not yet published" is always a live answer.**

   **The exception verbs are THREE — `block-state`, `read-prompt`, `answer` — and the
   dividing line is CALLER DECISION, not read-vs-write.** `inject`/`slash`/`queue` carry an
   arbitrary command = the caller's decision = R42.1; the server 403s them cross-agent.
   `block-state` reached the row late: v5.3.2 omitted it, I reported a doc-vs-implementation
   gap, the hub checked `lib/sudo-guard.ts:449` (it routes `GET /api/agents/[id]/block-state`
   through the **same `unblock-prompt` action**) and published v5.3.3 **twelve minutes**
   later. **The doc was the stale side, not the CLI** — and that is the second time in two
   days I measured one commit early. Both times the fix is the same act, and it is not
   "measure more carefully": **resolve the branch TIP first, then read the row.**
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
   `subagentCount`, surviving SessionStart.
8. ✅ **Hook #60: `writerVersion` stamp on every state record** — the fleet aggregator
   reads files written by many installed versions, so a missing `questions` was
   ambiguous between "no question pending" and "an agent still running the #59 clobber
   bug" (opposite actions). Resolved from `__dirname`, NEVER `$CLAUDE_PLUGIN_ROOT` (that
   names the spawning plugin's context and would stamp someone else's version — a wrong
   stamp is worse than none; test passes with the env var pointed elsewhere).
9. ✅ **Answered #60's three asks**, incl. the one blocking requirement for
   `TRDD-LT5N2JA4`: it MUST have a frozen-CLI verb, not only an API route — core#11 +
   `test_no_direct_api_calls` make an API-only probe unusable by every CORE skill. Also
   asked for 3 hook source-states (`present`/`stale`/**`absent`**) since our hook fails
   SILENTLY without node on PATH, so "no file" is an install defect while "17h old" is
   the healthy blocked case. 8 new real-subprocess tests; **330 suite tests pass**.

10. ✅ **Cross-repo coordination so the procedure is not written THREE times.** The server
    asked `ai-maestro-assistant-manager-agent#35` AND `ai-maestro-chief-of-staff#29` to each
    author a skill carrying this same procedure + the R42 rule. Commented on both (comments
    only — never their source, per the cross-project rule): CORE already ships `ama-unblock`
    in the umbrella plugin they inherit, so reference it and add only the role-specific part
    (MANAGER: scope + derivability; COS: how it establishes own-team membership BEFORE
    acting — the one constraint a COS can violate by accident). Divergent copies of an R42
    rule produce either a violation or a stalled fleet, with no way to tell which copy an
    agent read. Also passed on the probe-the-deployed-CLI lesson so they do not repeat my
    error.

**COLUMN: `dev` → `blocked` (2026-08-07).** Held in `dev` while its own NEXT ACTION read
"nothing runnable" — and `dev` asserts someone is working the card right now. That is the
same defect this session fixed on `TRDD-202ccfa2`, so it gets the same treatment rather
than an exception for being mine: the blockers are real, external, and now greppable in
`blocked-by:`. Two of the three deliverables ARE done and shipped (the skill; the hook
extensions for #58/#59/#60); only the mirror re-sync and the open server questions remain,
and neither is CORE's to move. `pre-block-column: dev` restores it when they land.

**UNBLOCKED 2026-08-08 — the blocker landed and CORE's half is SHIPPED.**

**COLUMN: `blocked` → `human_review`.** Every deliverable is out; what is left is not
work, it is other repos' answers. Holding `blocked` now would be the same lie in the
other direction — a card claiming it cannot move while nothing is stopping it.

1. ✅ **Mirror sync DONE** — the blocker was real and it cleared. `governance-rules`
   published v5.3.3 (blob `a13bed73fa9e`); mirror re-synced and shipped in **v3.1.2**,
   body verified **byte-identical** to upstream, `.cpv-audit-consent.json` regenerated
   (R42.1's row text changed exactly as predicted, so its full-line sha256 invalidated —
   ATOM-GSVC-UQT2 held), and R42.8's brand-new row consented after reading it in full.
   Two corrections rode in that CORE never had: R22.2 lost its `@<owner>` from the byline
   **template**, and R39.2's publication fact. The three-day staleness now has a standing
   guard (`tests/test_governance_mirror_stamp.py`) that asserts the POINTER — blob +
   read-date — and **never fetches**, because a network test collapses "stale" and
   "offline" into one red.
2. `ai-maestro#128` is **CLOSED**. Remaining open: `ai-maestro-plugin#58` / `#60`, and
   neither blocks anything — they are server digests awaiting server answers.
3. Awaiting server answers on #58 (should the WS broadcast carry `questions`/`lastError`
   too? want the red-state regex exported as generated JSON instead of a copied literal?),
   #60 (will `TRDD-LT5N2JA4` get a frozen-CLI verb? will `sources` split
   `absent` from `stale`?), and #128 (the autonomous agent's ADV-03 fixture — answered:
   stays REFUSE on TWO grounds, wrong actor AND wrong verb).
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
