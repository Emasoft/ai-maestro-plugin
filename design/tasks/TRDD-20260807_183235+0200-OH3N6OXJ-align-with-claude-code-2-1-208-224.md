---
trdd-id: OH3N6OXJ
title: Align CORE with Claude Code 2.1.208-2.1.224 and exploit the new surfaces
column: dev
created: 2026-08-07T18:32:35+0200
updated: 2026-08-07T18:32:35+0200
current-owner: ai-maestro-plugin
task-type: infra
approval-tier: 0
scope: project
project-id: ai-maestro-plugin
relevant-rules: []
---

# Align CORE with Claude Code 2.1.208-2.1.224

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative; supersedes the body) — 2026-08-07

**Directive (USER, verbatim):** *"big changes to claude code. study them well and update the
codebase to align with them and take advantage of them"* — followed by the full changelog for
**2.1.208 → 2.1.224**.

**Where the work stands:** fact-gathering pass DONE (below). Nothing changed in the tree yet.

**NEXT ACTION:** A1 is **BLOCKED ON THE USER** — see the A1 finding below. R42 is marked
`CRITICAL — IRON, USER-set`, so the sub-rule the platform invalidated cannot be edited by
MANAGER or by this agent (Tier 3). Proceed with A2–A5, which are Tier 0, while A1 waits.

### Verified facts about THIS repo (✓ = read, not grepped-and-assumed)

| Fact | Status |
|---|---|
| `hooks/hooks.json` registers **12** events: PreToolUse, PostToolUse, Notification, Stop, StopFailure, SessionStart, SessionEnd, SubagentStart, SubagentStop, PreCompact, PostCompact, PermissionRequest | ✓ VERIFIED |
| **No skill uses `context: fork`** — 2.1.218's background-by-default flip cannot affect CORE | ✓ VERIFIED (no `^context:` in `skills/`) |
| **CORE ships no `agents/` directory** — `plugin.json` lists `"agents"` only as a *keyword*, not a path. 2.1.218's "agent names may not contain `:`" is a no-op here | ✓ VERIFIED (read plugin.json in full) |
| `plugin.json` declares no explicit `skills`/`commands` path (conventional layout) — 2.1.221's `"."`-as-skills-path is available but unneeded | ✓ VERIFIED |
| R42's "messaging is the only channel" invariant is asserted across **8** files: `team-governance/{SKILL.md,references/GOVERNANCE-RULES.md}`, `ama-{panel,unblock,session,continuity}/SKILL.md`, `ama-session/references/session-reference.md`, `ai-maestro-agents-management/SKILL.md` | ✓ VERIFIED (grep -l, list is the search surface not the claim) |

### Work items, highest-value first

**A1 — Cross-session `SendMessage` / `ListAgents` (2.1.224) vs AMP + R42. THE REAL ONE.**

Claude Code now lets any local session message any other by name, and `ListAgents` enumerates
them. A `crossSessionInbound` setting gates receipt; `dialogExpiry` bounds the prompt.

This is a **second inter-agent channel that CORE's governance model does not know exists**, and
it bypasses every property AMP was built to provide: no AID identity, no title-scoping, no audit
trail, no R42 authorization matrix. R42.8 was negotiated as *the single carve-out* for one agent
to touch another — and the platform just shipped an ungated one underneath it.

**The precise finding (✓ VERIFIED — read `GOVERNANCE-RULES.md:1598-1611`, not grepped):**

- **R42.1 is NOT violated.** It forbids injecting *"a command, keystroke, prompt, or queued
  input"*. The native channel delivers a **message** the receiving agent processes on its own
  turn — that is the thing R42 was written to *permit*. Do not report this as a breach; it is
  not one, and saying so would misdirect the fix.
- **R42.3 is now FALSE as written.** It asserts *"the messaging system (AMP) is the ONLY
  channel by which one agent may influence another, and it is governed by the R6 communication
  graph"*. Both halves fail: AMP is no longer the only channel, and R6's who-may-message-whom
  graph is unenforced over the native one. The native channel also carries **no AID**, so a
  message has no verifiable author.
- **CORE cannot fix this itself.** R42 is `CRITICAL — IRON, USER-set`. Editing R42.3 — even to
  make it true — is **Tier 3 (USER)**. MANAGER may not, and neither may this agent.

Decide (needs a governance call, not a code change):
- Does CORE **forbid** the native channel for AMP-governed agents (assert `crossSessionInbound`
  off, document why), **bridge** it (accept it as a transport, keep AID on top), or **stay
  silent** (worst option — the invariant reads as true while a hole exists)?
- Whichever way: the 8 R42 sites above assert an invariant that is now **incomplete**, and at
  least the governance rules file must say so.
- Escalation: this touches governance wording → **Tier 2 (MANAGER)** if it changes a rule;
  Tier 0 if it only documents the platform's behavior. Author the proposal, do not self-approve
  a rule change.

**A2 — `DirectoryAdded` hook (2.1.219).** A 13th event CORE does not register. The hook keys
chat-state on `cwdHash`, so a workspace gaining a directory mid-session is exactly the event that
invalidates that key's assumption. Assess whether the state file should track added roots, or
whether registering it is noise. Do NOT register it reflexively — 12 events already fire on every
turn and each one costs.

**A3 — `workflowSizeGuideline` settings key (2.1.219)** and **subagent concurrency**
(`CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`, nesting depth 3, 200-agent cap removed). CORE's
`subagentCount` carry-through in the hook counts nesting that can now legitimately go 3 deep.
Verify the counter still means what its consumers think it means.

**A4 — `archive` plugin source + SHA-256 pinning (2.1.224).** Relevant to how CORE is
distributed via the marketplace. Assess against `scripts/publish.py` — a pinned archive source is
a supply-chain improvement CORE could offer consumers.

**A5 — mechanical / low-risk.** `claude plugin validate` now warns on marketplace+plugin names
Claude Desktop's managed sync rejects — run it and fix anything it flags. Frontmatter booleans
now accept `yes/no/on/off/1/0` (CORE should keep canonical `true/false`; no change, but the
skill-contract test could assert it). Memory frontmatter gained an ISO `modified` timestamp.
Task tool `mode` param deprecated — CORE does not use it (`team-governance/SKILL.md` is the only
hit for the grep and it is a `/review` mention, not a `mode:` use — **re-verify before claiming
clean**). `/review` is now `/code-review`.

### Gotchas

- **`grep -l` output is a search surface, not a verified claim.** The 8 R42 files above were
  located by grep; each must be READ before editing. This project has a standing rule about
  exactly this failure (`~/.claude/rules/claim-verification.md`) and an 80% false-claim incident
  behind it.
- **Do not register a hook event because it exists.** Every registered event fires on every
  matching turn across every session on the machine.

### SUPERSEDED — do NOT carry forward

Nothing yet — this card is new.

## Why

The platform moved 17 versions in one drop and one of those changes (cross-session messaging)
lands directly on top of this plugin's reason for existing. Alignment here is not
housekeeping: an inter-agent-messaging plugin whose governance model does not mention the
platform's own inter-agent messaging is asserting something untrue.

## Acceptance

- [ ] A1 decided and the R42 sites reconciled (or a proposal filed if it changes a rule)
- [ ] A2 assessed with an explicit register/do-not-register decision and its reason
- [ ] A3 `subagentCount` semantics re-verified against depth-3 nesting
- [ ] A4 assessed against the publish pipeline
- [ ] A5 `claude plugin validate` run clean; `mode:` absence re-verified by reading, not grep
- [ ] Full suite green

## Approval log
