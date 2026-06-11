#!/usr/bin/env python3
"""
amama_proposal_approvals.py — batch proposal approval tool for the 4-zone
design folders (proposals / tasks / refused / archived).

Operationalizes the proposal → planned lifecycle from
skills/prrd-trdd-kanban/references/approval-tiers-and-zones.md:

  list                         — number every pending proposal, one line each
  approve  <selector...>       — promote proposal(s): proposal → planned,
                                 git mv design/proposals/ → design/tasks/
  refuse   <selector...>       — decline proposal(s): proposal → refused,
                                 git mv design/proposals/ → design/refused/
                                 (--approve-rest also approves every OTHER
                                  proposal in the most recent listing)
  archive  --state S <sel...>  — terminal-DONE: column → completed|cancelled|
                                 superseded, git mv → design/archived/
                                 (`cancel` is an alias for --state cancelled)

A <selector> is EITHER the 1-based number from the most recent `list`
(resolved against a per-project manifest in the OS temp dir) OR the TRDD's
8-char id / full uuid. Numbers resolve by stable trdd-id, not array position.

Authority: approve/refuse/archive require MANAGER (AID_AUTH resolves to a
MANAGER title) OR the --user override (solo developer is the manager).

Python stdlib only. Never deletes a TRDD — every decision `git mv`s the file
between zones (RULE 0). git mv preserves history; if the path is not git
tracked the move falls back to a plain filesystem move with a warning.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import prrd_lib as L  # noqa: E402

ZONES = ("proposals", "tasks", "refused", "archived")
TERMINAL_STATES = ("completed", "cancelled", "superseded")


# ───────────────── zone paths ─────────────────


def design_dir(root: Path) -> Path:
    return root / "design"


def zone_dir(root: Path, zone: str) -> Path:
    return design_dir(root) / zone


def iso_now() -> str:
    return subprocess.check_output(["date", "+%Y-%m-%dT%H:%M:%S%z"]).decode().strip()


# ───────────────── frontmatter line edits ─────────────────


def set_fm_field(text: str, key: str, value: str) -> str:
    """Replace `^key: ...` in the frontmatter block, or insert it just before
    the closing `---` if the key is absent. Operates only inside the first
    frontmatter block (one-field-per-line invariant makes this safe)."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("TRDD has no YAML frontmatter")
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        raise ValueError("unterminated frontmatter")
    pat = re.compile(rf"^{re.escape(key)}:\s")
    for i in range(1, end):
        if pat.match(lines[i]):
            lines[i] = f"{key}: {value}"
            break
    else:
        lines.insert(end, f"{key}: {value}")
    return "\n".join(lines) + ("\n" if text.endswith("\n") else "")


def append_approval_log(text: str, line: str) -> str:
    """Append `line` under the body `## Approval log` section, creating the
    section at end-of-file if absent."""
    marker = "## Approval log"
    if marker in text:
        out, inserted = [], False
        body = text.splitlines()
        for idx, ln in enumerate(body):
            out.append(ln)
            if not inserted and ln.strip() == marker:
                # find the end of this section (next blank-then-heading or EOF)
                j = idx + 1
                while j < len(body) and not body[j].startswith("## "):
                    out.append(body[j])
                    j += 1
                if out and out[-1].strip() != "":
                    out.append("")
                out.append(line)
                out.extend(body[j:])
                inserted = True
                break
        return "\n".join(out) + ("\n" if text.endswith("\n") else "")
    sep = "" if text.endswith("\n") else "\n"
    return f"{text}{sep}\n{marker}\n\n{line}\n"


# ───────────────── manifest (number → trdd-id) ─────────────────


def manifest_path(root: Path) -> Path:
    h = hashlib.sha256(str(root.resolve()).encode()).hexdigest()[:16]
    return Path(tempfile.gettempdir()) / f"amama-proposal-manifest-{h}.json"


def write_manifest(root: Path, items: list[dict]) -> None:
    manifest_path(root).write_text(
        json.dumps({"root": str(root.resolve()), "items": items}, indent=2),
        encoding="utf-8",
    )


def read_manifest(root: Path) -> list[dict]:
    p = manifest_path(root)
    if not p.exists():
        return []
    try:
        return json.loads(p.read_text(encoding="utf-8")).get("items", [])
    except (ValueError, OSError):
        return []


