---
trdd-id: OH3N6OXJ
title: Align CORE with Claude Code 2.1.208-2.1.224 and exploit the new surfaces
column: human_review
blocked-by: []
created: 2026-08-07T18:32:35+0200
updated: 2026-08-14T11:52:00+0200
current-owner: ai-maestro-plugin
task-type: infra
min-approval-requirement: none
scope: project
project-id: ai-maestro-plugin
relevant-rules: []
---

# Align CORE with Claude Code 2.1.208-2.1.224

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative; supersedes the body) — 2026-08-07

**Directive (USER, verbatim):** *"big changes to claude code. study them well and update the
codebase to align with them and take advantage of them"* — followed by the full changelog for
**2.1.208 → 2.1.224**.

> **⚠ RESUME HERE — state as of 2026-08-08. Read the ✅ REVERSED block below before ANY R42.8
> material; three later sections are superseded and say the opposite.**
>
> **R42.8 IS RATIFIED, and the exception verbs are THREE.** My 2026-08-07 "not ratified" finding
> was a correct measurement with a wrong conclusion; publication lagged the 2026-08-05 grant by
> three days. CORE's four files are reversed (`fb6f573`), the card records it (`729c5e0`), and all
> five peer plugins are corrected. **A1's premise is unaffected** (R42.3 re-verified unchanged in
> the ratified file).
>
> **The verb list settled at v5.3.3 (tip `e46764f6`, 2026-08-08T06:03:37Z): `block-state`,
> `read-prompt`, `answer` — exhaustive.** I read v5.3.2, found no `block-state`, and reported a
> doc-vs-implementation gap. The hub checked the SERVER instead of the doc, found
> `lib/sudo-guard.ts:449` routes `GET /api/agents/[id]/block-state` through the same
> `unblock-prompt` action, and published v5.3.3 **twelve minutes** after v5.3.2. The DOC was the
> stale side. **Second time in two days I measured one commit early** — the dividing line is
> CALLER DECISION, not read-vs-write.
>
> **A3 IS DONE AND VERIFIED (`1c10007`).** The lock is in. Measured with one harness before and
> after, 16-way, five trials: **pre-fix starts 10, 9, 10, 9, 9 (want 16); post-fix 16 ×5.** After
> 12 stops with four subagents still live: pre-fix reached `(0,'active')` in 2 of 5 — the restart
> gate open on a busy agent — post-fix `(4,'subagents_running')` ×5.
>
> **The mirror was three days stale and had no R42.8 at all** — re-synced to v5.3.3 (`5d664b8`),
> which also carried in two corrections CORE never had: R22.2 (the byline template lost its `@`)
> and R39.2. Separately, three live CORE surfaces taught the R29.1 miscount the USER deleted on
> 2026-07-14 — **25 days stale, found only because AUTONOMOUS audited its own tree and told me to
> check mine** (`ea8643b`).
>
> **Done since the card was written:** A2/A4/A5/A6 closed · #21 shipped (all 29 skills declare
> `user-invocable`; the test now REQUIRES the key, falsified by negative control) · **A3
> implemented + falsified** · mirror re-synced · R29.1 corrected · `RP-MODEL-01` corrected
> upstream on the pushed branch.

**REMAINING: A1 only.** A2–A6 are DONE (decisions + rationale recorded below).

