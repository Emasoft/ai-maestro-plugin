---
name: ama-portfolio
user-invocable: false
description: "Mint, list, verify and revoke R28 approval and mandate tokens via the frozen aimaestro-portfolio.sh CLI — the machine-checkable answer to 'is this agent actually authorized to do this, for THIS card'. Use when granting a one-shot approval or a standing mandate, or before acting on a claimed authorization. Trigger with 'mint an approval token', 'does this agent have a mandate for X', 'verify this approval', 'revoke that token'. CRITICAL gotcha: verify has THREE exit codes — 0 VALID, 2 INVALID, 1 ERROR — and authorizing on anything but 0 turns a verifier outage into a verifier bypass. Loaded by ai-maestro-plugin"
allowed-tools: "Bash(aimaestro-portfolio.sh:*), Bash(aid-auth.sh:*), Bash(jq:*), Read, Grep, Glob"
metadata:
  author: "Emasoft"
  version: "1.0.0"
---

# ama-portfolio — R28 approval and mandate tokens

## Overview

`ama-portfolio` wraps the frozen `aimaestro-portfolio.sh` CLI: the surface that
turns "X approved this" from a claim in a comment into a **signed, ledger-anchored,
independently verifiable** fact. An **approval** is one-shot (≤ 1h); a **mandate**
is standing (≤ 30d). Tokens are minted INTO the subject agent's enclave, and can be
pinned to one TRDD, one agent, or one team.

It never calls the AI Maestro API directly — the CLI resolves the API base and the
caller's identity internally.

## THE GOTCHA — `verify` has THREE exit codes, and only `0` means authorized

```
0  VALID    signature, ledger anchor, issuer title, status, expiry ALL pass
            (and the token binds what you asked about)
2  INVALID  the server answered and the token does NOT verify
1  ERROR    usage, transport, or HTTP failure — the verdict is UNKNOWN
```

**Authorize on `0` and nothing else.** The failure mode this trichotomy exists to
prevent is treating "not INVALID" as good enough:

```bash
# WRONG — an outage (1) reads as authorized. This is a verifier BYPASS.
aimaestro-portfolio.sh verify --subject "$A" --token "$T"
[ $? -ne 2 ] && do_the_privileged_thing        # ← 1 slips through

# RIGHT — proceed only on 0, and say WHICH failure it was
aimaestro-portfolio.sh verify --subject "$A" --token "$T" --binds "$TRDD"; rc=$?
case $rc in
  0) do_the_privileged_thing ;;
  2) echo "REFUSED: token does not verify for $TRDD" >&2; exit 1 ;;
  *) echo "REFUSED: could not reach the verifier — verdict UNKNOWN" >&2; exit 1 ;;
esac
```

`2` and `1` both stop you, but they are **not** the same thing to report: `2` is a
bad token (a security event); `1` is a broken verifier (an availability event).
Collapsing them hides whichever one is actually happening.

## Ask the SPECIFIC question, not the general one

A token that is valid *in general* may not authorize *this* action. Pass the same
binding you care about to `verify`, so the CLI answers the question you actually
have:

```bash
# "Is there an approval for THIS card?" — not merely "is this token real?"
aimaestro-portfolio.sh verify --subject "$AGENT" --token "$T" --binds M7BZ4X1Q
aimaestro-portfolio.sh verify --subject "$AGENT" --token "$T" --scope trdd:approve
```

Verifying without the binding and then assuming it covers your case is how an
approval for one card silently authorizes another.

## Prerequisites

- AI Maestro running; `aimaestro-portfolio.sh` on `PATH` (installed by
  `install-messaging.sh`; re-run it if missing).
- **Agent callers must export `AID_AUTH`**: `export AID_AUTH="$(aid-auth.sh)"`.
  Without it the CLI has no caller identity and `mint`/`revoke` will fail.
- `jq` if you want to parse `--json` verdicts.

## Instructions

1. **Minting** — decide one-shot vs standing, and bind it as narrowly as the job
   allows. An unbound mandate is a standing grant over everything in scope:

   ```bash
   # one-shot, pinned to a single card, short TTL
   aimaestro-portfolio.sh mint --subject alice --kind approval \
     --scope trdd:approve --binds M7BZ4X1Q --ttl 900

   # standing, pinned to one team
   aimaestro-portfolio.sh mint --subject alice --kind mandate \
     --scope agent:create --binds-team backend --ttl 604800
   ```

   Ceilings are enforced: approval ≤ 1h, mandate ≤ 30d.

2. **Before acting on a claimed authorization**, verify it with the binding
   (see the gotcha above). Never take the claim from prose.
3. **Auditing** — `list --subject <agent>` shows that agent's ACTIVE tokens.
4. **Revoking** — `revoke --subject <agent> --token <uuid>`; issuer or owner only.

### Quick CLI Reference

| Subcommand | Key flags |
|---|---|
| `mint` | `--subject <agent>` `--kind approval\|mandate` `--scope <resource:action>` · pin with `--binds <trdd-id>` / `--binds-agent <id>` / `--binds-team <id>` · `--ttl <seconds>` |
| `list` | `--subject <agent>` |
| `verify` | `--subject <agent>` `--token <uuid>` · same `--binds*` / `--scope` to ask the specific question · `--json` for the raw verdict |
| `revoke` | `--subject <agent>` `--token <uuid>` |

## Output

Human-readable verdict on STDOUT; `--json` prints the raw verdict object for `jq`.
**The exit code is the interface for `verify`** — read it, do not scrape the text.

## Error Handling

| Symptom | Likely cause |
|---|---|
| exit `1` on every call | `AID_AUTH` not exported, or the API base is unreachable |
| exit `2` when you expected `0` | the token is expired/revoked, or it does not bind what you asked about — re-run without `--binds` to see whether the token is bad or merely not applicable |
| `mint` rejects the TTL | approval > 1h or mandate > 30d |
| `revoke` 403 | you are neither the issuer nor the owner |

## Examples

<example>
Before honouring "the MANAGER approved this card", prove it.
→ `aimaestro-portfolio.sh verify --subject "$ME" --token "$T" --binds M7BZ4X1Q`,
branch on `0` / `2` / `1` separately — never on "not 2".
</example>

<example>
Grant a narrow one-shot approval instead of a standing grant.
→ `mint --kind approval --scope trdd:approve --binds M7BZ4X1Q --ttl 900` — pinned
to one card and expiring in 15 minutes.
</example>

## Scope

Approval/mandate TOKENS only. The governance TITLES they are checked against are
`team-governance`; TRDD column moves are `ama-trdd-transition`.

## Resources

- `~/.claude/rules/prrd-design-rules.md` — the authority model these tokens make
  machine-checkable (golden vs silver, who may approve what).

## Use also

- `Skill(skill: "team-governance")` — the titles (MANAGER/COS/…) an issuer's
  authority is keyed on.
- `Skill(skill: "agent-identity")` — `AID_AUTH` comes from the AID layer this
  skill's callers must export.
