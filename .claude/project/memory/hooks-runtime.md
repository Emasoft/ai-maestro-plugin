---
name: hooks-runtime
description: "directory guard returns allow or abstains / why does the PreToolUse guard emit nothing / permission prompts suppressed by our own hook / is it safe to return allow from our guard / does CORE ship any agents / sub agents do not inherit the memory contract / which hook events could CORE still adopt / how many hook events does Claude Code have / hook drops state after the next event / why did this agent stop / lastError missing / askuserquestion not captured in chat-state / blocked agent looks healthy"
ocd: 2026-08-05
lmd: 2026-09-04
metadata:
  node_type: memory
  type: project
  tier: component
  globs: ["scripts/**", ".claude-plugin/**"]
publish-globally: false
split-lineage: cc9840b5939c4effac960eb58cab1b1e
---

# hooks-runtime

CORE's hook-layer behaviour: the `directory-guard.cjs` PreToolUse abstain/allow/deny
contract, the `agents/` directory gap in the memory-contract claim, which of Claude
Code's 29 hook events CORE registers, and `ai-maestro-hook.cjs`'s state-carry fields.

^ATOM-KXTI-U3Q2 [desc:"the PreToolUse directory-guard ABSTAINS (emits nothing) wherever it has no jurisdiction; returning allow there is a permission bypass, not a no-op", keywords: directory_guard_returns_allow_or_abstains why_does_the_pretooluse_guard_emit_nothing permission_prompts_suppressed_by_our_own_hook non_agent_session_guard_behaviour is_it_safe_to_return_allow_from_our_guard, ocd: 2026-08-05, lmd: 2026-08-05]

`scripts/directory-guard.cjs` (PreToolUse, matcher `Bash|Write|Edit|NotebookEdit`) has exactly three
outcomes, and the third is load-bearing: **deny** where a sandboxed write escapes its root, **allow**
only where it affirmatively vouches for a write inside a resolved `AGENT_WORK_DIR`, and **abstain —
emit no stdout at all** on every path where it has no jurisdiction (an ordinary non-agent session, or
a tool outside the matcher).

