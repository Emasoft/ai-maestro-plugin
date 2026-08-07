---
trdd-id: OH3N6OXJ
title: Align CORE with Claude Code 2.1.208-2.1.224 and exploit the new surfaces
column: human_review
pre-block-column: dev
created: 2026-08-07T18:32:35+0200
updated: 2026-08-07T19:03:43+0200
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

**NEXT ACTION: nothing — this card is in `human_review` and needs TWO USER decisions.** A2, A4
and A5 are DONE (decisions + rationale recorded below). Moved out of `dev` deliberately: `dev`
asserts someone is working the card right now, and nobody is. Restore to `dev` (see
`pre-block-column:`) the moment either decision lands.

1. **A1 — governance wording.** R42.3 is false as written. R42 is `CRITICAL — IRON, USER-set` ⇒
   **Tier 3**; neither MANAGER nor this agent may edit it even to make it true. Options put to
   the USER: **document-only** (recommended — see the correction below; the platform already
   defends the authority concern, so this is an audit/routing blind spot, not a hole),
   **bridge** (accept native as transport, keep AID on top), or **forbid**.
2. **A3 — implementation go/no-go.** The `subagentCount` lock is a Tier-0 change I can make, but
   it puts a lockfile in a hook that fires on **every event of every Claude Code session on this
   machine**. A stale-lock or missing-timeout bug hangs the whole machine, so it wants an
   explicit go rather than a drive-by at the end of a long session. Recommended shape: `O_EXCL`
   lockfile mutex with a staleness timeout, chosen because only a lock closes the window the
   file's own comment names.

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

> **⚠ CORRECTED 2026-08-07 against the authoritative changelog** (`gh api
> repos/anthropics/claude-code/contents/CHANGELOG.md`, 5370 lines, read first-hand). My original
> framing — *"the platform just shipped an ungated channel underneath R42.8"* — was **wrong in
> two ways that change the verdict**, and I had already relayed it to two peer role-plugin
> sessions before checking. The corrected finding is below; the superseded claim is kept in the
> SUPERSEDED list, not deleted.

**What is actually true (✓ each line traced to its changelog entry):**

