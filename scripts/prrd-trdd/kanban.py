#!/usr/bin/env python3
"""
kanban.py - Render the .md-pile kanban view from TRDDs.

Usage:
    kanban.py                          # render the full board, compact
    kanban.py --view wide              # wide view, more detail per card
    kanban.py --group-by assignee      # group by assignee instead of column
    kanban.py --check-drift            # only show drift signals
    kanban.py --red                    # only the red (blocked) column, with priority ranking
    kanban.py --column dev             # only one column
    kanban.py --json                   # JSON output for tooling

Pure render — does NOT mutate any TRDD frontmatter.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import prrd_lib as plib  # noqa: E402


# Column ordering for visual layout
COLUMN_GROUPS = [
    ("ENTRY", ["backburner", "todo", "live_auditing"]),
    ("DESIGN", ["design", "dispatch"]),
    ("WORK", ["dev", "testing", "ai_review", "human_review"]),
    ("READY", ["complete"]),
    ("SHIP-tools", ["publish", "published"]),
    ("SHIP-services", ["deploy", "live"]),
    ("RED", ["blocked"]),
    ("DEAD", ["failed", "superseded"]),
]

ALL_COLUMNS = [c for _, cols in COLUMN_GROUPS for c in cols]

WORKING_COLUMNS = {
    "backburner",
    "todo",
    "design",
    "dispatch",
    "dev",
    "testing",
    "ai_review",
    "human_review",
    "complete",
    "publish",
    "deploy",
    "live_auditing",
}
TERMINAL_COLUMNS = {"published", "live", "failed", "superseded"}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--view", choices=["compact", "wide"], default="compact")
    ap.add_argument(
        "--group-by", choices=["column", "assignee", "priority"], default="column"
    )
    ap.add_argument(
        "--check-drift", action="store_true", help="show only drift signals"
    )
    ap.add_argument(
        "--red",
        action="store_true",
        help="show only the blocked column + priority ranking",
    )
    ap.add_argument("--column", help="render only one column")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    args = ap.parse_args(argv)

    docs = plib.list_trdds()

    if args.json:
        return emit_json(docs)
    if args.check_drift:
        return render_drift(docs)
    if args.red:
        return render_red_column(docs)
    if args.column:
        return render_single_column(docs, args.column, args.view)
    if args.group_by == "assignee":
        return render_by_assignee(docs, args.view)
    if args.group_by == "priority":
        return render_by_priority(docs, args.view)
    return render_full_board(docs, args.view)


def render_full_board(docs: list[plib.TRDDDoc], view: str) -> int:
    by_col: dict[str, list[plib.TRDDDoc]] = defaultdict(list)
    for d in docs:
        by_col[d.column or "(unknown)"].append(d)
    for group_name, cols in COLUMN_GROUPS:
        any_in_group = any(by_col.get(c) for c in cols)
        if not any_in_group:
            continue
        print(f"\n══════ {group_name} ══════")
        for col in cols:
            items = sorted(by_col.get(col, []), key=lambda d: d.priority)
            if not items:
                continue
            print(f"\n  ── {col} ({len(items)}) ──")
            if col == "blocked":
                _emit_red_priority(indent="    ")
            for d in items:
                print(_card_line(d, view))
    # Drift summary at the end
    drifts = collect_drift(docs)
    if drifts:
        print("\n══════ DRIFT SIGNALS ══════")
        for sig, items in drifts.items():
            print(f"  [{sig}] {len(items)} TRDD(s)")
            for d in items[:5]:
                print(f"    {d.short_ref()}  {d.title[:70]}")
    return 0


def render_red_column(docs: list[plib.TRDDDoc]) -> int:
    blocked = [d for d in docs if d.column == "blocked" or d.blocked_by]
    if not blocked:
        print("(no TRDDs blocked — red column is empty)")
        return 0
    print("══════ 🚫 BLOCKED ══════\n")
    _emit_red_priority(indent="")
    print(f"\n— Blocked TRDDs ({len(blocked)}) —")
    for d in sorted(blocked, key=lambda d: d.priority):
        print(_card_line(d, "wide"))
        if d.blocked_by:
            print(f"      blocked-by: {', '.join(d.blocked_by)}")
    return 0


def render_single_column(docs: list[plib.TRDDDoc], col: str, view: str) -> int:
    items = [d for d in docs if d.column == col]
    print(f"── {col} ({len(items)}) ──")
    for d in sorted(items, key=lambda d: d.priority):
        print(_card_line(d, view))
    return 0


def render_by_assignee(docs: list[plib.TRDDDoc], view: str) -> int:
    by_ass: dict[str, list[plib.TRDDDoc]] = defaultdict(list)
    for d in docs:
        by_ass[d.assignee or "(unassigned)"].append(d)
    for ass in sorted(by_ass):
        items = by_ass[ass]
        active = [d for d in items if d.column in WORKING_COLUMNS]
        print(f"\n── {ass} ({len(items)} total, {len(active)} active) ──")
        for d in sorted(items, key=lambda d: (d.column, d.priority)):
            print(_card_line(d, view))
    return 0


def render_by_priority(docs: list[plib.TRDDDoc], view: str) -> int:
    buckets: dict[int, list[plib.TRDDDoc]] = defaultdict(list)
    for d in docs:
        if d.column in TERMINAL_COLUMNS:
            continue
        buckets[d.priority].append(d)
    for pri in sorted(buckets):
        print(f"\n── Priority {pri} ({len(buckets[pri])}) ──")
        for d in sorted(buckets[pri], key=lambda d: d.column):
            print(_card_line(d, view))
    return 0


def render_drift(docs: list[plib.TRDDDoc]) -> int:
    drifts = collect_drift(docs)
    if not drifts:
        print("✓ No drift signals.")
        return 0
    for sig, items in drifts.items():
        print(f"\n[{sig}] {len(items)} TRDD(s)")
        for d in items:
            print(f"  {d.short_ref():<14} {d.title[:80]}")
    return 1


def collect_drift(docs: list[plib.TRDDDoc]) -> dict[str, list[plib.TRDDDoc]]:
    sigs: dict[str, list[plib.TRDDDoc]] = defaultdict(list)
    docs_by_ref = {d.short_ref(): d for d in docs}
    for d in docs:
        col = d.column
        if d.blocked_by and col != "blocked":
            sigs["drift-block-down"].append(d)
        if not d.blocked_by and col == "blocked":
            sigs["drift-block-up"].append(d)
        if col == "complete":
            # gate: every eht must be in terminal column
            for eht_ref in d.eht:
                eht = docs_by_ref.get(eht_ref)
                if eht and eht.column not in (
                    "complete",
                    "published",
                    "live",
                    "superseded",
                ):
                    sigs["drift-eht-gate"].append(d)
                    break
        if col == "published" and not d.frontmatter.get("published-version"):
            sigs["drift-publish-missing"].append(d)
        if col == "live" and not d.frontmatter.get("live-since"):
            sigs["drift-live-missing"].append(d)
        if (
            col in ("publish", "deploy")
            and d.frontmatter.get("last-test-result") != "pass"
        ):
            sigs["drift-ship-untested"].append(d)
        if (
            d.release_via == "publish"
            and not d.frontmatter.get("publish-target")
            and col == "publish"
        ):
            sigs["drift-publish-target-missing"].append(d)
        if (
            d.release_via == "deploy"
            and not d.frontmatter.get("deploy-target")
            and col == "deploy"
        ):
            sigs["drift-deploy-target-missing"].append(d)
    return dict(sigs)


def emit_json(docs: list[plib.TRDDDoc]) -> int:
    by_col: dict[str, list[dict]] = defaultdict(list)
    for d in docs:
        by_col[d.column or "(unknown)"].append(
            {
                "uid8": d.uid8,
                "trdd-id": d.uid,
                "title": d.title,
                "assignee": d.assignee,
                "priority": d.priority,
                "task-type": d.task_type,
                "release-via": d.release_via,
                "blocked-by": d.blocked_by,
                "npt": d.npt,
                "eht": d.eht,
            }
        )
    print(
        json.dumps(
            {
                "columns": by_col,
                "drift": {
                    k: [d.short_ref() for d in v]
                    for k, v in collect_drift(docs).items()
                },
                "red_priority": [
                    {
                        "trdd": entry["trdd"].short_ref(),
                        "unblocks": entry["unblocks_count"],
                        "currently_in": entry["currently_in"],
                        "assignee": entry["assignee"],
                    }
                    for entry in compute_red_priority(docs)
                ],
            },
            indent=2,
        )
    )
    return 0


def compute_red_priority(docs: list[plib.TRDDDoc]) -> list[dict]:
    """Per column-transitions.md `red_column_priority()`."""
    blocked = [d for d in docs if d.blocked_by]
    docs_by_ref = {d.short_ref(): d for d in docs}
    blocker_ids: set[str] = set()
    for d in blocked:
        blocker_ids.update(d.blocked_by)
    ranking: list[dict] = []
    for bid in blocker_ids:
        unblocks = sum(1 for d in blocked if bid in d.blocked_by)
        blocker_doc = docs_by_ref.get(bid)
        if not blocker_doc:
            # The blocker may be an external ref or not yet authored.
            continue
        ranking.append(
            {
                "trdd": blocker_doc,
                "unblocks_count": unblocks,
                "currently_in": blocker_doc.column,
                "assignee": blocker_doc.assignee or "(unassigned)",
            }
        )
    ranking.sort(key=lambda r: r["unblocks_count"], reverse=True)
    return ranking


def _emit_red_priority(indent: str) -> None:
    # Compute against ALL TRDDs, not just the blocked subset, because the
    # blocker may not itself be blocked.
    all_docs = plib.list_trdds()
    ranking = compute_red_priority(all_docs)
    if not ranking:
        return
    print(f"{indent}🔓 BLOCK-CLEARING PRIORITY (orchestrator: bump these)")
    for entry in ranking[:5]:
        t = entry["trdd"]
        print(
            f"{indent}  {t.short_ref():<14} unblocks {entry['unblocks_count']}   "
            f"currently in {entry['currently_in']:<14} assignee: {entry['assignee']}"
        )
    print()


def _card_line(d: plib.TRDDDoc, view: str) -> str:
    short = d.short_ref()
    pri = f"p{d.priority}"
    ass = (d.assignee or "-")[:14]
    title = d.title
    if view == "wide":
        rv = d.release_via or "none"
        tt = d.task_type or "-"
        return f"    {short:<14} [{pri:<3}] {ass:<14} type={tt:<8} via={rv:<7}  {title[:60]}"
    return f"    {short:<14} [{pri:<3}] {ass:<14} {title[:80]}"


if __name__ == "__main__":
    sys.exit(main())