`permissionDecision: "allow"` is NOT "step aside". It is an affirmative override that skips the
user's permission prompt AND their configured rules, so returning it from a no-jurisdiction path
silently auto-approves the four highest-risk tools for anyone who installs the plugin. That shipped
in 2.9.0–2.11.0 and was fixed in `0683e1b`; the guard reached that state by fixing an earlier
fail-CLOSED bug (#22, a deny that bricked every interactive session) and over-correcting straight to
allow, skipping abstain. Abstaining satisfies #22 equally well — it does not deny — without granting.

`tests/test_directory_guard_bash.py::test_non_agent_session_without_work_dir_abstains_instead_of_allowing`
requires EMPTY stdout and names `allow` explicitly in its failure message, so a future
over-correction fails loudly instead of passing as "not denied".


^ATOM-2JGQ-JEAV [desc:"CLAUDE.md claims the memory contract is repeated in each agents/ prompt, but CORE ships no agents at all — the stated safeguard does not exist", keywords: claude_md_says_agents_prompts_repeat_the_memory_contract does_core_ship_any_agents where_are_the_agent_prompts sub_agents_do_not_inherit_the_memory_contract agents_directory_missing, ocd: 2026-08-05, lmd: 2026-08-05]

`CLAUDE.md` (the PROACTIVE MEMORY CONTRACT section) states the contract "is repeated in each
`agents/` prompt for that reason", justifying it with "sub-agents inherit nothing". **CORE ships
zero agents**: there is no `agents/` directory, `plugin.json` has no `agents` key, and the only
files matching `*agent*` are SKILLS *about* agents (`agent-identity`, `agent-messaging`,
`ai-maestro-agents-management`, `agent-repo-workflow`).

So the safeguard the sentence promises is absent — any sub-agent CORE spawns receives no memory
contract, while the file asserts otherwise. Verified 2026-08-05. Left unfixed deliberately:
`CLAUDE.md` is the owner's instruction file, and the fix is a judgement call between dropping the
clause and actually adding the agent prompts it promises.

Related: `tests/test_claude_code_platform_contracts.py::test_no_agent_name_contains_a_colon` scans
`agents/` and therefore currently proves nothing (it guards `if ... .is_dir() else []`). That is
correct behaviour for an optional directory, not a broken glob — but it means the 2.1.218 colon
rule has no live coverage here.


^ATOM-N3UF-12WL [desc:"CORE registers 12 of Claude Code's 29 hook events; TeammateIdle is the one with a real AMP fit, deliberately NOT adopted pending a decision", keywords: which_hook_events_could_core_still_adopt teammate_idle_hook_for_amp_inbox how_many_hook_events_does_claude_code_have should_core_register_more_hooks unused_hook_events, ocd: 2026-08-05, lmd: 2026-08-05]

Claude Code 2.1.222 dispatches **29** hook events; CORE registers **12**, all valid (locked by
`test_every_registered_hook_event_is_one_claude_code_actually_dispatches`, commit `61db3f6`). The
authoritative list comes from the binary's own enum, not the docs:

    strings -a "$(readlink "$(command -v claude)")" | grep -A18 -x 'PreToolUse'

The 17 unregistered events are a DESIGN CHOICE, not a gap — each hook costs a process spawn per
occurrence. One is worth revisiting: **`TeammateIdle`**, which exposes `executeTeammateIdleHooks`
and the string "TeammateIdle hook prevented continuation", i.e. it can stop an idle teammate from
halting. That is a direct fit for AMP — an idle teammate could drain its inbox instead of stopping.

Deliberately NOT built (2026-08-05): adding it changes behaviour for every plugin inheriting CORE,
so it is a proposal awaiting the owner, not alignment work. Also unregistered and plausibly useful
later: `TaskCreated`/`TaskCompleted` (kanban), `DirectoryAdded`, `ConfigChange`.


^ATOM-TKLL-H9B7 [desc:"ai-maestro-hook writeState has two CARRY-THROUGH fields (subagentCount, lastError) — a write that omits one must preserve the prior value, or a later event silently erases state a supervisor needs", keywords: hook_drops_state_after_the_next_event why_did_this_agent_stop lastError_missing errorType_gone_a_second_later subagentCount_reset_to_zero_mid_fanout, ocd: 2026-08-06, lmd: 2026-08-06]

`writeState` in `scripts/ai-maestro-hook.cjs` has TWO carry-through fields, and both exist
because a later event silently erased state a supervisor needed: `subagentCount` (#17) and
`lastError` (#58 — `status:'error'` and `errorType` describe only the CURRENT event, so the next
event of any kind made "why did this agent stop" unanswerable; the terminal cannot answer it
either, being a live tail that a scrolled-off error has left). `lastError` carries its own `at` so
a consumer judges staleness instead of being told nothing happened. An explicit value always wins
over the carry, so a handler resets deliberately (`subagentCount: 0`, `lastError: null`). [^4]


^ATOM-VN4C-8QRP [desc:"a GENERIC hook notification must never overwrite a more SPECIFIC pending classification — Notification(permission_prompt) fires for AskUserQuestion too and used to clobber the captured question", keywords: askuserquestion_not_captured_in_chat-state read-prompt_returns_null_but_a_menu_is_on_screen notificationType_is_permission_prompt_for_a_question blocked_agent_looks_healthy question_text_never_recorded, ocd: 2026-08-06, lmd: 2026-08-06]

The `Notification(permission_prompt)` handler must NOT clobber a pending `AskUserQuestion`.
Claude Code emits that notification for question blocks too, and the handler used to rebuild
state from a whitelist keeping only a recent `permission_request` — dropping `questions` and
downgrading `notificationType` from `question` to `permission_prompt` about a second after
`PreToolUse` had captured it. Measured server-side: question text captured **0 of 419** live
state files, so `read-prompt` answered `null` for the one prompt shape that blocks an agent
forever and a stalled agent read as healthy (#59). The invariant: **a GENERIC notification never
overwrites a more SPECIFIC classification that is still pending.** That carry-through takes **no
age bound** — `PostToolUse` is what ends the state, and a blocked agent stays blocked for hours
(17h observed), so any window would re-drop the question in exactly the case it exists for.

## Governed by
- [[architecture]] — the functionality hub this component sits under (its `## Applies to`
  carries the reciprocal link).

## Notes and lessons learned
[^4]: [id:ATOM-IW75-RF2M, status:valid, desc:"writerVersion must come from __dirname, never $CLAUDE_PLUGIN_ROOT — a wrong stamp is worse than none (#60, 2026-08-06)", keywords:"plugin_version_stamp_on_chat-state writerVersion_field CLAUDE_PLUGIN_ROOT_wrong_plugin_version how_does_the_hook_know_its_own_version is_the_version_stamp_redundant stale_producer_detection", ocd:2026-08-06, lmd:2026-08-06] DO NOT resolve the plugin version (or any plugin-root path) inside `scripts/ai-maestro-hook.cjs` from `$CLAUDE_PLUGIN_ROOT`, and DO NOT drop the `writerVersion` stamp as redundant. BECAUSE that env var names whichever plugin's context spawned the hook process, not this plugin, so it can stamp ANOTHER plugin's version onto our state record — and a wrong stamp is worse than none, since `writerVersion` is the one field a fleet consumer trusts to decide the producer is current (it is what lets the server distinguish 'no question pending' from 'this agent still runs the #59 clobber bug', which demand opposite actions). DO resolve from `__dirname`, whose value is the file's own location and cannot be wrong; the regression test passes with `CLAUDE_PLUGIN_ROOT` deliberately pointed elsewhere, so keep it that way.
