#!/usr/bin/env python3
"""
findtrdd.py - Find TRDDs by short-uuid, metadata, or content.

Usage:
    findtrdd.py 9a8aba94                  # find by 8+-char UUID prefix
    findtrdd.py --column blocked          # all TRDDs in a column
    findtrdd.py --assignee alice          # all TRDDs assigned to alice
    findtrdd.py --blocked-by 9a8aba94     # all TRDDs blocked by ref
    findtrdd.py --relevant-rule 64        # all TRDDs citing PRRD rule 64
    findtrdd.py --grep "auth"             # regex search over title + body
    findtrdd.py --where "column=dev AND priority<3"
    findtrdd.py --validate <path>         # validate a TRDD's frontmatter

Output: one file path per line (relative to project root), unless
--format json|table is given.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import prrd_lib as plib  # noqa: E402

KNOWN_COLUMNS = {
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
    "published",
    "deploy",
    "live",
    "live_auditing",
    "blocked",
    "failed",
    "superseded",
}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument(
        "uid", nargs="?", help="partial UUID (8+ hex chars) or 'TRDD-<prefix>'"
    )
    ap.add_argument("--column", help="filter by column")
    ap.add_argument("--assignee", help="filter by assignee session name")
    ap.add_argument("--blocked-by", metavar="REF", help="all TRDDs blocked by this ref")
    ap.add_argument(
        "--blocks", metavar="REF", help="inverse — all TRDDs blocking this ref"
    )
    ap.add_argument(
        "--relevant-rule", metavar="N", type=int, help="all TRDDs citing PRRD rule N"
    )
    ap.add_argument("--grep", metavar="REGEX", help="regex search over title + body")
    ap.add_argument("--where", help="SQL-ish filter: 'column=dev AND priority<3'")
    ap.add_argument("--task-type", help="filter by task-type")
    ap.add_argument("--release-via", choices=["publish", "deploy", "none"])
    ap.add_argument(
        "--validate", metavar="PATH", help="validate a single TRDD's frontmatter"
    )
    ap.add_argument("--format", choices=["paths", "json", "table"], default="paths")
    ap.add_argument(
        "--sort",
        choices=["updated", "created", "priority", "column"],
        default="updated",
    )
    args = ap.parse_args(argv)

    if args.validate:
        return cmd_validate(args.validate)

    docs = plib.list_trdds()

    if args.uid:
        prefix = args.uid.lower().removeprefix("trdd-").removeprefix("#")
        docs = [
            d
            for d in docs
            if d.uid8.startswith(prefix) or d.uid.lower().startswith(prefix)
        ]
    if args.column:
        docs = [d for d in docs if d.column == args.column]
    if args.assignee:
        docs = [d for d in docs if d.assignee == args.assignee]
    if args.blocked_by:
        ref = _normalize_trdd_ref(args.blocked_by)
        docs = [
            d for d in docs if any(ref in b or b.endswith(ref) for b in d.blocked_by)
        ]
    if args.blocks:
        ref = _normalize_trdd_ref(args.blocks)
        # All TRDDs whose ref appears in some other TRDD's blocked-by — but we
        # want TRDDs that BLOCK the given ref, i.e. the given ref's blockers.
        target = next((d for d in docs if d.uid8.startswith(ref.lower())), None)
        if not target:
            return 0
        blockers = set(target.blocked_by)
        docs = [d for d in docs if d.short_ref() in blockers or d.uid in blockers]
    if args.relevant_rule is not None:
        rn = args.relevant_rule
        docs = [d for d in docs if _trdd_cites_rule(d, rn)]
    if args.grep:
        pat = re.compile(args.grep, re.IGNORECASE)
        kept = []
        for d in docs:
            if pat.search(d.title):
                kept.append(d)
                continue
            try:
                content = d.path.read_text(encoding="utf-8") if d.path else ""
                if pat.search(content):
                    kept.append(d)
            except OSError:
                pass
        docs = kept
    if args.where:
        docs = [d for d in docs if plib.matches_where(d, args.where)]
    if args.task_type:
        docs = [d for d in docs if d.task_type == args.task_type]
    if args.release_via:
        docs = [d for d in docs if d.release_via == args.release_via]

    docs = _sort_docs(docs, args.sort)
    _emit(docs, args.format)
    return 0


def _normalize_trdd_ref(ref: str) -> str:
    return ref.lower().removeprefix("trdd-").removeprefix("#")


def _trdd_cites_rule(d: plib.TRDDDoc, rule_number: int) -> bool:
    for item in d.relevant_rules:
        # item is "64" or "64.134"
        try:
            n = int(str(item).split(".")[0])
            if n == rule_number:
                return True
        except ValueError:
            continue
    return False


def _sort_docs(docs: list[plib.TRDDDoc], by: str) -> list[plib.TRDDDoc]:
    if by == "priority":
        return sorted(docs, key=lambda d: d.priority)
    if by == "column":
        return sorted(docs, key=lambda d: d.column)
    if by == "created":
        return sorted(docs, key=lambda d: d.frontmatter.get("created", ""))
    return sorted(docs, key=lambda d: d.frontmatter.get("updated", ""))


def _emit(docs: list[plib.TRDDDoc], fmt: str) -> None:
    root = plib.find_project_root()
    if fmt == "paths":
        for d in docs:
            if d.path:
                try:
                    print(d.path.relative_to(root))
                except ValueError:
                    print(d.path)
        return
    if fmt == "json":
        out = []
        for d in docs:
            out.append(
                {
                    "trdd-id": d.uid,
                    "uid8": d.uid8,
                    "title": d.title,
                    "column": d.column,
                    "assignee": d.assignee,
                    "priority": d.priority,
                    "path": str(d.path) if d.path else None,
                }
            )
        print(json.dumps(out, indent=2))
        return
    if fmt == "table":
        if not docs:
            print("(no TRDDs match)")
            return
        # Compact table
        col_uid, col_col, col_pri, col_ass, col_title = 10, 14, 4, 18, 60
        print(
            f"{'UID':<{col_uid}} {'COLUMN':<{col_col}} {'PRI':<{col_pri}} {'ASSIGNEE':<{col_ass}} TITLE"
        )
        print("-" * (col_uid + col_col + col_pri + col_ass + col_title + 4))
        for d in docs:
            uid = d.uid8[:col_uid]
            col = (d.column or "")[:col_col]
            pri = str(d.priority)[:col_pri]
            ass = (d.assignee or "-")[:col_ass]
            title = d.title[:col_title]
            print(
                f"{uid:<{col_uid}} {col:<{col_col}} {pri:<{col_pri}} {ass:<{col_ass}} {title}"
            )


def cmd_validate(path_str: str) -> int:
    path = Path(path_str)
    if not path.exists():
        plib.die(f"file not found: {path}", code=2)
    d = plib.parse_trdd(path)
    errors: list[str] = []
    fm = d.frontmatter
    # 1. Identity mandatory
    for key in ("trdd-id", "title", "column", "created", "updated"):
        if not fm.get(key) and not (key == "column" and fm.get("status")):
            errors.append(f"missing mandatory field: {key}")
    # 2. Column in enum
    col = d.column
    if col and col not in KNOWN_COLUMNS:
        errors.append(f"column={col!r} not in canonical enum")
    # 3. release-via constraints
    rv = d.release_via
    if col in ("publish", "published") and rv != "publish":
        errors.append(f"column={col} requires release-via=publish (have: {rv})")
    if col in ("deploy", "live") and rv != "deploy":
        errors.append(f"column={col} requires release-via=deploy (have: {rv})")
    if col == "blocked" and not d.blocked_by:
        errors.append("column=blocked but blocked-by is empty")
    if col == "superseded" and not fm.get("superseded-by"):
        errors.append("column=superseded but superseded-by is empty")
    if col == "published" and not fm.get("published-version"):
        errors.append("column=published but published-version is null")
    if col == "live" and not fm.get("live-since"):
        errors.append("column=live but live-since is null")
    if rv == "publish" and col == "publish" and not fm.get("publish-target"):
        errors.append("release-via=publish AND column=publish requires publish-target")
    if rv == "deploy" and col == "deploy" and not fm.get("deploy-target"):
        errors.append("release-via=deploy AND column=deploy requires deploy-target")
    if errors:
        for e in errors:
            print(f"  ✗ {e}")
        print(f"VALIDATION FAILED: {len(errors)} issue(s) in {path}")
        return 1
    print(f"VALIDATION OK: {path.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
