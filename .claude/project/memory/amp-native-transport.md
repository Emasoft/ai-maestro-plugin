---
name: amp-native-transport
description: "403 not returned / forbidden send no error / does SendMessage bypass the comm graph / is AMP the only channel / is the native transport enforcing R6 now / did my forbidden send get blocked / sendmessage returned refused / native send reported refused / is my agent's cross-session message policed / R42.3 wording unpoliced transport / cross machine send still unpoliced"
ocd: 2026-08-08
lmd: 2026-09-04
metadata:
  node_type: memory
  type: project
  tier: component
publish-globally: false
split-lineage: cc9840b5939c4effac960eb58cab1b1e
---

# amp-native-transport

Why a native cross-session `SendMessage`/`ListAgents` never returns a comm-graph 403,
and what a 2.1.238 `refused` reply does and does not prove about R6 enforcement.

^ATOM-P29X-WO6W [desc:"A comm-graph 403 is evidence about AMP only: native SendMessage reaches another session with no ai-maestro server in the path, so a forbidden send returns no error — reach spans machines, RC, cloud", keywords: 403_not_returned forbidden_send_no_error SendMessage_bypasses_the_comm_graph agent_messaged_another_agent_directly communication_graph_not_enforced ListAgents_cross-session AMP_is_the_only_channel_is_false R42.3_wording unpoliced_transport native_transport_is_not_local same_machine_claim_is_wrong cross_machine_send_still_unpoliced, ocd: 2026-08-08, lmd: 2026-08-14]

`SendMessage` / `ListAgents` are a native session-to-session transport between live Claude
Code sessions that **never reaches the ai-maestro server**. `validateMessageRoute()` is not
consulted, so a forbidden edge over that path returns **no** HTTP 403
`title_communication_forbidden`; nothing on it can.

**Its reach is not one machine**, and the precision matters: sessions on any of your
machines (2.1.224), Remote Control sessions by name (2.1.225) and cloud sessions
(`ListAgents` labels them since 2.1.229). What makes the 403 impossible is that the
**ai-maestro** server is absent from the path — NOT that the message stays local. A
cross-machine send plainly traverses something; it just traverses nothing that holds the
communication graph.

**A 403 you never received is not permission.** R6 and R42 bind an agent on both
transports; only AMP can tell it when it broke them. `amp-send.sh` is the verb that gets
signed, routed, graph-checked and recorded.

Measured 2026-08-08 (`ai-maestro#131`, filed by the ASSISTANT role-plugin): **7 of 7**
role-plugin personas asserted server enforcement, **0 of 7** named the transport. CORE was
in the same state — 4 files asserting the 403, 0 mentioning `SendMessage` — which was worse,
because those personas inherit their messaging contract from CORE's `agent-messaging`.

Fixed in CORE v3.1.9 across `agent-messaging` (SKILL + detailed-guide) and `team-governance`
(SKILL + REFERENCE), guarded by
`tests/test_claude_code_platform_contracts.py::test_no_403_claim_travels_without_the_transport_that_cannot_return_one`.

The rule-text half is NOT fixed and is not CORE's: R42.3 ("messaging is the ONLY channel")
is false as written, and R42 is `CRITICAL — IRON, USER-set` ⇒ Tier 3. Tracked as A1 of
`TRDD-OH3N6OXJ`, open with the USER. The clean split: plugin text is each plugin's to fix
today; rule text is ONE user request, not seven reinterpretations. [^5] [^6]

## Governed by
- [[architecture]] — the functionality hub this component sits under (its `## Applies to`
  carries the reciprocal link).

## Notes and lessons learned
[^5]: [id:ATOM-E7FC-E5XZ, status:valid, desc:"corrects this atom's pre-2026-08-14 body, which read 'between live Claude Code sessions on one machine that never reaches the ai-maestro server'", keywords:"native_transport_is_local no_server_in_the_path same_machine_claim cross-machine_send_is_still_unpoliced the_stated_reason_went_false_but_the_conclusion_held scoping_argument_built_on_the_wrong_premise", ocd:2026-08-14, lmd:2026-08-14] DO NOT justify "a native send returns no 403" by calling the transport LOCAL, or by saying it "never reaches the server" unqualified — this atom's own body did, reading "between live Claude Code sessions on one machine", and three CORE skills taught the same until 2026-08-14. BECAUSE the reach was never one machine (2.1.224 any of your machines, 2.1.225 Remote Control by name, 2.1.229 cloud sessions), so a cross-machine send plainly traverses infrastructure; a reader who catches that false premise can discard the TRUE conclusion along with it and route around the comm graph believing the doc is merely stale. A right conclusion resting on a checkable-false reason is more dangerous than a visibly wrong one. DO name WHICH server is absent — the ai-maestro one, the only one holding the communication graph — so the argument survives every future change in reach.
[^6]: [id: ATOM-U8NM-8NOS, status: valid, desc: "Claude Code 2.1.238 made a crossSessionInbound refusal visible to the sender; that is not the comm graph arriving on the native path", keywords: "sendmessage_returned_refused native_send_reported_refused is_the_native_transport_enforcing_R6_now crossSessionInbound_refuse_reports_to_sender 2.1.238_refusal_is_not_silent did_my_forbidden_send_get_blocked blanket_refusal_not_edge_aware silent_success_replaced_by_refused", ocd: 2026-08-22, lmd: 2026-08-22] DO NOT read a native cross-session `refused` as the communication graph enforcing R6, BECAUSE the refusal Claude Code 2.1.238 added is blanket — the `crossSessionInbound: "refuse"` that R42.9 writes into every agent workdir fires identically for a route R6 permits and one it forbids, so it reports a shut door and never a violated edge. DO keep every 403/R6 conclusion on the AMP path, and treat the native refusal only as evidence that the message did not land.
