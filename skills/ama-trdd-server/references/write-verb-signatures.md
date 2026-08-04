# Write-verb signatures (frozen, from SCRIPT-MANIFEST.md)

## Contents

- [Signatures](#signatures)
- [Flag semantics](#flag-semantics)

## Signatures

| Verb | Signature | Effect |
|---|---|---|
| `edit <id>` | `--set k=v` (repeatable) | mutate frontmatter **in place**, no folder move |
| `approve <id>` | `--approver W --tier N --rationale R` | proposal → planned; `git mv proposals/ → tasks/`; mints the signed token |
| `refuse <id>` | `--approver W --tier N --reason R` | → `refused/` |
| `promote <id> --column C` | `[--note N] [--approver W]` | advance the card in place to column `C` |
| `archive <id> --state S` | `[--reason R] [--superseded-by ID] [--approver W]` | `S` ∈ `completed \| cancelled \| superseded` — **refuses `failed`** |

## Flag semantics

`--approver W` names the approving authority; `--tier N` is the tier being
exercised (which must meet the card's `min-approval-requirement:`). Global
`--agent <uuid|name>` operates on that agent's `<workdir>/design` corpus.

Nothing is committed for you.

`archive` refusing `failed` is deliberate and not an oversight: a failed card
stays ON the board so it can be retried, and archiving it as failed would hide
work that is still owed. See the kanban rule — the exception columns are signals,
not exits.
