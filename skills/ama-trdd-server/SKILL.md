---
name: ama-trdd-server
user-invocable: false
description: "Search, read, verify, and (server-mediated) mutate TRDDs through the aimaestro-trdd.sh CLI — the AI Maestro dashboard's authorization-aware view of the design/ corpus. Read verbs: search / read / verify (verify checks an approval's cryptographic authenticity). Write verbs (STRICT, governed by the manage-trdd AuthAction, agent acts with its own AID + title): edit / approve / refuse / promote / archive — each gated by the TRDD's own min-approval-requirement, with a hard self-approval ban and USER-only for user-tier cards. Use when server-mirrored state or server-side authorization matters — the dashboard's kanban view, approving a proposal, or confirming an approval is real. Trigger with /ama-trdd-server, 'approve this TRDD', 'search TRDDs on the dashboard', 'verify this TRDD's approval'. For local design/ file editing (still the source of truth) use ama-trdd-find/write/update/transition. Loaded by ai-maestro-plugin"
allowed-tools: "Bash(aimaestro-trdd.sh:*), Bash(jq:*), Read, Grep, Glob"
disallowed-tools: "Edit, Write, NotebookEdit"
metadata:
  author: "Emasoft"
  version: "1.1.0"
---

# ama-trdd-server — server-mediated TRDD search / read / verify / mutate

## Overview

`ama-trdd-server` wraps the frozen `aimaestro-trdd.sh` CLI (Tier A, §2.1 of
`SCRIPT-MANIFEST.md`): the **server-mediated** view of the 3-pillars task
system, backing the AI Maestro dashboard's kanban mirror. It carries both
the **read** surface (`search`, `read`, `verify`) and the **write** surface
(`edit`, `approve`, `refuse`, `promote`, `archive`) — the latter being the
server-side, authorization-checked, token-minting path.

**Local files remain the single source of truth.** TRDD files under
`design/` — searched/read/edited by `ama-trdd-find` / `ama-trdd-write` /
`ama-trdd-update` / `ama-trdd-transition` — are authoritative. The
dashboard and any GitHub Project board are **mirrors** of them, not a second
ledger. Use this skill when *server-mirrored* state or *server-side
authorization* specifically matters — approving a proposal so the server
mints a signed token, or what the dashboard shows — not to avoid opening a
file that is right there in your working tree. `aimaestro-trdd.sh` commits
nothing for you.

## The write verbs — authority is the load-bearing part

The write verbs `edit`, `approve`, `refuse`, `promote`, and `archive`
**work for agents as of commit `d7531e53` (`TRDD-K2WJH7RF`)**. They used to
403 every agent with `agent_policy_undefined`; that gap is closed. They are
now governed by the **`manage-trdd` AuthAction**, and the authority model
below is not optional flavor text — get it exactly right or an agent earns
a 403 (best case) or oversteps the governance graph (worst case).

**The seven rules that govern every write verb:**

1. **All five are STRICT verbs** governed by `manage-trdd`. An **agent**
   authenticates with its own **AID + governance title** (no sudo prompt);
   a **human** would need a fresh sudo token (but the human path 401s today
   — see the gap note below).
2. **The required tier is read from the TRDD's own
   `min-approval-requirement:`** field. The authority matrix mirrors the
   approval tiers: `none < orchestrator < chief-of-staff < manager < user`.
   Your title must **meet or exceed** the card's required tier.
3. **NO agent may approve a `user`-tier TRDD.** A `user`-tier card is
   USER-only; no agent token — MANAGER's included — can satisfy it.
4. **NO one may approve their OWN proposal — MANAGER included.** The
   self-approval ban is hard. The approver and the proposer must differ.
5. **Only invoke a verb you have authority for.** If the card's tier
   exceeds your title, do **not** call the verb — route it through your
   **CHIEF-OF-STAFF** (team-internal) or **MANAGER** per the approval
   tiers. A MEMBER never self-approves; it signals and lets the matrix
   Mover act.
6. **`approve` MINTS a signed approval token**; **`verify` reads it back**.
   The token is host-signed, R34-ledger-anchored, and PINNED to the card's
   identity. Keep using `verify` to confirm an approval is real — it reads
   the TOKEN, never the card's editable prose.
7. **`archive --state` refuses `failed`.** It accepts `completed`,
   `cancelled`, `superseded`. A failed TRDD is retryable and stays in
   `tasks/`; giving up on it is an explicit `cancel`, not an archive-as-failed.

Rules 3–5 are why this skill is authorization-aware and the local-file
skills are not: the server enforces the tier matrix; a raw file edit does
not. When the change is a plain frontmatter/body edit with no
authorization dimension, prefer the local-file skills; reach for these
server verbs when the tier matrix, the signed token, or the dashboard
mirror is the point.