# ───────────────── proposal discovery ─────────────────


def scan_proposals(root: Path) -> list[L.TRDDDoc]:
    d = zone_dir(root, "proposals")
    if not d.is_dir():
        return []
    docs = []
    for f in sorted(d.glob("TRDD-*.md")):
        try:
            doc = L.parse_trdd(f)
        except Exception as e:  # noqa: BLE001 - tool resilience
            L.warn(f"failed to parse {f.name}: {e}")
            continue
        if doc.column == "refused":
            continue
        docs.append(doc)
    docs.sort(key=lambda d: d.frontmatter.get("created", ""))
    return docs


def find_trdd_any_zone(root: Path, ident: str) -> Path | None:
    """Locate a TRDD file by 8-char id or full uuid across all zones."""
    ident = ident.lower().removeprefix("trdd-").removeprefix("#")
    for zone in ZONES:
        d = zone_dir(root, zone)
        if not d.is_dir():
            continue
        for f in d.glob("TRDD-*.md"):
            doc = L.parse_trdd(f)
            if doc.uid8 == ident[:8] or doc.uid == ident:
                return f
    return None


def resolve_selector(root: Path, selector: str) -> Path | None:
    """Resolve a selector to a TRDD path. A SHORT all-digit selector (< 8
    digits) is a 1-based list number resolved against the last `list` manifest
    (by stable trdd-id). Anything else — including an 8-char id that happens to
    be all digits (~2% of real UUIDv4 prefixes) — is a uid8 / full uuid.
    (uid8 is always exactly 8 chars; list numbers are never that large.)"""
    s = selector.strip()
    if s.isdigit() and len(s) < 8:
        n = int(s)
        for item in read_manifest(root):
            if item.get("n") == n:
                return find_trdd_any_zone(root, item["id"])
        L.die(f"selector {n} not in the last listing — re-run `list` first", 2)
    return find_trdd_any_zone(root, s)


# ───────────────── authority ─────────────────


def require_manager(args: argparse.Namespace) -> None:
    if getattr(args, "user", False):
        return  # solo developer is the manager (matches prrd-edit.py --user)
    if not L.caller_is_manager():
        L.die(
            "approve/refuse/archive require MANAGER authority "
            "(AID_AUTH → MANAGER) or the --user override",
            4,
        )


# ───────────────── moves ─────────────────


