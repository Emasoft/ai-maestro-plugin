#!/usr/bin/env python3
"""
get-prrd.py - Look up PRRD rules.

Usage:
    get-prrd.py <number>          # latest version of rule N
    get-prrd.py <number>.<ver>    # specific rule N.v
    get-prrd.py G<number>.<ver>   # letter is ignored on input
    get-prrd.py --list            # list all rules
    get-prrd.py --list --kind G   # list only golden
    get-prrd.py --cite <number>.<ver>   # `PRRD G70.3 — <text>` form
    get-prrd.py --json <number>.<ver>   # JSON object
    get-prrd.py --init            # create an empty PRRD at design/requirements/PRRD.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Allow running as a standalone script: locate prrd_lib relative to this file.
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import prrd_lib as plib  # noqa: E402


def parse_ref(s: str) -> tuple[int, int | None]:
    """Accept `64`, `64.134`, `G64.134`, `S64.134` → (64, 134) or (64, None)."""
    m = re.match(r"^[GSgs]?(\d+)(?:\.(\d+))?$", s.strip())
    if not m:
        plib.die(f"unrecognised rule reference: {s!r}")
    assert m is not None
    n = int(m.group(1))
    v = int(m.group(2)) if m.group(2) else None
    return n, v


def cmd_init() -> int:
    p = plib.prrd_path()
    if p.exists():
        plib.die(f"PRRD already exists at {p}", code=2)
    p.parent.mkdir(parents=True, exist_ok=True)
    empty = plib.PRRDDoc(path=p)
    p.write_text(plib._render_prrd_default(empty), encoding="utf-8")
    print(f"initialised PRRD at {p}")
    return 0


def cmd_list(kind_filter: str | None) -> int:
    doc = plib.parse_prrd()
    rules = doc.rules
    if kind_filter:
        kf = kind_filter.upper()[:1]
        rules = [r for r in rules if r.kind == kf]
    for r in sorted(rules, key=lambda r: (r.number, -r.version)):
        # In ascending number order; if multiple versions of same number exist
        # (unusual but possible during transitions), prefer latest first.
        print(f"{r.kind}{r.number}.{r.version}\t{r.text}")
    return 0


def cmd_get(args: argparse.Namespace) -> int:
    n, v = parse_ref(args.ref)
    doc = plib.parse_prrd()
    if v is None:
        rule = doc.latest(n)
    else:
        rule = doc.by_number_version(n, v)
    if rule is None:
        plib.die(f"no rule {args.ref} found in {doc.path}", code=3)
    assert rule is not None
    if args.json:
        print(
            json.dumps(
                {
                    "number": rule.number,
                    "version": rule.version,
                    "kind": rule.kind,
                    "text": rule.text,
                },
                indent=2,
            )
        )
        return 0
    if args.cite:
        print(f"{rule.cite()} — {rule.text}")
        return 0
    print(rule.text)
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("ref", nargs="?", help="rule reference (e.g. 64, 64.134, G64.134)")
    ap.add_argument("--list", action="store_true", help="list all rules")
    ap.add_argument(
        "--kind",
        choices=["G", "S", "g", "s", "golden", "silver"],
        help="filter list by kind",
    )
    ap.add_argument("--cite", action="store_true", help="format result as a citation")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    ap.add_argument(
        "--init", action="store_true", help="create an empty PRRD if missing"
    )
    args = ap.parse_args(argv)

    if args.init:
        return cmd_init()
    if args.list:
        kf = args.kind
        if kf and kf.lower().startswith("g"):
            kf = "G"
        elif kf and kf.lower().startswith("s"):
            kf = "S"
        return cmd_list(kf)
    if not args.ref:
        ap.print_help()
        return 1
    return cmd_get(args)


if __name__ == "__main__":
    sys.exit(main())
