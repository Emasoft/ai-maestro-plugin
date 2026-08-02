---
name: memory-search
description: Recall prior knowledge from the markdown wiki-memory corpus (LOCAL + PROJECT + USER) via memgrep
---
# /memory-search

Recall what a past session already learned, indexed by the **symptom** — the words you
would use to describe the problem, not the jargon of its answer.

## Usage

```text
/memory-search <symptom or question>
```

## Implementation

Load the `memory-search` skill and follow it with the user's argument as the symptom.
The skill builds the three memory roots (LOCAL, PROJECT, USER) as a shell **array** and
runs `memgrep recall`, degrading to `grep -rliE` when memgrep is absent.

## Examples

```text
/memory-search the strict gate went red and I changed no code
/memory-search why does local publish disagree with CI
```

## Notes

Recall is **two hops**: this returns a ranked triage list of `<date> <page> <description>`
rows. The description tells you which page to open — it is not the answer. Take the second
hop on the one you pick:

```text
memgrep recall <page-or-atom-id> <memdir>
```

Nothing found means the memory does not exist yet — write one after you solve the problem.