## The write verbs — exact signatures (frozen, from SCRIPT-MANIFEST.md)

| Verb | Signature | Effect |
|---|---|---|
| `edit <id>` | `--set k=v` (repeatable) | mutate frontmatter **in place**, no folder move |
| `approve <id>` | `--approver W --tier N --rationale R` | proposal → planned; `git mv proposals/ → tasks/`; mints the signed token |
| `refuse <id>` | `--approver W --tier N --reason R` | → `refused/` |
| `promote <id> --column C` | `[--note N] [--approver W]` | advance the card in place to column `C` |
| `archive <id> --state S` | `[--reason R] [--superseded-by ID] [--approver W]` | `S` ∈ `completed \| cancelled \| superseded` — **refuses `failed`** |

`--approver W` names the approving authority; `--tier N` is the tier being
exercised (which must meet the card's `min-approval-requirement:`). Global
`--agent <uuid|name>` operates on that agent's `<workdir>/design` corpus.
Nothing is committed for you.

## The read verbs

### `search` / `read`

`search` filters the server's mirror; `read <id>` returns one card.
Both are non-strict.

### `verify` — is this card's approval REAL?

`verify <id> [--json]` answers **"is this card's approval authentic?"** by
checking the signed token — never the prose — and re-validates the
issuer's title, the R34 ledger anchor, and that the issuer's authority
meets the card's `min-approval-requirement:`. It mutates nothing:

| Exit code | Meaning |
|---|---|
| `0` | verified — the approval is authentic |
| `2` | **NOT verified** — the server checked and it failed |
| `1` | error (usage/transport/HTTP) — the verdict is *unknown*, not "no" |

Treat `1` and `2` differently: an unreachable verifier is not the same as a
forged approval. Never collapse them into a single boolean. (What `verify`
does NOT prove: the token binds an approval to the card's *identity*, not
its *content* — someone with repo write can edit the body after approval
and `verify` will still say the approval is authentic, because it is.)

## Prerequisites

- AI Maestro running; `aimaestro-trdd.sh` on `PATH` (installed by
  `install-messaging.sh`; re-run it if missing).
- The CLI resolves your agent identity + bearer token internally.
- `jq` for parsing JSON output.
- You know your own governance **title** — the write verbs' authority
  matrix is keyed on it, and you must self-check rule 5 before invoking one.
- For a plain local edit with no authorization dimension, prefer the
  local-file skills (`ama-trdd-find`, `-write`, `-update`, `-transition`).

## Instructions

1. **Search** the server's mirror, or **read** one card:

   ```bash
   aimaestro-trdd.sh search --column dev
   aimaestro-trdd.sh search --id 9a8aba94
   aimaestro-trdd.sh search --keyword "auth"
   aimaestro-trdd.sh search --zone proposals
   aimaestro-trdd.sh read 9a8aba94
   ```

2. Before ANY write verb, **read the card's `min-approval-requirement:`**
   and confirm YOUR title meets it (rule 2), that the card is not
   `user`-tier if you are an agent (rule 3), and that you are not the
   proposer (rule 4). If you lack the authority, STOP and route through
   COS/MANAGER (rule 5) — do not call the verb.

3. **Approve** a proposal (mints the signed token; moves `proposals/ →
   tasks/`):

   ```bash
   aimaestro-trdd.sh approve 9a8aba94 --approver <you> --tier <N> --rationale "meets the design spec"
   ```

4. **Refuse** a proposal (→ `refused/`):

   ```bash
   aimaestro-trdd.sh refuse 9a8aba94 --approver <you> --tier <N> --reason "duplicates TRDD-XXXX"
   ```

5. **Promote** a card to the next column in place:

   ```bash
   aimaestro-trdd.sh promote 9a8aba94 --column testing --approver <you> --note "gates green"
   ```

6. **Edit** frontmatter in place (no folder move):

   ```bash
   aimaestro-trdd.sh edit 9a8aba94 --set priority=1 --set assignee=alice
   ```

7. **Archive** a terminal card (never `failed`):

   ```bash
   aimaestro-trdd.sh archive 9a8aba94 --state completed --approver <you>
   aimaestro-trdd.sh archive 9a8aba94 --state superseded --superseded-by K3QX9P2W --approver <you>
   ```

8. **Verify** an approval is authentic (read-only, exit-code contract):

   ```bash
   aimaestro-trdd.sh verify 9a8aba94 --json
   ```

### Quick CLI Reference

| Subcommand | Flags | Class |
|---|---|---|
| `search` | `--column C`, `--id I`, `--keyword K`, `--zone proposals\|tasks\|archived\|refused` | read, non-strict |
| `read <id>` | — | read, non-strict |
| `verify <id>` | `--json` | read-only, non-strict, mutates nothing |
| `edit <id>` | `--set k=v` (repeatable) | **write, STRICT** |
| `approve <id>` | `--approver W` `--tier N` `--rationale R` | **write, STRICT** — mints token, `proposals/ → tasks/` |
| `refuse <id>` | `--approver W` `--tier N` `--reason R` | **write, STRICT** — `→ refused/` |
| `promote <id> --column C` | `--note N` `--approver W` | **write, STRICT** — advance in place |
| `archive <id> --state S` | `--reason R` `--superseded-by ID` `--approver W` | **write, STRICT** — refuses `failed` |
| `--agent <uuid\|name>` (global) | — | operate on that agent's `<workdir>/design` corpus |

## Output

JSON or table text on STDOUT (pipe to `jq` for JSON); errors on STDERR with
a non-zero exit. `verify`'s exit code is the contract (0/2/1). `approve`
returns the minted token reference. Nothing is committed for you.

## Error Handling

| Symptom | Likely cause |
|---|---|
| 403 on a write verb | your title does not meet the card's `min-approval-requirement:` (rule 2), or it's a `user`-tier card and you're an agent (rule 3) — route through COS/MANAGER |
| 403 approving a card you authored | the self-approval ban (rule 4) — a different authority must approve it |
| `archive --state failed` rejected | expected — `failed` is retryable and stays in `tasks/`; use `cancelled` to give up (rule 7) |
| Card the local `design/` file shows isn't in server search | the dashboard mirror hasn't synced, or `--agent` targeted the wrong corpus |
| `verify` exits `1` | transport/usage error — verdict unknown, not "unverified" |
| `verify` exits `2` | the approval genuinely does not check out — do not trust the card's `## Approval log` prose over this |
| 401 from a human terminal | there is no USER auth path in the script layer yet (`Emasoft/ai-maestro#55`) — this skill is agent-facing |

## Examples

<example>
An ORCHESTRATOR approves a designed proposal whose `min-approval-requirement:`
is `orchestrator`.
→ First confirm the tier and that you are not the proposer, then
`aimaestro-trdd.sh approve 9a8aba94 --approver <self> --tier orchestrator --rationale "matches the accepted design"`.
The server mints the signed token and moves the file `proposals/ → tasks/`.
</example>

<example>
A MEMBER wants a proposal approved but the card is `manager`-tier.
→ The MEMBER does NOT call `approve` (rule 5). It routes the request through
its CHIEF-OF-STAFF to the MANAGER, who approves. A MEMBER never
self-approves.
</example>

<example>
Confirm a TRDD's approval is cryptographically real before relying on it.
→ `aimaestro-trdd.sh verify 9a8aba94 --json` — exit `0` verified, `2` not
verified, `1` could not ask (never treat `1` as "no").
</example>

<example>
Archive a superseded card.
→ `aimaestro-trdd.sh archive 9a8aba94 --state superseded --superseded-by K3QX9P2W --approver <self>`.
(`--state failed` would be rejected — a failed card stays open and retryable.)
</example>

## Scope

Server-mediated TRDD read (`search`/`read`/`verify`) **and** write
(`edit`/`approve`/`refuse`/`promote`/`archive`, STRICT, tier-gated). The
`disallowed-tools` line drops the Claude-Code-native Edit/Write/NotebookEdit
tools — this skill never hand-edits local files; all mutation flows through
the authorization-checked `aimaestro-trdd.sh` CLI. Local `design/` file
operations — find, author, edit fields, move columns without the server's
tier check — are `ama-trdd-find` / `ama-trdd-write` / `ama-trdd-update` /
`ama-trdd-transition`.

## Resources

- `${CLAUDE_PLUGIN_ROOT}/rules/trdd-design-tasks.md` — canonical TRDD v2
  format (auto-installed each session).
- `${CLAUDE_PLUGIN_ROOT}/rules/trdd-approval-tiers.md` — the four-tier
  approval ladder and `min-approval-requirement:` semantics the write
  verbs enforce (auto-installed each session).
- [../ama-trdd-transition/references/approval-tiers-and-zones.md](../ama-trdd-transition/references/approval-tiers-and-zones.md)
  — the four zones + tier ladder + objective tier-floor this skill's write
  verbs and `verify` are checked against.

## Use also

- `Skill(skill: "ama-trdd-find")` — find a TRDD in the local `design/`
  corpus (the source of truth).
- `Skill(skill: "ama-trdd-transition")` — move a TRDD between columns
  locally, with the full transition matrix (the local counterpart to
  `promote`).
- `Skill(skill: "ama-proposal-approvals")` — batch proposal approvals on
  local `design/` files.
- `Skill(skill: "team-kanban")` — the live team-coordination board (a
  different domain than the design/spec board this skill mirrors).