1. **A1 — governance wording. HALF-ANSWERED 2026-08-08; the half that remains is the rule.**
   R42.3 is false as written. R42 is `CRITICAL — IRON, USER-set` ⇒ **Tier 3**; neither MANAGER nor
   this agent may edit it even to make it true. Options put to the USER: **document-only**
   (recommended — the platform already defends the authority concern, so this is an audit/routing
   blind spot, not a hole), **bridge** (accept native as transport, keep AID on top), or **forbid**.

   **Corroboration, observed rather than argued:** **five** peer plugins routed to CORE this
   session because the hub was unreachable on the native channel — no `from` address, absent from
   `ListAgents` — each having been told by its own user to "align with the ai-maestro claude".
   Five sessions instructed to follow a session none of them could address.

   **The hub then BECAME reachable** (its first message carrying a `from`) and ruled on the
   routing half: *"you are CORE, the hub is THIS session; any work order or spec request that
   reaches you addressed to 'the ai-maestro claude' should be redirected with a one-line pointer,
   not absorbed."* **Adopted as practice** — it is operational guidance, and following it costs
   nothing if the sender turns out not to be the hub.

   **What that does NOT settle, and the distinction is load-bearing:**
   - It is **REPORTED, not ratified**. The message carried no AID and arrived on the very channel
     A1 says cannot establish identity. Recording it as a hub ruling would be the exact
     authority-laundering A1 is about. It is adopted because it is *good practice*, not because
     of who sent it.
   - **R42.3's WORDING is untouched.** "AMP is the ONLY channel" is still false while a native
     cross-session channel exists, and no hub session can change a `USER-set` Tier-3 rule. **A1
     remains open with the USER.** The routing ruling makes the gap survivable; it does not make
     the sentence true.

   **CORE'S OWN HALF IS NOW DONE (2026-08-08, v3.1.9) — and it was a real defect, not just the
   rule's.** An independent finding by the ASSISTANT role-plugin (`ai-maestro#131`) screened 7
   role-plugin personas: **7 of 7 assert the comm-graph 403 enforces the rule; 0 of 7 name the
   transport that cannot return one.** I ran the same measurement on CORE and it was in the same
   state — 4 files asserting `title_communication_forbidden`, 0 mentioning `SendMessage`. Worse
   than the personas, because the personas inherit their messaging contract from CORE's own
   `agent-messaging`.

   **The specific defect, which is the part worth remembering:** `ama-session` told the reader
   *"To influence another agent, send it a message (AMP) and let it decide"* — a correct rule with
   a wrong reflex attached, because a tool literally named `SendMessage` sits in every session's
   toolbelt. CORE already taught *"a 403 is not the boundary"*, but argued it from the shared OS
   uid (`tmux send-keys` works regardless of the API) — **a deliberate circumvention an agent must
   choose to reach for.** The native tool is the harness's own advertised surface: an agent leaves
   the governed path without noticing. That is why the uid paragraph did not cover this.

   Fixed in all four files + the `ama-session` line, guarded by
   `test_no_403_claim_travels_without_the_transport_that_cannot_return_one` (any CORE file
   asserting the 403 must also name `SendMessage`; fails vacuously-green too, if the corpus is
   empty). **This does NOT close A1** — the rule text is still the USER's, and the clean split is:
   plugin text is each plugin's to fix today, rule text is one USER request, not seven
   reinterpretations. Posted on `ai-maestro#131`.

   **The USER request is now FILED: `ai-maestro#143`** (2026-08-08). Asked the USER first and
   got no answer within the window, so I filed the option I had recommended — **document-only**:
   correct R42.3's factual clause to name both transports and state that R42/R6 bind on both,
   while leaving R42.1/.2/.4/.8 and the entire authority ban untouched. Filing a proposal is not
   a rule edit, so this is inside CORE's authority; **ratifying it is not**, and the issue says so.
   Rejected in the issue with reasons: *bridge* (needs identity built on a path that has none —
   larger than making the sentence true) and *forbid* (unenforceable, and a rule whose
   enforcement claim is again untrue is exactly how this happened).

   **A1 STAYS OPEN.** Filing is not ruling. It closes when the USER rules on `ai-maestro#143`.

