# PRRD/TRDD/Kanban scripts — full usage

The pillar scripts (+ shared `prrd_lib.py`) live at
`${CLAUDE_PLUGIN_ROOT}/scripts/prrd-trdd/`. Every script accepts
`--help`. All write to STDOUT, errors to STDERR, exit 0 on success.

**Reaching the scripts from a ROLE plugin** (amama-/amoa-/…): a role plugin's
own `${CLAUDE_PLUGIN_ROOT}` does NOT point at ai-maestro-plugin (the base that
ships these scripts), so resolve the directory at runtime with
`resolve_pillar_scripts.sh` (see below) — never hard-code a prose prerequisite.

## Contents

- resolve_pillar_scripts.sh — locate the scripts from any plugin (delivery mechanism)
- get-prrd.py — read PRRD rules
- prrd-edit.py — mutate the PRRD (MANAGER-only for direct mutation)
- findprrd.py — search PRRD rules
- findtrdd.py — find TRDDs
- kanban.py — render the board (READ-ONLY)
- bootstrap_design.py — create the 4-zone design/ folders
- amama_proposal_approvals.py — batch proposal approvals (list/approve/refuse/archive)
- Authoring a new TRDD (canonical skeleton)
- Exit codes
- Per-role quick examples

## resolve_pillar_scripts.sh — locate the scripts (cross-plugin delivery)

```bash
DIR="$(sh "$CLAUDE_PLUGIN_ROOT/scripts/prrd-trdd/resolve_pillar_scripts.sh")" || exit 1
python3 "$DIR/get-prrd.py" --list
```

Resolution order: `$AI_MAESTRO_PRRD_SCRIPTS_DIR` override → the resolver's own
dir (when called from the base) → highest `~/.claude/plugins/cache/*/ai-maestro-plugin/*/scripts/prrd-trdd`.
Exit 1 + a stderr diagnostic if no installed base is found. Full rationale:
[pillar-scripts-delivery.md](pillar-scripts-delivery.md).

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

## bootstrap_design.py — create the 4-zone design/ folders

```bash
bootstrap_design.py            # auto-detect project root
bootstrap_design.py /path/to/project
```

Idempotent. Creates `design/{requirements,proposals,tasks,refused,archived}/`
(with `.gitkeep` in the empty lifecycle zones) and removes a stray exact-match
`design/` line from `.gitignore` (design/ is git-tracked). Zone semantics:
[approval-tiers-and-zones.md](approval-tiers-and-zones.md).

## amama_proposal_approvals.py — batch proposal approvals

```bash
amama_proposal_approvals.py list                       # number every pending proposal
amama_proposal_approvals.py approve 4,6 --user         # or: approve <8-char-id>
amama_proposal_approvals.py refuse 7,8 --approve-rest --user   # refuse named, approve the rest
amama_proposal_approvals.py archive 9a8aba94 --state completed --user
amama_proposal_approvals.py archive 9a8aba94 --cancel --user   # alias: --state cancelled
```

A selector is a list-NUMBER (resolved against the most recent `list`, by stable
trdd-id) OR an 8-char id / full uuid. `approve` promotes proposal → planned
(`git mv` proposals/ → tasks/); `refuse` → refused/; `archive` → archived/.
Requires MANAGER authority or `--user`. Each decision appends an `## Approval
log` line and `git mv`s the file (never deletes). See
[approval-tiers-and-zones.md](approval-tiers-and-zones.md).

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