def git_mv(root: Path, src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(
        ["git", "-C", str(root), "mv", str(src), str(dst)],
        capture_output=True,
        text=True,
        check=False,
    )
    if r.returncode != 0:
        L.warn(f"git mv failed ({r.stderr.strip()}); falling back to plain move")
        shutil.move(str(src), str(dst))


def promote(root: Path, src: Path, new_column: str, log_verb: str,
            approver: str, note: str) -> Path:
    doc = L.parse_trdd(src)
    tier = doc.frontmatter.get("approval-tier", 0)
    text = src.read_text(encoding="utf-8")
    text = set_fm_field(text, "column", new_column)
    text = set_fm_field(text, "updated", iso_now())
    log = f"- {iso_now()} — {log_verb} by {approver} (tier {tier}). {note}".rstrip(". ") + "."
    text = append_approval_log(text, log)
    src.write_text(text, encoding="utf-8")
    target_zone = {"planned": "tasks", "refused": "refused"}.get(
        new_column, "archived" if new_column in TERMINAL_STATES else "tasks"
    )
    dst = zone_dir(root, target_zone) / src.name
    git_mv(root, src, dst)
    return dst


# ───────────────── subcommands ─────────────────


def cmd_list(args: argparse.Namespace) -> int:
    root = Path(args.project).resolve() if args.project else L.find_project_root()
    docs = scan_proposals(root)
    items = []
    for i, doc in enumerate(docs, start=1):
        items.append(
            {
                "n": i,
                "id": doc.uid8 or doc.uid,
                "tier": doc.frontmatter.get("approval-tier", 0),
                "title": doc.title,
            }
        )
    write_manifest(root, items)
    if args.json:
        print(json.dumps(items, indent=2))
        return 0
    if not items:
        print("No pending proposals in design/proposals/.")
        return 0
    print(f"Pending proposals ({len(items)}) — reply `approve N,N` or `refuse N,N`:")
    for it in items:
        print(f"  {it['n']:>3}  {it['id']:<8}  tier {it['tier']}  {it['title']}")
    return 0


def cmd_approve(args: argparse.Namespace) -> int:
    require_manager(args)
    root = Path(args.project).resolve() if args.project else L.find_project_root()
    approver = args.approver or os.environ.get("AMAMA_APPROVER", "MANAGER")
    note = args.rationale or "approved"
    n = 0
    for sel in args.selectors:
        src = resolve_selector(root, sel)
        if not src:
            L.warn(f"selector '{sel}' did not resolve to a proposal; skipping")
            continue
        dst = promote(root, src, "planned", "APPROVED", approver, note)
        print(f"approved: {src.name} → {dst.parent.name}/")
        n += 1
    print(f"{n} proposal(s) approved → planned.")
    return 0 if n else 1


def cmd_refuse(args: argparse.Namespace) -> int:
    require_manager(args)
    root = Path(args.project).resolve() if args.project else L.find_project_root()
    approver = args.approver or os.environ.get("AMAMA_APPROVER", "MANAGER")
    note = args.reason or "refused"
    named_ids = set()
    refused = 0
    for sel in args.selectors:
        src = resolve_selector(root, sel)
        if not src:
            L.warn(f"selector '{sel}' did not resolve to a proposal; skipping")
            continue
        named_ids.add(L.parse_trdd(src).uid8)
        promote(root, src, "refused", "REFUSED", approver, note)
        print(f"refused: {src.name}")
        refused += 1
    approved = 0
    if args.approve_rest:
        for doc in scan_proposals(root):
            if doc.uid8 in named_ids or doc.path is None:
                continue
            src = doc.path
            dst = promote(root, src, "planned", "APPROVED", approver,
                          "approved (complement of refused set)")
            print(f"approved (rest): {src.name} → {dst.parent.name}/")
            approved += 1
    print(f"{refused} refused; {approved} approved-as-rest.")
    return 0 if (refused or approved) else 1


def cmd_archive(args: argparse.Namespace) -> int:
    require_manager(args)
    state = "cancelled" if args.cancel else args.state
    if state not in TERMINAL_STATES:
        L.die(f"--state must be one of {TERMINAL_STATES}", 2)
    root = Path(args.project).resolve() if args.project else L.find_project_root()
    approver = args.approver or os.environ.get("AMAMA_APPROVER", "MANAGER")
    note = args.reason or state
    n = 0
    for sel in args.selectors:
        src = resolve_selector(root, sel)
        if not src:
            L.warn(f"selector '{sel}' did not resolve to a TRDD; skipping")
            continue
        dst = promote(root, src, state, state.upper(), approver, note)
        print(f"archived ({state}): {src.name} → {dst.parent.name}/")
        n += 1
    print(f"{n} TRDD(s) archived as {state}.")
    return 0 if n else 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--project", help="project root (default: auto-detect)")
    sub = p.add_subparsers(dest="cmd", required=True)

    pl = sub.add_parser("list", help="list pending proposals")
    pl.add_argument("--json", action="store_true")
    pl.set_defaults(func=cmd_list)

    for name, fn, helptext in (
        ("approve", cmd_approve, "promote proposal(s) → planned"),
        ("refuse", cmd_refuse, "decline proposal(s) → refused"),
    ):
        sp = sub.add_parser(name, help=helptext)
        sp.add_argument("selectors", nargs="+", help="numbers (from list) or 8-char ids")
        sp.add_argument("--user", action="store_true", help="solo override (skip AID check)")
        sp.add_argument("--approver", help="approver name (default MANAGER)")
        if name == "approve":
            sp.add_argument("--rationale", help="one-line rationale for the approval log")
        else:
            sp.add_argument("--reason", help="one-line reason for the approval log")
            sp.add_argument("--approve-rest", action="store_true",
                            help="ALSO approve every other listed proposal")
        sp.set_defaults(func=fn)

    pa = sub.add_parser("archive", help="archive a TRDD (completed/cancelled/superseded)")
    pa.add_argument("selectors", nargs="+", help="numbers or 8-char ids")
    pa.add_argument("--state", choices=TERMINAL_STATES, default="completed")
    pa.add_argument("--cancel", action="store_true", help="alias for --state cancelled")
    pa.add_argument("--user", action="store_true")
    pa.add_argument("--approver")
    pa.add_argument("--reason")
    pa.set_defaults(func=cmd_archive)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
