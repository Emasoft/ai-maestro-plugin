#!/usr/bin/env python3
"""
findprrd.py - Search PRRD rules by metadata.

Usage:
    findprrd.py --kind golden                # list all golden rules
    findprrd.py --grep "credentials"         # rules whose text matches regex
    findprrd.py --cited-in design/tasks/     # rules cited by any TRDD in that dir
    findprrd.py --unused                     # rules NOT cited by any TRDD
    findprrd.py --count                      # summary stats
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import prrd_lib as plib  # noqa: E402


def cmd_kind(kind: str) -> int:
    doc = plib.parse_prrd()
    k = "G" if kind.lower().startswith("g") else "S"
    for r in sorted([r for r in doc.rules if r.kind == k], key=lambda r: r.number):
        print(f"{r.cite()}\t{r.text}")
    return 0


def cmd_grep(pattern: str) -> int:
    doc = plib.parse_prrd()
    pat = re.compile(pattern, re.IGNORECASE)
    for r in sorted(doc.rules, key=lambda r: r.number):
        if pat.search(r.text):
            print(f"{r.cite()}\t{r.text}")
    return 0


def cmd_cited_in(target: str) -> int:
    doc = plib.parse_prrd()
    target_path = Path(target)
    files: list[Path] = []
    if target_path.is_file():
        files = [target_path]
    elif target_path.is_dir():
        files = sorted(target_path.rglob("*.md"))
    else:
        plib.die(f"path not found: {target}", code=2)
    cited: set[int] = set()
    rule_ref_re = re.compile(r"PRRD\s+[GS](\d+)(?:\.(\d+))?")
    frontmatter_re = re.compile(r"^relevant-rules:\s*\[(.*?)\]\s*$")
    for f in files:
        try:
            for line in f.read_text(encoding="utf-8").splitlines():
                for m in rule_ref_re.finditer(line):
                    cited.add(int(m.group(1)))
                fm = frontmatter_re.match(line.strip())
                if fm:
                    inner = fm.group(1)
                    for part in inner.split(","):
                        part = part.strip().strip("'\"")
                        if not part:
                            continue
                        ref = part.split(".")[0]
                        try:
                            cited.add(int(ref))
                        except ValueError:
                            pass
        except OSError:
            continue
    for r in sorted(
        [r for r in doc.rules if r.number in cited], key=lambda r: r.number
    ):
        print(f"{r.cite()}\t{r.text}")
    return 0


def cmd_unused() -> int:
    # Anti-cited: list rules NOT mentioned anywhere in design/tasks/ or design/requirements/
    doc = plib.parse_prrd()
    root = plib.find_project_root()
    cited: set[int] = set()
    rule_ref_re = re.compile(r"PRRD\s+[GS](\d+)(?:\.(\d+))?")
    frontmatter_re = re.compile(r"^relevant-rules:\s*\[(.*?)\]\s*$")
    for sub in (root / "design" / "tasks", root / "design" / "requirements"):
        if not sub.is_dir():
            continue
        for f in sub.rglob("*.md"):
            try:
                for line in f.read_text(encoding="utf-8").splitlines():
                    for m in rule_ref_re.finditer(line):
                        cited.add(int(m.group(1)))
                    fm = frontmatter_re.match(line.strip())
                    if fm:
                        inner = fm.group(1)
                        for part in inner.split(","):
                            part = part.strip().strip("'\"")
                            ref = part.split(".")[0] if part else ""
                            try:
                                cited.add(int(ref))
                            except ValueError:
                                pass
            except OSError:
                continue
    for r in sorted(
        [r for r in doc.rules if r.number not in cited], key=lambda r: r.number
    ):
        print(f"{r.cite()}\t{r.text}")
    return 0


def cmd_count() -> int:
    doc = plib.parse_prrd()
    g = len(doc.golden_rules())
    s = len(doc.silver_rules())
    total = len(doc.rules)
    print(f"PRRD path:     {doc.path}")
    print(f"prrd-version:  {doc.frontmatter.get('prrd-version', '(unset)')}")
    print(f"Rules total:   {total}  (golden={g}, silver={s})")
    if total > 0:
        next_n = doc.next_free_number()
        nums = sorted(r.number for r in doc.rules)
        print(f"Number range:  {min(nums)} … {max(nums)}  (next free: {next_n})")
        # Detect gaps from deletions
        expected = set(range(min(nums), max(nums) + 1))
        gaps = sorted(expected - set(nums))
        if gaps:
            print(
                f"Retired:       {len(gaps)}  ({gaps[:10]}{'...' if len(gaps) > 10 else ''})"
            )
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument(
        "--kind", choices=["golden", "silver", "G", "S", "g", "s"], help="list by kind"
    )
    g.add_argument("--grep", metavar="REGEX", help="search rule text")
    g.add_argument(
        "--cited-in", metavar="PATH", help="list rules cited by any TRDD in path"
    )
    g.add_argument(
        "--unused", action="store_true", help="list rules not cited anywhere"
    )
    g.add_argument("--count", action="store_true", help="summary stats")
    args = ap.parse_args(argv)

    if args.kind:
        return cmd_kind(args.kind)
    if args.grep:
        return cmd_grep(args.grep)
    if args.cited_in:
        return cmd_cited_in(args.cited_in)
    if args.unused:
        return cmd_unused()
    if args.count:
        return cmd_count()
    return 1


if __name__ == "__main__":
    sys.exit(main())
