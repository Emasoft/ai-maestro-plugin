#!/usr/bin/env sh
# resolve_pillar_scripts.sh — print the absolute path of the directory that
# holds the PRRD/TRDD/Kanban pillar scripts (get-prrd.py, prrd-edit.py,
# findprrd.py, findtrdd.py, kanban.py, amama_proposal_approvals.py,
# bootstrap_design.py, prrd_lib.py).
#
# WHY THIS EXISTS: a ROLE plugin (amama-/amoa-/amaa-/amia-/ampa-/amcos-/
# autonomous/maintainer) needs these scripts at runtime, but its own
# ${CLAUDE_PLUGIN_ROOT} points at the ROLE plugin, not at ai-maestro-plugin
# (the base that ships the scripts). A prose-only "you need ai-maestro-plugin"
# prerequisite is a silent runtime failure. This resolver makes the dependency
# executable: source/call it and you get the real directory or a non-zero exit.
#
# Resolution order (first hit wins):
#   1. $AI_MAESTRO_PRRD_SCRIPTS_DIR        — explicit override (CI, tests, dev).
#   2. This script's OWN directory          — when called from inside the base.
#   3. ~/.claude/plugins/cache/*/ai-maestro-plugin/*/scripts/prrd-trdd
#                                            — highest installed version.
#
# Usage from a role plugin:
#   DIR="$(sh resolve_pillar_scripts.sh)" || exit 1
#   python3 "$DIR/get-prrd.py" --list
#
# Exit 0 + prints the dir on success; exit 1 + diagnostic on stderr if no
# copy of the base is found. POSIX sh; no bashisms.

set -u

has_pillars() {
    # A directory qualifies only if it actually contains the shared lib.
    [ -f "$1/prrd_lib.py" ]
}

# 1. Explicit override.
if [ "${AI_MAESTRO_PRRD_SCRIPTS_DIR:-}" != "" ] && has_pillars "$AI_MAESTRO_PRRD_SCRIPTS_DIR"; then
    printf '%s\n' "$AI_MAESTRO_PRRD_SCRIPTS_DIR"
    exit 0
fi

# 2. This script's own directory (resolve symlinks via cd -P).
SELF_DIR="$(cd -P "$(dirname "$0")" 2>/dev/null && pwd)"
if [ -n "${SELF_DIR:-}" ] && has_pillars "$SELF_DIR"; then
    printf '%s\n' "$SELF_DIR"
    exit 0
fi

# 3. Highest installed ai-maestro-plugin version in the plugins cache.
#    Version dirs sort lexicographically; `sort -V` gives semantic order.
CACHE_GLOB="${HOME}/.claude/plugins/cache"
if [ -d "$CACHE_GLOB" ]; then
    best=""
    # shellcheck disable=SC2044
    for d in "$CACHE_GLOB"/*/ai-maestro-plugin/*/scripts/prrd-trdd; do
        [ -d "$d" ] || continue
        has_pillars "$d" || continue
        if [ -z "$best" ]; then
            best="$d"
        else
            # Keep whichever version dir sorts higher with -V.
            higher="$(printf '%s\n%s\n' "$best" "$d" | sort -V | tail -n1)"
            best="$higher"
        fi
    done
    if [ -n "$best" ]; then
        printf '%s\n' "$best"
        exit 0
    fi
fi

printf '%s\n' "resolve_pillar_scripts: could not find ai-maestro-plugin pillar scripts. Install the ai-maestro-plugin base, or set AI_MAESTRO_PRRD_SCRIPTS_DIR." >&2
exit 1