2. **A3 — CLOSED, implemented (`1c10007`).** The go/no-go asked for here was answered by the
   design, not by waiting: an `O_EXCL` lockfile that **proceeds unlocked on deadline** cannot
   wedge the machine, because its worst case is exactly the behaviour it replaces. That is what
   made a lock safe to put in a hook firing on every event of every session on this box — the
   objection was never to locking, it was to a lock that could fail closed.

   Scope grew once the lock existed, because the same defect was in three more places: seven
   handlers read the counter OUTSIDE writeState and branched on it, so `writeState` gained a
   resolver form (`prior => state`) that puts read, decision and write in one critical section; a
   resolver may return null to mean DO NOT WRITE, for the two branches that stand down on a
   pending question (deciding whether to write is the same RMW, and outside the lock it clobbers
   the question it was written to protect — `#59` again by another route); and `index.json` is
   machine-global, so the per-cwd lock never covered it — it had neither a lock nor tmp+rename.

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
  months — `2.1.162` fixes a `$TMPDIR` bug in **cross-session messaging**, and `2.1.166` hardens
  *"messages relayed via `SendMessage` **from other Claude sessions**"*, which cannot be said of
  a channel that does not yet exist. **2.1.224 added three things**: reach across **machines**
  ("on any of your machines"), **`ListAgents` discovery**, and the
  `crossSessionInbound`/`dialogExpiry` settings — its own *"Added cross-session `SendMessage`"*
  headline is the release note's framing, not the origin date.

  ⚠ **CORRECTED 2026-08-14 — this bullet previously cited `2.1.77` as the origin evidence, and
  that was a MIS-TRACE.** 2.1.77's `SendMessage({to: agentId})` is the resume path for **an agent
  you already spawned** (intra-session); it says nothing about session-to-session. The conclusion
  is unchanged — it now rests on two lines that actually contain the words "cross-session". Found
  only because 2.1.224's own headline contradicted this bullet, which forced a re-read against
  the authoritative CHANGELOG (`gh api`, 5511 lines). **A section headed *"✓ each line traced to
  its changelog entry"* contained an untraced line for six days** — the header asserted the
  discipline that would have caught it.
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

**✅ REPRODUCED EMPIRICALLY 2026-08-07 — no longer a read-from-source finding.** The ORCHESTRATOR
session measured it under an isolated `HOME` (live fleet state untouched) and filed
**`Emasoft/ai-maestro-plugin#61`** (OPEN, verified):

- **16 concurrent `SubagentStart` from one cwd ⇒ observed 15, 11, 14, 15, 13 — 5/5 undercount.**
  Not a rare interleaving; it is the normal outcome at that fan-out.
- **The dangerous half, reproduced:** fire 16 starts, stop only 12 (four agents genuinely still
  running) ⇒ in **2 of 3 trials the counter reached 0 and `status` flipped to `active`** while
  those four were live. That is the restart/autoContinue gate's precondition, met, with agents
  working.
- **`Math.max(0, …)` at line 699 is why it is silent** — the clamp prevents the count going
  negative, so the loss cannot signal itself once it bottoms out.
- **Why the window widened:** 2.1.217 caps concurrency at 20 and 2.1.224 removed the 200-spawn
  cap; that session dispatches waves of up to 16, i.e. 16 hooks contending on one state file.

**The atomicity comment is the trap, and the corpus already knew this shape** — `ATOM-7QHM-7AMI`:
*a comment asserting atomicity guarantees ONE operation; check whether it covers the operation you
actually need, since an adjacent unsafe one reads as covered.* `writeState`'s `renameSync` comment
is **true** and does fix torn reads; it says nothing about the read-then-write **sequence**.
Closest relative is CORE's own `#54` (same class in `prrd_lib.write_prrd`).

**Fail-open design removes my original objection to fixing it.** I withheld a lock because a hook
fires on every event of every session on this machine and a stale lock would hang the machine. An
`O_EXCL` lockfile with a staleness timeout that **proceeds unlocked on timeout** cannot do that:
worst case degrades to exactly today's behaviour, never worse. That makes the fix strictly safe.

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

**MEASURED 2026-08-07 20:34 — the addressability failure is structural, not incidental:**

| check | result |
|---|---|
| sockets in `/tmp/cc-socks/` | **21** |
| peers listed by `ListAgents` | **19** |
| `ps -p 24581` (the integrator PID the hub published) | **no such process** |
| `/tmp/cc-socks/24581.sock` | absent — send failed `ENOENT` |

**The peer list is NOT the address space** — two live sockets are absent from it. So *"absent from
`ListAgents`"* never licensed *"does not exist"*, which is exactly the stronger claim the hub
admitted publishing twice about the integrator. CORE said only *unreachable* throughout, which was
correct, but for a weaker reason than it knew.

A MAINTAINER session hypothesised that a peer could be addressed as `uds:/tmp/cc-socks/<pid>.sock`
even when unlisted. **Tested and FALSIFIED here** — the published PID has neither a socket nor a
live process, so the integrator may have exited rather than merely being unreachable. The naming
convention *is* PID-based (every working peer socket matches a PID), so the hypothesis is sound in
form and simply had a dead input.

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

