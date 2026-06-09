# PRRD/TRDD/Kanban scripts — full usage

The five scripts (+ shared `prrd_lib.py`) live at
`${CLAUDE_PLUGIN_ROOT}/scripts/prrd-trdd/`. Every script accepts
`--help`. All write to STDOUT, errors to STDERR, exit 0 on success.

## Contents

- get-prrd.py — read PRRD rules
- prrd-edit.py — mutate the PRRD (MANAGER-only for direct mutation)
- findprrd.py — search PRRD rules
- findtrdd.py — find TRDDs
- kanban.py — render the board (READ-ONLY)
- Authoring a new TRDD (canonical skeleton)
- Exit codes
- Per-role quick examples

## get-prrd.py — read PRRD rules

```bash
get-prrd.py 70                 # latest version of rule 70
get-prrd.py 70.3               # specific version
get-prrd.py --cite 70.3        # formatted: "PRRD G70.3 — <text>"
get-prrd.py --list             # all rules
get-prrd.py --list --kind silver
get-prrd.py --json 70.3        # JSON object
get-prrd.py --init             # create an empty PRRD
```

The letter (G/S) in a reference is IGNORED on input — rules are
identified by number alone; the letter is for the human reader.

## prrd-edit.py — mutate the PRRD (MANAGER-only for direct mutation)

```bash
prrd-edit.py add silver "Use AID auth for all API calls"
prrd-edit.py revise 70 "new rule text"      # bumps version
prrd-edit.py delete 70                       # number retires forever
prrd-edit.py --user promote 70               # S -> G (USER-only)
prrd-edit.py --user demote 70                # G -> S (USER-only)
prrd-edit.py propose silver "text" --target 70 \
            --proposed-by my-session --routed-via cos-myteam
```

`--user` bypasses the MANAGER auth check (solo work without AI Maestro).
Non-MANAGER attempts to mutate without `--user` are refused; agents
must `propose` instead. Golden mutations + promote/demote are USER-only.

## findprrd.py — search PRRD rules

```bash
findprrd.py --kind golden
findprrd.py --grep "credentials"
findprrd.py --cited-in design/tasks/
findprrd.py --unused
findprrd.py --count
```

## findtrdd.py — find TRDDs

```bash
findtrdd.py 9a8aba94                          # by short UUID prefix
findtrdd.py --column blocked
findtrdd.py --assignee alice
findtrdd.py --blocked-by 9a8aba94             # reverse-dep
findtrdd.py --relevant-rule 64                # citation-aware
findtrdd.py --where "column=dev AND priority<3"
findtrdd.py --grep "auth"
findtrdd.py --format table
findtrdd.py --validate design/tasks/TRDD-...md
```

## kanban.py — render the board (READ-ONLY)

```bash
kanban.py                       # full board, compact
kanban.py --view wide
kanban.py --red                 # blocked column + priority ranking
kanban.py --column dev
kanban.py --group-by assignee
kanban.py --check-drift         # drift signals
kanban.py --json
```

`kanban.py` NEVER mutates a TRDD. Column moves are performed by editing
the TRDD's `column:` frontmatter field (per
[column-transitions.md](column-transitions.md)).

## Authoring a new TRDD (canonical skeleton)

```bash
TRDD_UUID=$(python3 -c "import uuid; print(uuid.uuid4())")
SHORT=${TRDD_UUID:0:8}                 # NB: not $UID (zsh reserves it)
TS=$(date +%Y%m%d_%H%M%S%z)
ISO=$(date +%Y-%m-%dT%H:%M:%S%z)
FN="design/tasks/TRDD-$TS-$SHORT-<short-slug>.md"

cat > "$FN" <<EOF
---
trdd-id: $TRDD_UUID
title: <one-line title>
column: backburner
created: $ISO
updated: $ISO
current-owner: <session-name>
task-type: feature
parent-trdd: null
npt: []
eht: []
blocked-by: []
relevant-rules: []
release-via: none
target-branch: main
test-requirements: []
runtime-targets: [macos]
impacts: []
attempts: 0
test-failures: 0
last-test-result: not-run
implementation-commits: []
ci-runs: []
---

# <title>

<prose body>
EOF
```

Minimal mandatory fields: `trdd-id`, `title`, `column`, `created`,
`updated`. All other fields take documented defaults from
[trdd-frontmatter-schema.md](trdd-frontmatter-schema.md).

## Exit codes

| Code | Meaning |
|---|---|
| 0 | success |
| 1 | usage / generic error |
| 2 | file / state precondition failed (PRRD missing, file exists) |
| 3 | not found (rule, TRDD) |
| 4 | authority refused (MANAGER-only without `--user`) |

## Per-role quick examples

```text
# AMAMA promotes a TRDD from backburner to todo
findtrdd.py 9a8aba94            # find the file, then edit column: todo

# ORCH checks the red column priority
kanban.py --red

# ARCHITECT looks up the rule a TRDD cites
get-prrd.py --cite 64.134

# INTEGRATOR validates a TRDD before deploying
findtrdd.py --validate design/tasks/TRDD-9a8aba94-*.md

# MEMBER files a proposal to revise rule S70
prrd-edit.py propose silver "new wording" --target 70 \
            --proposed-by member-frontend --routed-via cos-website
```
