#!/usr/bin/env python3
"""
prrd-edit.py - Mutate the PRRD (MANAGER-only for direct mutation).

Subcommands:
    add <kind> "<text>"               # next free number, version 1
    revise <number> "<new-text>"      # bump N.v -> N.v+1
    delete <number>                   # remove rule N; number retires forever
    promote <number>                  # S -> G (USER-only — pass --user)
    demote <number>                   # G -> S (USER-only — pass --user)
    propose <kind> "<text>" [--target N]  # writes a proposal file; does NOT touch PRRD

Authority:
    By default, requires the caller to be MANAGER (resolved via AID_AUTH
    against the AI Maestro server). Use --user to bypass for solo work
    (e.g. a developer working without AI Maestro). Use --force to bypass
    a non-fatal sanity check.
"""

from __future__ import annotations

import argparse
import sys
import uuid
from datetime import datetime
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import prrd_lib as plib  # noqa: E402


def now_iso() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")


def now_filename_ts() -> str:
    return datetime.now().astimezone().strftime("%Y%m%d_%H%M%S%z")


def require_manager(args: argparse.Namespace) -> None:
    if args.user:
        return
    if not plib.caller_is_manager():
        plib.die(
            "this operation requires MANAGER authority. "
            "If you are the human user working without AI Maestro, "
            "re-run with --user.",
            code=4,
        )


def require_user(args: argparse.Namespace) -> None:
    if not args.user:
        plib.die(
            "promote / demote / golden-rule mutation requires --user "
            "(the human, not MANAGER). Even MANAGER cannot toggle GOLDEN.",
            code=4,
        )


def cmd_add(args: argparse.Namespace) -> int:
    if args.kind.upper().startswith("G"):
        require_user(args)
        kind = "G"
    else:
        require_manager(args)
        kind = "S"
    doc = plib.parse_prrd()
    if not doc.path or not doc.path.exists():
        plib.die("no PRRD found. Run `get-prrd.py --init` first.", code=2)
    n = doc.next_free_number()
    rule = plib.PRRDRule(number=n, version=1, kind=kind, text=args.text.strip())
    doc.rules.append(rule)
    _bump_prrd_version(doc, kind)
    plib.write_prrd(doc)
    print(f"✓ added rule {rule.cite()}: {rule.text}")
    _warn_mirrors(doc)
    return 0


def cmd_revise(args: argparse.Namespace) -> int:
    doc = plib.parse_prrd()
    latest = doc.latest(args.number)
    if latest is None:
        plib.die(f"rule {args.number} not found", code=3)
    assert latest is not None
    if latest.kind == "G":
        require_user(args)
    else:
        require_manager(args)
    new_rule = plib.PRRDRule(
        number=latest.number,
        version=latest.version + 1,
        kind=latest.kind,
        text=args.text.strip(),
    )
    # Remove old, append new
    doc.rules = [r for r in doc.rules if not (r.number == latest.number and r.version == latest.version)]
    doc.rules.append(new_rule)
    _bump_prrd_version(doc, new_rule.kind)
    plib.write_prrd(doc)
    print(f"✓ revised {latest.kind}{latest.number}.{latest.version} → {new_rule.cite()}: {new_rule.text}")
    _warn_mirrors(doc)
    return 0


def cmd_delete(args: argparse.Namespace) -> int:
    doc = plib.parse_prrd()
    latest = doc.latest(args.number)
    if latest is None:
        plib.die(f"rule {args.number} not found", code=3)
    assert latest is not None
    if latest.kind == "G":
        require_user(args)
    else:
        require_manager(args)
    doc.rules = [r for r in doc.rules if r.number != args.number]
    _bump_prrd_version(doc, latest.kind)
    plib.write_prrd(doc)
    print(f"✓ deleted rule {args.number} (number retires forever)")
    _warn_mirrors(doc)
    return 0


def cmd_promote(args: argparse.Namespace) -> int:
    require_user(args)
    doc = plib.parse_prrd()
    latest = doc.latest(args.number)
    if latest is None:
        plib.die(f"rule {args.number} not found", code=3)
    assert latest is not None
    if latest.kind == "G":
        plib.die(f"rule {args.number} is already golden", code=2)
    # Flip letter, keep number and version
    latest.kind = "G"
    _bump_prrd_version(doc, "G")
    plib.write_prrd(doc)
    print(f"✓ promoted S{latest.number}.{latest.version} → G{latest.number}.{latest.version}")
    _warn_mirrors(doc)
    return 0