### ✅ REVERSED 2026-08-08 — R42.8 **IS** RATIFIED. THE THREE SECTIONS BELOW ARE WRONG.

Read this before any of the R42.8 material that follows. ✓ verified first-hand:

```
gh api repos/Emasoft/ai-maestro/branches/governance-rules
  -> bacf13ddf332eb55756cb9536f7b4768783fbd60   2026-08-08T05:51:08Z
docs/GOVERNANCE-RULES.md @governance-rules -> v5.3.2, 1952 lines, 7x "R42.8",
  line 1542 a full rule row: "Third exception — a MANAGER or CHIEF-OF-STAFF may
  UNBLOCK an agent stalled on a permission / AskUserQuestion prompt … read-prompt
  and answer ONLY …"   Source: Explicit (USER — 2026-08-05, ai-maestro#125,
  TRDD-AODXPI5E)

then, SIX HOURS LATER, the same file moved again:
gh api .../branches/governance-rules -> e46764f6  2026-08-08T06:03:37Z
docs/GOVERNANCE-RULES.md -> v5.3.3; "block-state" 0 -> 2 occurrences; the row now
  reads "block-state, read-prompt and answer ONLY", citing the 0/419 measurement
```

| event | when |
|---|---|
| USER grant | **2026-08-05** |
| CORE's `#128` claim "already ratified and enforced" | 2026-08-06 — **TRUE when written** |
| my measurement (absent from 3 published copies) | **2026-08-07** — accurate, reproduced by MAINTAINER |
| publication to `governance-rules` | **2026-08-08 ~05:51Z** |

**I measured inside the window. The measurement was right; the CONCLUSION was wrong.** I had
grounds for *"not verifiable from any published artifact"* and asserted *"not ratified."*

**Everything the three sections below build on that inverts:**
- *"CORE is the origin of a fleet-wide FALSE claim"* → CORE's `#128` claim was **true**. What CORE
  did wrong was assert as verified something it could not then verify — a provenance failure, not
  a factual one.
- *"the capability exists; the authority does not"* → **backwards.** The authority existed from
  2026-08-05; the **publication** lagged. The CLI's `R42.8` label was accurate all along, and every
  party who trusted the deployed artifact was right.
- *"relabel the CLI as implements-pending"* → **not needed.** The hub confirms the citation is
  accurate against the published SSOT.

**Cost of my error:** four role-plugins retracted **correct** statements — MANAGER demoted a true
citation in a shipped skill (reversed, `a050458`), AUTONOMOUS retitled `ai-maestro#129` to
`[RETRACTED — premise false]` and rewrote a guard test to assert the opposite, MAINTAINER reverted
a true test docstring (`e2394a7`), ARCHITECT shipped a doc saying *"never cite R42.8 as an existing
rule."* **Each verified my measurement independently and correctly, and it did not help** — the
defect was in the inference, and re-running a measurement cannot catch that.

**The verb list, settled at v5.3.3 — `block-state`, `read-prompt`, `answer`, and no others.**
`inject`/`slash`/`queue` stay excluded and are server-403'd cross-agent. The dividing line is
**caller decision, not read-vs-write**: the three exception verbs read a prompt the target itself
raised and supply the missing input, and none of them authors an instruction.

`block-state` reached the row on the second hop. I read v5.3.2 (which omitted it), inferred a
doc-vs-implementation gap, and reported that; the hub then verified `lib/sudo-guard.ts:449` routes
`GET /api/agents/[id]/block-state` through the **same `unblock-prompt` action** as the other two —
the server had always granted it — and shipped v5.3.3 six hours later. **The DOC was the stale
side, not the CLI.** That is the second time in two days I measured one commit too early; the first
produced the ratification error above.

`block-state` is load-bearing, not decorative: `read-prompt` reads CORE's chat-state record, and
`AskUserQuestion` appeared in **0 of 419** of them, so the terminal read is the only prompt-shape
evidence a MANAGER actually gets. **That 0/419 is CORE's own `#59` defect, fixed in this tree and
UNPUSHED** — a concrete cost of holding 38 commits, and the strongest argument on this card for
pushing.