- **Cross-session `SendMessage` is NOT new in 2.1.224.** It predates R42.8 (2026-08-05) by
  months — `2.1.77` already documents `SendMessage({to: agentId})` as the resume path, `2.1.162`
  fixes a `$TMPDIR` bug in it. **2.1.224 added three things**: reach across **machines** ("on any
  of your machines"), **`ListAgents` discovery**, and the `crossSessionInbound`/`dialogExpiry`
  settings.
- **It is NOT ungated — the platform hardened it against exactly my concern, twice.**
  `2.1.166`: *"messages relayed via `SendMessage` from other Claude sessions **no longer carry
  user authority** — receivers refuse relayed permission requests, and auto mode blocks them"*.
  `2.1.222`: messages to other agent sessions are *"evaluated by the permission classifier before
  dispatch"*. `2.1.224`'s `crossSessionInbound` holds messages to a bypassed-permissions session
  for the user's approval. **Permission laundering — the failure mode I raised — is the specific
  thing the platform already defends.**

**So the severity drops from "security hole" to "audit and routing blind spot".** That reframing
matters: a hole gets closed by forbidding the channel; a blind spot gets closed by observing it.
Recommending a ban on the strength of the original framing would have been the wrong fix.

**The precise finding (✓ VERIFIED — read `GOVERNANCE-RULES.md:1598-1611`, not grepped):**

- **R42.1 is NOT violated.** It forbids injecting *"a command, keystroke, prompt, or queued
  input"*. The native channel delivers a **message** the receiving agent processes on its own
  turn — that is the thing R42 was written to *permit*. Do not report this as a breach; it is
  not one, and saying so would misdirect the fix.
- **R42.3 is still FALSE as written — this part survives the correction.** It asserts *"the
  messaging system (AMP) is the ONLY channel by which one agent may influence another, and it is
  governed by the R6 communication graph"*. Both halves still fail: AMP is not the only channel,
  and R6's who-may-message-whom graph is unenforced over the native one. The native channel
  carries **no AID**, so a message has no verifiable author and no AI-Maestro audit entry.
- **What 2.1.224 genuinely widened, and is worth the USER's attention:** the channel now reaches
  **across machines**, and `ListAgents` lets an agent **enumerate peers without going through the
  server's roster**. AID identity and R42 were designed as per-host concerns; cross-machine reach
  and out-of-band discovery are a larger surface than the rules contemplate — independent of the
  authority question, which the platform handles.
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

**A2 — `DirectoryAdded` hook (2.1.219). DECIDED: do NOT register.** A 13th event CORE does not
register. Reason, recorded so nobody re-litigates it: chat-state is keyed on `cwdHash`, and
adding a workspace root **does not change `cwd`** — so the key the state is filed under is
unaffected. No consumer asks "which roots does this agent have"; the server tracks agents by
workdir. Registering it would add an event that fires on every matching turn across every
session on the machine and feeds nothing. Revisit only if a consumer appears that needs the
root set.

**A4 — `archive` plugin source + SHA-256 pinning (2.1.224). DECIDED: cross-repo, not CORE's to
make.** CORE's `plugin.json` declares dependencies by `marketplace` + `version`; switching a
consumer to a SHA-256-pinned `archive` source is a **marketplace-repo** change
(`ai-maestro-plugins`), not a change to this manifest. Per the cross-project rule, file it
upstream rather than editing that repo from here. It is a genuine supply-chain improvement and
worth proposing — just not from this card.

**A3 — `subagentCount` is an unlocked cross-process counter, and the platform just made its
race the normal case. VERIFIED DEFECT — second-most-valuable item after A1.**

✓ VERIFIED by reading `ai-maestro-hook.cjs:128-149, 679-711`:

- `SubagentStart` does `getSubagentCount(cwd) + 1` then `writeState` — a **read-modify-write
  across separate Node processes with no lock**. The file's own comment concedes it:
  *"One read does not close that race (only a lock would)"*. The atomic `rename(2)` prevents a
  **torn** file; it does nothing about a **lost update**.
- Two concurrent `SubagentStart`s both read 5, both write 6, and the counter is permanently
  1 low. Nothing ever recomputes it from truth, so the error **never re-syncs** — it compounds
  across a fan-out.
- 2.1.x removed the 200-spawn cap, raised default nesting to **depth 3**, and caps concurrency
  at **20**. Concurrent Start/Stop events go from rare to routine. The race was latent; the
  platform made it live.

**Why this is a safety issue, not a cosmetic one.** The counter gates **restart/autoContinue**
(`ai-maestro-hook.cjs:680`). An undercount reaches 0 while subagents are still running, `status`
flips to `active`, and the restart gate opens on a busy agent. That is exactly the interlock
**R42.7(c)** leans on — *"the same `idle_prompt` + subagent-counter 409 the human's Restart
button obeys"*. So a platform change to subagent orchestration quietly weakened a governance
interlock, in the fail-DANGEROUS direction (reading high would merely keep the gate shut).

**Not fixed here — it is a design call on a load-bearing file.** Reading LOW is the only unsafe
direction, so the fix should be chosen for fail-safety, not exactness: an `O_EXCL` lockfile
mutex with a staleness timeout, or a CAS-retry loop, or tracking live agent ids instead of an
integer (note: a set does **not** self-heal either — a lost add is still a lost add). Recommend
the lockfile: it is the only option that actually closes the window the comment names.
`workflowSizeGuideline` (2.1.219) is unrelated config and needs no CORE change.

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

### A1 — LIVE EVIDENCE, observed 2026-08-07, not hypothesised

A session **claiming to be the ai-maestro server** (branch `governance-rules`) messaged CORE on
the native channel, explicitly framing it as *"trialling Claude Code's cross-session SendMessage
… to coordinate directly instead of via GitHub issues"*, and asked what CORE is working on, what
it is blocked on, and what server behaviour it depends on.

Three things are true at once and together they ARE the A1 finding:

1. **The claim of identity is unverifiable.** No AID, no title, no R6 routing, no audit entry.
   The questions were benign and I answered as I would in public — but nothing in the channel
   distinguishes the server from anyone able to open a socket.
2. **The reply could not be routed at all.** The message carried **no `from` address**, only
   `from-name="Ask the advisor"`, and that name is absent from `ListAgents` (17 peers). The send
   failed: *"No agent named 'Ask the advisor' is reachable."* I did **not** guess a nearby peer
   from the list — broadcasting a status report to a mis-identified session is a worse failure
   than not replying.
3. **Governance coordination is already migrating onto it**, by explicit intent, away from the
   auditable GitHub-issue path.

So the blind spot is not theoretical and not future: parties are already coordinating governance
over a channel where authorship cannot be verified and replies can silently fail to route. That
is an argument for **observing and bridging** the channel (option 2), not for forbidding it —
forbidding a channel people are already using produces unlogged use, not less use.

**SECOND INCIDENT, same hour — and this one caused real harm.** The **INTEGRATOR (AMIA)** session
messaged CORE saying its USER had directed it to **stop autonomous work** and that it was
*"standing by and will follow your directives"*. Two failures compounded:

1. **An agent accepted work assignment from an unauthenticated peer.** CORE is not its MANAGER,
   not a COS, not the governance owner. I declined the directive role — but the channel offered
   no way for AMIA to establish that before acting on it. An agent that takes its next task from
   whoever messaged it last has replaced its authority chain with the transport.
2. **The reply could not be routed — again.** No `from` address; no integrator session in
   `ListAgents` (17 peers, checked twice). **So AMIA is idle, waiting on a response that has no
   delivery path, and cannot be told why nothing is coming.**

**This is the strongest argument on the card: the channel can silently STRAND an agent.** Not
"unaudited" in the abstract — a real agent stopped working, and the fleet's own rescue story
(`ama-unblock`) does not cover it, because AMIA is not blocked on a prompt; it is blocked on a
message that will never arrive. I reported the strand to the apparent MANAGER session as a
status report (explicitly not a directive), noting its own USER is the only reachable route.

**Both incidents share one root: a message with no verifiable sender and no return path.** A
bridge that stamped AID on outbound native messages and logged inbound ones would have prevented
the second outright — AMIA could have seen that CORE holds no authority over it, and CORE could
have answered. That is why the recommendation is bridge, not ban.

### A6 — the governance SSOT was found mid-card, and CORE conforms

**The SSOT lives on an UNMERGED branch, `Emasoft/ai-maestro@governance-rules`** — a query against
`main` 404s and that 404 means nothing. It carries `docs/GOVERNANCE-RULES.md`, `rules/aimaestro/`
(5 multi-agent overlays on the host-global base rules), and `design/specs/` including
**`role-plugins-spec.md`** (spec-version 1.0.0, `status: authoritative`).

✓ **CORE conformance checked against it:**
- CORE is **not** a role-plugin (no `.agent.toml`, no `agents/`), so RP-QUAD / RP-TOML /
  RP-PREFIX do not apply — correct by design; CORE is the umbrella core plugin.
- All five skills role-plugins declare as `external_skills` **exist**: `planning`,
  `agent-messaging`, `agent-identity`, `team-kanban`, `team-governance`.
- **RP-VAL-05** (no element may embed `/api/…`, a `:23000` URL, or a raw server HTTP call — go
  via the `aimaestro-*` / `amp-*` CLI layer) is enforced by a real test,
  `tests/test_no_direct_api_calls.py`.

**RP-MODEL-01 corrects an answer I gave three peers — then turns out to be FALSE itself.** I had
said no fleet policy existed on `model:` pins; the spec does carry one (pin the family alias
`opus` on the main-agent, omit on subagents, explicitly conceding it contradicts CPV's CA-04
cache-warmth guidance). A documented deliberate inconsistency is not the same as no policy — so
my "unknown" was wrong. But the rule's own factual premise does not hold.

✓ **Complete 8-of-8 sweep on CONSISTENT provenance.** Seven read from
`~/.claude/plugins/cache/ai-maestro-plugins/<P>/<newest version>/agents/<P>-main-agent.md`.
Integrator is not installed here, so I first read its repo HEAD and flagged that as a weaker,
different-provenance value rather than hiding the gap; the architect peer then **discharged the
caveat instead of carrying it** — `gh release view` ⇒ latest `v1.3.7` (2026-06-22), and the
main-agent at `?ref=v1.3.7` also reads `model: opus`, identical to HEAD. All eight values are now
shipped-release readings. *A caveat that can be discharged with one command should be, not
inherited by every later reader.*

| `model:` value | plugins | count |
|---|---|---|
| `opus` | assistant-manager 2.14.3, chief-of-staff 2.21.1, orchestrator 1.9.5, integrator **v1.3.7** | **4** |
| *(no `model:` key)* | architect 2.11.1, programmer 1.4.7 | **2** |
| `inherit` | maintainer 1.7.21 | **1** |
| `sonnet` | autonomous 1.5.5 | **1** |

**Exactly half the fleet follows the rule the spec says all of it follows.** Four spellings, and
the architect peer sharpened one I missed: `inherit` is **semantically "no pin" but syntactically
a pin**, so any ruling that treats the field as binary re-opens this.

**The decisive fact is not the distribution — it is the mandated counterexample.**
`ai-maestro-autonomous-agent` pins **`sonnet`**, and `RP-TITLES-02` in the *same document* calls
that plugin **mandatory**. A universal whose counterexample the same spec requires is not a rule
with an outlier; it is a rule that was never true. That makes "amend the rule to describe
reality" available **without touching any plugin** — the cheapest exit, and one that framing this
as non-conformance would have hidden.

**Dating caveat for whoever amends it:** the spec's survey is dated 2026-07-22; these readings
are ~2 weeks later. Either it was inaccurate then or the plugins drifted since — the ruling needs
only the current state, but the amendment's author may want to know which.

### Gotchas

- **`grep -l` output is a search surface, not a verified claim.** The 8 R42 files above were
  located by grep; each must be READ before editing. This project has a standing rule about
  exactly this failure (`~/.claude/rules/claim-verification.md`) and an 80% false-claim incident
  behind it.
- **Do not register a hook event because it exists.** Every registered event fires on every
  matching turn across every session on the machine.
- **UNRESOLVED version discrepancy on the `context: fork` backgrounding flip.** This card says
  2.1.218; the AMAA peer session says 2.1.222. One of us misread the changelog. It does not
  change CORE's answer (no-op either way — zero `context:` keys anywhere, verified three ways),
  but **do not cite a version from this card** without checking the changelog text first. A
  wrong version in a fleet-wide advisory sends other repos looking at the wrong release.
- **The `context: fork` flip is a fleet risk CORE is exempt from, not immune to.** The AMAA peer
  reports 26 of 27 of its skills carry `context: fork` with no `background:`, so all 26 silently
  became fire-and-forget while their bodies are written synchronously — the caller never sees the
  result, and there is no error. CORE is clean AND does not teach the pattern (✓ verified: the
  only hit in the whole repo is this card). Detection anywhere, one line:
  `grep -c '^context: fork$' skills/*/SKILL.md`.

### ⛔ R42.8 IS NOT RATIFIED — discovered 2026-08-07, and it is bigger than this card

A peer session challenged my citation of R42.8 as law. It was right. ✓ VERIFIED first-hand:

- **`Emasoft/ai-maestro#125` is OPEN**, created 2026-08-05T18:27:24Z, never closed, and titled
  *"R42 amendment **request** (MAESTRO): grant MANAGER and CHIEF-OF-STAFF cross-agent terminal
  read/write…"*. A **pending request**, not a USER grant.
- **`GOVERNANCE-RULES.md` tops out at R42.7 — R42.8 is ABSENT.** (My mirror is stale, so absence
  alone is weak; combined with an OPEN issue that calls itself a request, the burden is on
  proving ratification, not assuming it.)
- **CORE asserts R42.8 as granted in 6 files**: `skills/ama-unblock/SKILL.md`,
  `skills/ama-session/SKILL.md`, `skills/ama-session/references/session-reference.md`,
  `skills/ama-panel/SKILL.md`, `design/tasks/…ZNGTF0FG…md`, and this card.

**How the error compounded:** I cited `#125` as the authority for R42.8 to **three** peer
role-plugin sessions. Anyone who followed my own citation would have found it says *request* and
is *open* — the citation I offered as proof is the thing that disproves the claim. I passed on a
provenance I had not read.

**Contained by luck, not by process:** `ama-unblock` is **not on the remote** (21 local commits
unpushed), so nothing built on R42.8 has shipped to a consumer. The live blast radius was the
three peers, now corrected.

**Required:** either the USER confirms a grant happened outside #125, or every one of the 6
assertions above must be re-worded from "granted" to "requested, pending". Until then **R42.8
must not be taught as law**. Tracked as its own task; owning card is TRDD-ZNGTF0FG.

### SUPERSEDED — do NOT carry forward

- **"R42.8 — USER grant 2026-08-05, ai-maestro#125."** NOT ESTABLISHED. #125 is an OPEN
  amendment **request**; R42.8 does not appear in the governance rules file. Relayed to three
  peers as law before it was checked.

- **"Cross-session `SendMessage` is new in 2.1.224."** FALSE — it predates R42.8 by months
  (`2.1.77`, `2.1.162`). 2.1.224 added cross-**machine** reach, `ListAgents` discovery, and the
  two settings.
- **"The platform shipped an ungated channel underneath R42.8."** FALSE and the more damaging
  error — `2.1.166` removed user authority from relayed messages and made receivers refuse
  relayed permission requests; `2.1.222` added permission-classifier evaluation before dispatch.
  The authority-laundering failure mode is **already defended**. Anyone reading this card for a
  ban recommendation is reading a superseded claim.
- **The version discrepancy on the `context: fork` flip is RESOLVED: 2.1.218.** Confirmed
  first-hand in the changelog's own 2.1.218 block, not by accepting the peer's concession. Its
  neighbours in that block (agent names rejecting `:`, the ISO `modified` memory field) confirm
  placement. All other attributions in this card verified against the same source: `DirectoryAdded`
  = 2.1.219 ✓, depth-3 = 2.1.219 ✓, concurrency cap 20 = **2.1.217** ✓, 200-spawn-cap removal =
  2.1.224 ✓, `archive` source = 2.1.224 ✓.

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
