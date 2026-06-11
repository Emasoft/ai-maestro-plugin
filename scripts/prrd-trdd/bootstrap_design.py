#!/usr/bin/env python3
"""
bootstrap_design.py — create the 4-zone design/ folder model for a project.

Idempotent. Creates (if absent):

  design/requirements/      — home of PRRD.md
  design/proposals/         — TRDDs awaiting approval (column: proposal)
  design/tasks/             — OPEN work (column: planned … failed)
  design/refused/           — proposals never approved (column: refused)
  design/archived/          — terminal-DONE (completed/cancelled/superseded)

Each empty zone gets a .gitkeep so git tracks it. design/ is git-tracked and
MUST NOT be gitignored — this script removes a stray `design/` ignore entry if
it finds an exact-match line and warns about pattern matches it can't safely
auto-edit.

Usage:  python3 bootstrap_design.py [project-root]   (default: auto-detect)

Python stdlib only.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import prrd_lib as L  # noqa: E402

ZONES = ("requirements", "proposals", "tasks", "refused", "archived")


def ensure_not_gitignored(root: Path) -> None:
    gi = root / ".gitignore"
    if not gi.exists():
        return
    lines = gi.read_text(encoding="utf-8").splitlines()
    kept, removed = [], []
    for ln in lines:
        if ln.strip().rstrip("/") in ("design", "/design"):
            removed.append(ln)
        else:
            kept.append(ln)
    if removed:
        gi.write_text("\n".join(kept) + ("\n" if kept else ""), encoding="utf-8")
        print(f"removed {len(removed)} stray design/ ignore line(s) from .gitignore")
    for ln in kept:
        if "design" in ln and ln.strip().rstrip("/") not in ("design", "/design"):
            L.warn(f".gitignore pattern may still hide design/: {ln!r} — review by hand")


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    root = Path(argv[0]).resolve() if argv else L.find_project_root()
    if not root.is_dir():
        L.die(f"project root not a directory: {root}", 2)

    created = []
    for zone in ZONES:
        d = root / "design" / zone
        existed = d.is_dir()
        d.mkdir(parents=True, exist_ok=True)
        # .gitkeep only for the work/lifecycle zones (requirements holds PRRD.md)
        if zone != "requirements":
            keep = d / ".gitkeep"
            if not any(d.iterdir()) and not keep.exists():
                keep.write_text("", encoding="utf-8")
        if not existed:
            created.append(f"design/{zone}/")

    ensure_not_gitignored(root)

    if created:
        print("created: " + ", ".join(created))
    else:
        print("design/ 4-zone model already present — nothing to create")
    print(f"design zones ready under {root}/design/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
