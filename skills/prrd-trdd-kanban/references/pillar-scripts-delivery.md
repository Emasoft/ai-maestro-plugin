# Cross-plugin pillar-script delivery

**The problem.** The PRRD/TRDD/Kanban pillar scripts (`get-prrd.py`,
`prrd-edit.py`, `findprrd.py`, `findtrdd.py`, `kanban.py`,
`amama_proposal_approvals.py`, `bootstrap_design.py`, shared `prrd_lib.py`) ship
in ONE place: `ai-maestro-plugin/scripts/prrd-trdd/`. Every role plugin
(`amama-`/`amoa-`/`amaa-`/`amia-`/`ampa-`/`amcos-`/autonomous/maintainer) needs
them at runtime, but a role plugin's `${CLAUDE_PLUGIN_ROOT}` points at the ROLE
plugin, not at the base. A prose-only "you need ai-maestro-plugin installed"
prerequisite is a **silent runtime failure** the first time an agent runs
`get-prrd.py` and the shell reports "command not found".

**The mechanism.** ai-maestro-plugin ships `resolve_pillar_scripts.sh` — a tiny
POSIX-sh resolver that returns the absolute path of the pillar-scripts directory
or exits non-zero with a diagnostic. Role plugins call it instead of hard-coding
a path:

```bash
# The role plugin invokes the resolver (bundled or found on PATH) and uses the
# directory it prints. If the resolver exits non-zero, the base is not installed.
DIR=$(sh resolve_pillar_scripts.sh) || { echo "ai-maestro-plugin base not installed; see its README" >&2; exit 1; }
python3 "$DIR/get-prrd.py" --list
```

Resolution order (first hit wins):

1. **`$AI_MAESTRO_PRRD_SCRIPTS_DIR`** — explicit override (CI, tests, unusual
   installs). Always wins when it points at a dir containing `prrd_lib.py`.
2. **The resolver's own directory** — correct when the resolver is invoked from
   inside the base itself (the base's own skills/commands).
3. **`~/.claude/plugins/cache/*/ai-maestro-plugin/*/scripts/prrd-trdd`** — the
   highest installed version (`sort -V`). This is how a SEPARATE role plugin
   reaches the base after both are installed from the marketplace.

## Contents

- Two supported delivery models
- Why a resolver, not a hard-coded path

## Two supported delivery models

A role plugin picks ONE — both are first-class; the resolver supports both:

| Model | How the role plugin reaches the scripts | When to use |
|---|---|---|
| **Depend on the base** (recommended) | Role plugin's docs declare the `ai-maestro-plugin` dependency; at runtime it calls the resolver (case 3 finds the cached base). | The normal marketplace install — one copy of the scripts, shared. |
| **Bundle the scripts** | Role plugin vendors `scripts/prrd-trdd/` into its own tree; the resolver's case 2 (own dir) finds them. | Air-gapped / standalone distribution where the base may be absent. |

**Declaring the dependency.** Until Claude Code ships a formal `plugin.json`
`dependencies` field, a role plugin declares the dependency in its README /
plugin description prose AND makes it executable by shipping (or invoking) the
resolver — the resolver turns a soft prose dependency into a hard runtime check
that fails loudly (exit 1 + diagnostic) instead of silently. A role plugin MUST
NOT rely on prose alone.

## Why a resolver, not a hard-coded path

- Plugin cache paths embed the **marketplace owner** and the **version**
  (`~/.claude/plugins/cache/<marketplace>/ai-maestro-plugin/<version>/…`), both
  of which change across installs and updates. A hard-coded path rots on the
  next `claude plugin update`.
- The env override gives tests and CI a deterministic injection point without
  touching the cache.
- The "own dir" case means the base's own skills keep working with zero
  configuration.

The resolver is intentionally dependency-free POSIX sh (no python, no jq, no
bashisms) so it runs in the most minimal shell a hook or skill might invoke it
from.