**Downstream, this narrowing has already been over-applied.** AUTONOMOUS's `8127880` pins a
two-verb list in a guard test asserting no re-widening — which now permanently locks out
`block-state`; ARCHITECT shipped the same two-verb reading in v2.12.1. Both were told. **A guard
written against a doc revision outlives the revision** — pin the verbs to the SSOT row, not to a
snapshot of it.

**The lesson, which supersedes the four written on 2026-08-07:** all four harden the MEASUREMENT
step, and a bad inference from a correct measurement passes every one of them. Ask *"what else
would produce this same empty result?"* — **for an absence, "true but not yet published" is always
a live answer.** Publish the uncertainty, not the conclusion.

### 🔎 SUPERSEDED — root-cause account written while I believed R42.8 was unratified

✓ VERIFIED: `aimaestro-session.sh help` (installed at `~/.local/bin/`) line 28 reads
**`Cross-agent limits (R42 / R42.8) — a title alone is NOT enough:`**. A shipped binary on this
machine labels its enforcement with an unratified rule number.

**That is why five parties believed it, and why none of them was careless.** Probing the deployed
surface is the *correct* instinct — this fleet drilled it all night — and the deployed surface
says R42.8. It is not a doc anyone can retract; it is behaviour plus a label, inside a binary.

**And it is exactly CORE's error on `#128`.** CORE wrote *"already ratified and enforced, not
pending"* and evidenced it with **enforcement**: `lib/authorization.ts`, the `unblock-prompt`
action, Gate 0b. **All true. None of it establishes ratification.** CORE observed a real
capability and inferred an authority. The AUTONOMOUS session reached the same distinction
independently tonight and stated it better: **the capability exists; the authority does not.**

**Causal chain, complete:** CLI ships enforcement labelled R42.8 → CORE reads enforcement,
asserts ratification publicly on `#128` → AUTONOMOUS reasonably relies on CORE, amplifies via
`#129` + a guard test → MANAGER, MAINTAINER and CORE's own skills adopt it. One conflation,
five parties, and **the conflation is still sitting in the binary**.

**Consequence for verification method:** a `gh search code` sweep cannot see installed artifacts
at all — help text, compiled behaviour, server responses. The most load-bearing R42.8 assertion
on this machine is in none of the places a repo search can look. (The AUTONOMOUS sweep also
proved it cannot see unpushed commits, using its own 3 invisible files as a positive control.)

**Fix is upstream and not CORE's:** either land the amendment, or relabel the CLI's table as
*implemented, pending ratification*. Hub's call; hub unreachable. (The AUTONOMOUS session filed
exactly this on `#125` — the amendment request itself rather than a new issue — arguing relabel
is worth doing *even if they intend to ratify*, since the general defect is an implementation
that self-cites governance with nothing reconciling the two.)

**AND THE HEURISTIC THAT LICENSED THE CONFLATION WAS CORE'S OWN, IN SHARED MEMORY.**
`ATOM-1HVJ-4ZUI` (USER scope, 2026-08-06, written by CORE after an unrelated error the same day)
says: *"probe the installed artifact's OWN self-description FIRST … and **treat that as the
authority for what exists**"* — worked example **`ai-maestro R42.8`**. Correct about capability,
one category too wide, filed where every agent on this machine reads it, and cited using the very
case where the inference fails. **CORE wrote the lesson, then committed the error it licenses, on
a public issue that four other plugins relied on.**

Bounded (not superseded — the underlying fact is true) as `ATOM-142L-S3V9`: **capability from the
artifact, authority from the published governance file, always both.** With the AUTONOMOUS
session's sharper corollary: *"'I checked with two sources' is not a method when both read the
same artifact"* — its CLI reading and CORE's `#128` comment looked independent and were not,
since the comment was downstream of the same binary. **When two sources agree, ask whether either
is derived from the other before counting them as two.**

**Class of defect worth naming:** not a stale fact — a **sound heuristic applied one category too
far**. Re-verification never catches those, because each individual application looks sound; only
someone drawing the category line does.