def cmd_demote(args: argparse.Namespace) -> int:
    require_user(args)
    doc = plib.parse_prrd()
    latest = doc.latest(args.number)
    if latest is None:
        plib.die(f"rule {args.number} not found", code=3)
    assert latest is not None
    if latest.kind == "S":
        plib.die(f"rule {args.number} is already silver", code=2)
    latest.kind = "S"
    _bump_prrd_version(doc, "G")
    plib.write_prrd(doc)
    print(f"✓ demoted G{latest.number}.{latest.version} → S{latest.number}.{latest.version}")
    _warn_mirrors(doc)
    return 0


def cmd_propose(args: argparse.Namespace) -> int:
    """Anyone can propose. Writes a proposal file; does NOT mutate PRRD."""
    root = plib.find_project_root()
    proposals_dir = root / "design" / "requirements" / "proposals"
    proposals_dir.mkdir(parents=True, exist_ok=True)
    pid = uuid.uuid4()
    ts = now_filename_ts()
    short = str(pid)[:8]
    slug = _slugify(args.text)[:40]
    fpath = proposals_dir / f"PROPOSAL-{ts}-{short}-{slug}.md"
    target = str(args.target) if args.target else "null"
    kind = args.kind.lower()
    body = f"""---
proposal-id: {pid}
proposes: {args.proposes}
target-rule: {target}
target-kind: {kind}
proposed-by: {args.proposed_by or 'unknown'}
routed-via: {args.routed_via or 'null'}
status: open
created: {now_iso()}
updated: {now_iso()}
---

# Proposal: {args.text[:80]}

## Rationale

<explain WHY this change is proposed>

## Proposed text

```
{args.text}
```

## MANAGER decision

<populated by MANAGER on review: accept | reject | forward-to-user>
"""
    fpath.write_text(body, encoding="utf-8")
    print(f"✓ proposal filed: {fpath.relative_to(root)}")
    print(f"  Routed via COS for MANAGER review.")
    return 0


def _bump_prrd_version(doc: plib.PRRDDoc, kind: str) -> None:
    """Major bump on golden changes; minor bump on silver."""
    v = str(doc.frontmatter.get("prrd-version", "0.1"))
    try:
        major, minor = v.split(".", 1)
        major, minor = int(major), int(minor)
    except ValueError:
        major, minor = 0, 1
    if kind == "G":
        major += 1
        minor = 0
    else:
        minor += 1
    doc.frontmatter["prrd-version"] = f"{major}.{minor}"
    doc.frontmatter["updated"] = now_iso()


def _warn_mirrors(doc: plib.PRRDDoc) -> None:
    mirrors = doc.frontmatter.get("mirrors") or []
    if isinstance(mirrors, list) and mirrors:
        print("⚠ Mirrors require sync:")
        for m in mirrors:
            print(f"    {m}")


def _slugify(text: str) -> str:
    import re
    s = text.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "proposal"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--user", action="store_true", help="bypass MANAGER auth (solo / no AI Maestro)")
    ap.add_argument("--force", action="store_true", help="bypass sanity checks")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_add = sub.add_parser("add", help="add a new rule (next free number, v1)")
    p_add.add_argument("kind", choices=["golden", "silver", "G", "S", "g", "s"])
    p_add.add_argument("text")

    p_rev = sub.add_parser("revise", help="bump a rule's version")
    p_rev.add_argument("number", type=int)
    p_rev.add_argument("text")

    p_del = sub.add_parser("delete", help="delete a rule; number retires forever")
    p_del.add_argument("number", type=int)

    p_pro = sub.add_parser("promote", help="S -> G (USER-only)")
    p_pro.add_argument("number", type=int)

    p_dem = sub.add_parser("demote", help="G -> S (USER-only)")
    p_dem.add_argument("number", type=int)

    p_prop = sub.add_parser("propose", help="file a proposal (anyone can propose)")
    p_prop.add_argument("kind", choices=["golden", "silver", "G", "S", "g", "s"])
    p_prop.add_argument("text")
    p_prop.add_argument("--proposes", default="revise", choices=["add", "revise", "delete", "promote", "demote"])
    p_prop.add_argument("--target", type=int, default=None)
    p_prop.add_argument("--proposed-by", default=None, help="agent session name")
    p_prop.add_argument("--routed-via", default=None, help="COS session name")

    args = ap.parse_args(argv)
    cmd = args.cmd
    if cmd == "add":
        return cmd_add(args)
    if cmd == "revise":
        return cmd_revise(args)
    if cmd == "delete":
        return cmd_delete(args)
    if cmd == "promote":
        return cmd_promote(args)
    if cmd == "demote":
        return cmd_demote(args)
    if cmd == "propose":
        return cmd_propose(args)
    return 1


if __name__ == "__main__":
    sys.exit(main())
