# Reading a blocked state — the two verbs, the host caveat, the failure table

## Contents

- [The two read verbs are NOT alternatives](#the-two-read-verbs-are-not-alternatives)
- [Three measured facts every consumer must know](#three-measured-facts-every-consumer-must-know)
- [HOST CAVEAT — the terminal read is tmux-backed](#host-caveat--the-terminal-read-is-tmux-backed)
- [Error handling](#error-handling)

## The two read verbs are NOT alternatives

- **`read-prompt <agent>`** returns what the plugin **HOOK recorded** — so what
  it can tell you depends on the target's installed plugin version, which is why
  every state record now carries `writerVersion`. On versions **before** the
  `#59` fix it carried permission prompts but carried AskUserQuestion **never**
  (measured 0/419 question texts across live chat-state files): for the one
  prompt shape that blocks an agent forever it answered `null` and the agent
  looked fine. **On the fixed version it carries the question text, its
  normalized `{key,label}` choices, and `questionCount`.** Check
  `writerVersion` before reading a `null` as either answer.
- **`block-state <agent>`** reads the **TERMINAL** — the only source that
  reflects the screen *now*. Returns the structured verdict:

  ```json
  { "blocked": true, "reason": "ask_user",
    "field":   { "visible": true, "empty": true, "text": "" },
    "choices": [ { "key": "1", "label": "…" } ],
    "excerpt": [ "…the question, verbatim…" ],
    "hookDisagreed": false, "sessionName": "…" }
  ```

  `reason ∈ ask_user | permission | rate_limited | api_error | idle |
  active | unknown`. `--match "<regex>"` searches the pane **server-side**
  (only matching lines cross the boundary; requires the agent to be blocked).

Use both: the hook record is the fast hint, the pane verdict is the
**authority**, and `hookDisagreed: true` means exactly that — resolve toward
the pane. (Pre-`#59` versions mislabelled a live AskUserQuestion as
`permission_prompt`; fixed versions classify it `question`. Either way the pane
wins — that a record CAN be wrong in a way only the screen contradicts is the
reason the disagreement signal exists.)

## Three measured facts every consumer must know

From `ai-maestro-plugin#58` / `#59`:

- **`status` cannot discriminate blocked from idle** — a blocked agent and a
  healthy idle one both read `waiting_for_input`. The discriminator is
  **`notificationType`**, not `status`. The BLOCKED values are
  **`question`** (an AskUserQuestion — emitted only by versions carrying the
  `#59` fix), **`permission_prompt`**, and **`elicitation_dialog`** (an MCP
  server's elicitation). The not-blocked value is `idle_prompt`. Match that
  exact spelling: `elicitation_dialog` is what the hook writes, and a filter
  looking for `elicitation_prompt` matches nothing, so an agent stalled on an
  MCP dialog is silently classified healthy. Treat an UNKNOWN
  `notificationType` as possibly-blocked and fall through to `block-state`,
  never as not-blocked.
- **Chat-state goes stale on exactly the agents that matter** — the hook
  writes on events and a blocked agent generates none (~17 h observed). So
  `updatedAt` is NOT a liveness signal, and "no recent event" is
  indistinguishable from "healthy" from the file alone.
- **`field`** (`visible`/`empty`/`text`) is how "the input field is clear"
  is checked on the ai-maestro channel — never by eyeballing a pane dump.

## HOST CAVEAT — the terminal read is tmux-backed

**The pane path assumes the target runs under tmux.** The CLI's own help describes
`state --pane` as "live **tmux** pane status", and `block-state` / `--match` read that same
pane server-side. (✓ verified from the CLI help; the failure mode for a non-tmux host is
INFERRED from that, not yet measured against a live iTerm-hosted agent — measure before
asserting it to anyone.)

Why it matters: an agent running in a bare **iTerm** pane may be unreadable by
`block-state`, and the janitor's global daemon separately cannot rescue iTerm panes at all
without a macOS Automation (Apple Events) grant — which on some hosts will not persist.
**Both rescue paths can therefore be unavailable at once, for the same agent, silently.**
That is the worst shape this capability can take: a MANAGER runs `block-state`, learns
nothing, and a stalled agent looks fine — the exact "blocked forever" the exception exists
to prevent.

**Operational consequence: run fleet agents under tmux.** The guardian rescues tmux panes
with no Automation grant at all. If you find an agent you cannot read, check how it is
hosted BEFORE concluding it is healthy — and report `unknown_blocked` with that fact rather
than silence. Never fall back to driving an iTerm pane by another route; the prohibition is
about the ROUTE, and it does not relax because the sanctioned one is unavailable.

## Error handling

| Symptom | Meaning |
|---|---|
| `block-state`: unknown command | interim mode — this server predates the capability; escalate-only |
| 403 on `block-state` / `read-prompt` / `answer` | title matrix failed — you are not MANAGER/COS, the target is out of your scope, or it is an ASSISTANT; the refusal is the check |
| 409 on `answer` / `--match` | the target is not actually blocked (constraint (a) / Gate 0b) — re-read `block-state`; if it says blocked and the server says 409, report the disagreement upstream, do not force |
| `read-prompt` returns null but the pane shows a menu | check `writerVersion`: on pre-`#59` versions this is the known capture gap and the `block-state` excerpt/choices are the readable copy. On a fixed version a null is REAL — do not dismiss it as the old gap |
| `read-prompt` shows choices but `questionCount` > 1 | `options`/`message` describe the FIRST question only; answering by key sends that keystroke to whichever question the terminal has focused. Read the full `questions` array, or escalate |
| target resumed but did the wrong thing | your NOTIFY message is how it finds out and corrects — send it, then follow up via AMP |