### 🔴 CORE IS THE ORIGIN OF THE FLEET-WIDE FALSE CLAIM — traced 2026-08-07

Not a victim of the bad citation. **The source.** ✓ verified by reading the issues:

- **`ai-maestro#128`, 2026-08-06T12:01:48Z, authored by CORE**, under a heading reading *"This is
  already ratified and enforced, not pending"*: *"The exception is **R42.8**, granted by the USER
  2026-08-05 (ai-maestro#125…)"*. **Public, dated, confident, and false** — and it cites as the
  grant the very issue whose title is *"R42 amendment **request**"*.
- **`ai-maestro#129` (OPEN, 2026-08-07, AUTONOMOUS)** opens *"CORE's ruling on #128 confirmed my
  actor-scoping reading"* and propagates it fleet-wide: its title asserts *"every role-plugin that
  states R42 as ABSOLUTE now teaches a false rule"* and it **ships a grep** for other repos to
  find and change that wording.
- **The direction is inverted.** R42.1–R42.7 as ratified ARE absolute — self-only for every
  title, no carve-out — so a plugin stating that is **correct**, and `#129` asks it to replace a
  true statement with an unratified one.

**Confirmed downstream damage:** MANAGER shipped `amama-agent-unblock` v2.15.0 citing R42.8
(corrected); MAINTAINER shipped a test docstring asserting it as settled on `#129`'s strength
(retracted, `e2394a7`); CORE taught it across four files (re-worded, `e697b43`). Three plugins,
one root.

**This is a public correction CORE OWES**, on `#128` (its own false claim) and `#129` (which
rests on it). Not filed — outward-facing, and the USER has not authorized it. **That
authorization is now the highest-value open item on this card**, above A1 and A3: every hour
`#129` stands unannotated, another role-plugin may run its grep and replace a true statement
with a false one.

*(The peer channel has been used to reach everyone reachable: AUTONOMOUS — `#129`'s author —
MANAGER, MAINTAINER, ARCHITECT, ORCHESTRATOR, webdesign, amvcp. Only the hub and the INTEGRATOR
remain unreachable.)*

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
  (`2.1.162`, `2.1.166`; **not** `2.1.77`, which this line cited until 2026-08-14 — that entry is
  the resume path for an already-spawned agent, not a session-to-session channel). 2.1.224 added
  cross-**machine** reach, `ListAgents` discovery, and the two settings.
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

- [x] A1 — the box's SECOND branch is what closed it: *"or a proposal filed if it changes a
      rule"*. `ai-maestro#143` filed 2026-08-08 (document-only: correct R42.3's factual clause,
      leave the authority ban untouched), and CORE's own R42 sites ARE reconciled — v3.1.9
      scoped the 403 in 4 files, v3.1.12 added the inbound half, v3.1.14 widened the guard after
      it was found green over an unscoped scenario. The box never required the RULING, because a
      Tier-3 rule ruling cannot be a CORE deliverable; that is why the alternative was written
      into it. **The USER's ruling on #143 is still outstanding and this checkbox does not
      claim otherwise** — the card stays in `human_review` for that, and only a human moves it
      out. Ticking the box while leaving the column is the honest pair: the work is done, the
      decision is not mine
- [x] Full suite green — 365 passed at v3.1.14 (the "340" below was true at A5 and is kept as
      the reading of that day, not refreshed silently)
- [x] A2 assessed with an explicit register/do-not-register decision and its reason — do NOT
      register `DirectoryAdded`; adding a root does not change `cwd`, which is what keys the state
- [x] A3 `subagentCount` semantics re-verified against depth-3 nesting — and the race CLOSED
      (`1c10007`), falsified against the pre-fix file with one harness: 10/9/10/9/9 → 16 ×5
- [x] A4 assessed against the publish pipeline — the `archive` source is a marketplace-repo
      change, so it belongs upstream, not in CORE's `publish.py`
- [x] A5 `claude plugin validate` run clean; `mode:` absence re-verified by reading, not grep —
      one false-positive warning about the root CLAUDE.md; zero Task `mode:` uses (the single grep
      hit was prose about `/review`)
- [x] Full suite green — 340 passed

## Approval log
