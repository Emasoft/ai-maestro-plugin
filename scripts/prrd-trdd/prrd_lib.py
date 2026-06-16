#!/usr/bin/env python3
"""
prrd_lib.py - Shared library for PRRD/TRDD scripts.

Python stdlib only. No third-party dependencies. Hand-parses the
restricted YAML subset used by PRRD/TRDD frontmatter (one field per
line, flow-style lists, bare enums, ISO 8601 datetimes).

This is NOT a general YAML library. It works only because the
PRRD/TRDD greppability invariants restrict the input space.
"""

from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, NoReturn

# ───────────────── path resolution ─────────────────


def find_project_root(start: Path | None = None) -> Path:
    """Walk up from `start` (cwd default) until we find one of:
    - design/requirements/PRRD.md (canonical PRRD home)
    - design/tasks/ (canonical TRDD home)
    - .git (repo root fallback)
    """
    p = (start or Path.cwd()).resolve()
    for candidate in [p, *p.parents]:
        if (candidate / "design" / "requirements" / "PRRD.md").exists():
            return candidate
        if (candidate / "design" / "tasks").is_dir():
            return candidate
        if (candidate / ".git").exists():
            return candidate
    return Path.cwd().resolve()


def prrd_path(project_root: Path | None = None) -> Path:
    root = project_root or find_project_root()
    return root / "design" / "requirements" / "PRRD.md"


def trdd_dir(project_root: Path | None = None) -> Path:
    root = project_root or find_project_root()
    return root / "design" / "tasks"


# ───────────────── PRRD parsing ─────────────────

PRRD_RULE_RE = re.compile(
    r"^\s*[-*]\s*\*\*(?P<letter>[GS])(?P<number>\d+)\.(?P<version>\d+)\*\*\s*[-—]+\s*(?P<text>.*?)\s*$"
)


@dataclass
class PRRDRule:
    number: int
    version: int
    kind: str  # 'G' or 'S'
    text: str
    line_number: int = 0  # in the PRRD file

    def cite(self) -> str:
        return f"PRRD {self.kind}{self.number}.{self.version}"

    def ident_long(self) -> str:
        return f"{self.kind}{self.number}.{self.version}"

    def ident_short(self) -> str:
        return f"{self.number}.{self.version}"


@dataclass
class PRRDDoc:
    frontmatter: dict[str, Any] = field(default_factory=dict)
    rules: list[PRRDRule] = field(default_factory=list)
    path: Path | None = None
    raw_lines: list[str] = field(default_factory=list)

    def by_number(self, number: int) -> list[PRRDRule]:
        return [r for r in self.rules if r.number == number]

    def by_number_version(self, number: int, version: int) -> PRRDRule | None:
        for r in self.rules:
            if r.number == number and r.version == version:
                return r
        return None

    def latest(self, number: int) -> PRRDRule | None:
        candidates = self.by_number(number)
        if not candidates:
            return None
        return max(candidates, key=lambda r: r.version)

    def next_free_number(self) -> int:
        if not self.rules:
            return 1
        return max(r.number for r in self.rules) + 1

    def golden_rules(self) -> list[PRRDRule]:
        return [r for r in self.rules if r.kind == "G"]

    def silver_rules(self) -> list[PRRDRule]:
        return [r for r in self.rules if r.kind == "S"]


def parse_prrd(path: Path | None = None) -> PRRDDoc:
    p = path or prrd_path()
    if not p.exists():
        return PRRDDoc(path=p)
    raw = p.read_text(encoding="utf-8")
    lines = raw.splitlines()
    fm, body_start = _parse_frontmatter(lines)
    rules: list[PRRDRule] = []
    for i, line in enumerate(lines[body_start:], start=body_start + 1):
        m = PRRD_RULE_RE.match(line)
        if m:
            rules.append(
                PRRDRule(
                    number=int(m.group("number")),
                    version=int(m.group("version")),
                    kind=m.group("letter"),
                    text=m.group("text").strip(),
                    line_number=i,
                )
            )
    return PRRDDoc(frontmatter=fm, rules=rules, path=p, raw_lines=lines)


# ───────────────── TRDD parsing ─────────────────

TRDD_FILENAME_RE = re.compile(
    r"TRDD-(?P<ts>[\d_+\-]+)-(?P<uid8>[0-9a-fA-F]{8})-(?P<slug>[^.]+)\.md$"
)


@dataclass
class TRDDDoc:
    frontmatter: dict[str, Any] = field(default_factory=dict)
    path: Path | None = None
    uid: str = ""
    uid8: str = ""

    @property
    def column(self) -> str:
        # v2 column or v1 status fallback
        c = self.frontmatter.get("column")
        if c:
            return c
        s = self.frontmatter.get("status")
        return _v1_status_to_v2_column(s) if s else ""

    @property
    def title(self) -> str:
        return self.frontmatter.get("title", "")

    @property
    def blocked_by(self) -> list[str]:
        return self.frontmatter.get("blocked-by", []) or []

    @property
    def npt(self) -> list[str]:
        return self.frontmatter.get("npt", []) or []

    @property
    def eht(self) -> list[str]:
        return self.frontmatter.get("eht", []) or []

    @property
    def relevant_rules(self) -> list[str]:
        return self.frontmatter.get("relevant-rules", []) or []

    @property
    def assignee(self) -> str | None:
        return self.frontmatter.get("assignee")

    @property
    def priority(self) -> int:
        try:
            return int(self.frontmatter.get("priority", 5))
        except (TypeError, ValueError):
            return 5

    @property
    def task_type(self) -> str:
        return self.frontmatter.get("task-type", "")

    @property
    def release_via(self) -> str:
        return self.frontmatter.get("release-via", "none")

    def short_ref(self) -> str:
        return f"TRDD-{self.uid8}" if self.uid8 else ""


_V1_TO_V2 = {
    "not-started": "backburner",
    "in-progress": "dev",
    "completed": "complete",
    "failed": "failed",
    "blocked": "blocked",
    "superseded": "superseded",
}


def _v1_status_to_v2_column(status: str | None) -> str:
    if not status:
        return ""
    return _V1_TO_V2.get(status, status)


def parse_trdd(path: Path) -> TRDDDoc:
    raw = path.read_text(encoding="utf-8")
    lines = raw.splitlines()
    fm, _ = _parse_frontmatter(lines)
    doc = TRDDDoc(frontmatter=fm, path=path)
    doc.uid = fm.get("trdd-id", "")
    # uid8 — first 8 chars of UUID, or derive from filename
    m = TRDD_FILENAME_RE.search(path.name)
    if m:
        doc.uid8 = m.group("uid8").lower()
    elif doc.uid:
        doc.uid8 = doc.uid[:8].lower()
    return doc


def list_trdds(root: Path | None = None) -> list[TRDDDoc]:
    d = trdd_dir(root)
    if not d.is_dir():
        return []
    out = []
    for f in sorted(d.glob("TRDD-*.md")):
        try:
            out.append(parse_trdd(f))
        except Exception as e:  # noqa: BLE001 - tool resilience
            print(f"warning: failed to parse {f.name}: {e}", file=sys.stderr)
    return out


# ───────────────── frontmatter parsing ─────────────────


def _parse_frontmatter(lines: list[str]) -> tuple[dict[str, Any], int]:
    """Parse YAML frontmatter delimited by `---` lines.

    Returns (frontmatter_dict, body_start_line_index).

    Hand-parser tuned for the PRRD/TRDD invariants:
    - one field per line: `key: value`
    - flow-style lists: `key: [a, b, c]`
    - bare enums: `key: dev`
    - quoted strings: `key: "value with spaces"`
    - booleans: true / false
    - ints: `key: 7`
    - null: null / ~ / (empty)
    - nested mappings are NOT supported (intentionally — invariant 1).
    """
    if not lines or lines[0].strip() != "---":
        return {}, 0
    fm: dict[str, Any] = {}
    end = 0
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i + 1
            break
    else:
        return {}, 0
    for line in lines[1 : end - 1]:
        # skip blanks and comment-only lines
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip()
        # strip inline comments AFTER a value (but allow # inside quoted strings)
        if val and not val.startswith(('"', "'", "[")):
            hashpos = val.find(" #")
            if hashpos != -1:
                val = val[:hashpos].rstrip()
        fm[key] = _coerce_yaml_value(val)
    return fm, end


def _coerce_yaml_value(val: str) -> Any:
    s = val.strip()
    if s == "" or s.lower() in ("null", "~"):
        return None
    if s.lower() == "true":
        return True
    if s.lower() == "false":
        return False
    # flow-style list
    if s.startswith("[") and s.endswith("]"):
        inner = s[1:-1].strip()
        if not inner:
            return []
        items = []
        for raw in _split_flow_items(inner):
            items.append(_coerce_yaml_value(raw))
        return items
    # quoted string
    if (s.startswith('"') and s.endswith('"')) or (
        s.startswith("'") and s.endswith("'")
    ):
        return s[1:-1]
    # int?
    if re.fullmatch(r"-?\d+", s):
        try:
            return int(s)
        except ValueError:
            pass
    # float?
    if re.fullmatch(r"-?\d+\.\d+", s):
        try:
            return float(s)
        except ValueError:
            pass
    # plain string
    return s


def _split_flow_items(inner: str) -> list[str]:
    """Split `a, b, [c, d]` on commas at top level (not inside nested brackets)."""
    out, depth, start = [], 0, 0
    for i, ch in enumerate(inner):
        if ch in "[(":
            depth += 1
        elif ch in "])":
            depth -= 1
        elif ch == "," and depth == 0:
            out.append(inner[start:i].strip())
            start = i + 1
    last = inner[start:].strip()
    if last:
        out.append(last)
    return out


# ───────────────── PRRD writing ─────────────────


def write_prrd(doc: PRRDDoc, path: Path | None = None) -> None:
    """Re-emit the PRRD file with current rules and frontmatter.

    Rules are sorted by number ascending within each section. The
    rest of the file body (non-rule lines) is preserved AS-IS via the
    raw_lines, with the rule lines re-rendered in place.
    """
    p = path or doc.path or prrd_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    # We rewrite the GOLDEN and SILVER sections from doc.rules; other
    # sections (overview, §0, etc.) are preserved by walking raw_lines.
    # For simplicity, we delegate full re-emission via render_prrd().
    p.write_text(render_prrd(doc), encoding="utf-8")


def render_prrd(doc: PRRDDoc) -> str:
    """Produce the canonical PRRD text from a PRRDDoc.

    If `doc.raw_lines` is present and contains the marker sections
    `## 🥇 GOLDEN` and `## 🥈 SILVER`, replace their body with the
    rendered rule lists; everything outside is preserved verbatim.

    Otherwise emit a minimal default layout.
    """
    if doc.raw_lines:
        return _render_prrd_preserving(doc)
    return _render_prrd_default(doc)


def _render_prrd_preserving(doc: PRRDDoc) -> str:
    lines = list(doc.raw_lines)
    # Sync the frontmatter dict back into the file (overwrites raw frontmatter)
    lines = _sync_frontmatter_dict(lines, doc.frontmatter)
    g_start, g_end = _find_section_bounds(lines, "🥇 GOLDEN")
    s_start, s_end = _find_section_bounds(lines, "🥈 SILVER")
    golden = sorted(doc.golden_rules(), key=lambda r: r.number)
    silver = sorted(doc.silver_rules(), key=lambda r: r.number)
    g_lines = [_render_rule_line(r) for r in golden]
    s_lines = [_render_rule_line(r) for r in silver]
    # Replace silver first to avoid index shifts when golden is earlier
    if s_start is not None and s_end is not None:
        lines = lines[: s_start + 1] + [""] + s_lines + [""] + lines[s_end:]
    if g_start is not None and g_end is not None:
        lines = lines[: g_start + 1] + [""] + g_lines + [""] + lines[g_end:]
    return "\n".join(lines) + ("\n" if lines and not lines[-1].endswith("\n") else "")


def _sync_frontmatter_dict(lines: list[str], fm: dict[str, Any]) -> list[str]:
    """Replace the frontmatter block (lines[0..end]) with `fm`'s contents.

    Preserves field order from the original frontmatter where possible;
    appends new fields at the end.
    """
    if not lines or lines[0].strip() != "---":
        return lines
    end = None
    original_keys: list[str] = []
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
        if ":" in lines[i] and not lines[i].lstrip().startswith("#"):
            k, _, _ = lines[i].partition(":")
            original_keys.append(k.strip())
    if end is None:
        return lines
    new_fm_lines = ["---"]
    written: set[str] = set()
    for k in original_keys:
        if k in fm:
            new_fm_lines.append(f"{k}: {_render_yaml_value(fm[k])}")
            written.add(k)
    for k, v in fm.items():
        if k not in written:
            new_fm_lines.append(f"{k}: {_render_yaml_value(v)}")
            written.add(k)
    new_fm_lines.append("---")
    return new_fm_lines + lines[end + 1 :]


def _render_yaml_value(v: Any) -> str:
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, list):
        return "[" + ", ".join(_render_yaml_value(x) for x in v) + "]"
    s = str(v)
    # Quote only if the string contains characters that would confuse the parser
    if any(ch in s for ch in (":", "#")) and not (
        s.startswith('"') or s.startswith("'")
    ):
        return f'"{s}"'
    return s


def _render_prrd_default(doc: PRRDDoc) -> str:
    from datetime import datetime

    now_iso = datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")
    now_iso = now_iso[:-2] + now_iso[-2:]  # keep ±HHMM compact
    fm = {
        "prrd-version": doc.frontmatter.get("prrd-version", "0.1"),
        "updated": now_iso,
        "project": doc.frontmatter.get("project", "unnamed-project"),
        "canonical-source": "design/requirements/PRRD.md",
        "mirrors": "[]",
    }
    out: list[str] = ["---"]
    for k, v in fm.items():
        out.append(f"{k}: {v}")
    out.append("---")
    out.append("")
    out.append("# Project Requirements & Rules")
    out.append("")
    out.append("## §I. How to read this document")
    out.append("")
    out.append("Rule citation form: `PRRD G<n>.<v>` or `PRRD S<n>.<v>`. See")
    out.append("`~/.claude/rules/prrd-design-rules.md` for the full spec.")
    out.append("")
    out.append("## 🥇 GOLDEN — set by the USER (immutable to MANAGER)")
    out.append("")
    for r in sorted(doc.golden_rules(), key=lambda r: r.number):
        out.append(_render_rule_line(r))
    out.append("")
    out.append("## 🥈 SILVER — MANAGER-mutable (agents propose via COS)")
    out.append("")
    for r in sorted(doc.silver_rules(), key=lambda r: r.number):
        out.append(_render_rule_line(r))
    out.append("")
    return "\n".join(out)


def _render_rule_line(r: PRRDRule) -> str:
    return f"- **{r.kind}{r.number}.{r.version}** — {r.text}"


def _find_section_bounds(
    lines: list[str], section_marker: str
) -> tuple[int | None, int | None]:
    """Find the index of the section header line containing `section_marker`,
    plus the index of the NEXT `## ` header (or EOF). Returns (start, end)
    where lines[start] is the header and lines[end] is the next header (or len).
    """
    start = None
    for i, ln in enumerate(lines):
        if ln.startswith("## ") and section_marker in ln:
            start = i
            break
    if start is None:
        return None, None
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("## ") or lines[j].startswith("# "):
            return start, j
    return start, len(lines)


# ───────────────── filter / query helpers ─────────────────


def matches_where(trdd: TRDDDoc, where: str) -> bool:
    """SQL-ish where clause: 'column=blocked AND priority<3'.

    Supported operators: =, !=, <, <=, >, >=, IN (...).
    Connectors: AND, OR (case-insensitive).
    Field names are TRDD frontmatter field names.
    """
    if not where:
        return True
    # Tokenize on AND/OR (we don't support parens here)
    tokens = re.split(r"\s+(AND|OR|and|or)\s+", where)
    # Even indices: clauses; odd indices: connectors
    result = _eval_clause(trdd, tokens[0])
    i = 1
    while i < len(tokens) - 1:
        connector = tokens[i].upper()
        clause_val = _eval_clause(trdd, tokens[i + 1])
        if connector == "AND":
            result = result and clause_val
        elif connector == "OR":
            result = result or clause_val
        i += 2
    return result


def _eval_clause(trdd: TRDDDoc, clause: str) -> bool:
    clause = clause.strip()
    m = re.match(
        r"^(?P<f>[a-zA-Z][\w-]*)\s*(?P<op>=|!=|<|<=|>|>=|IN|NOT IN|in|not in)\s*(?P<rhs>.+)$",
        clause,
    )
    if not m:
        return False
    field = m.group("f")
    op = m.group("op").upper()
    rhs = m.group("rhs").strip()
    value = trdd.frontmatter.get(field)
    if op in ("=", "!="):
        # Quote-strip RHS
        rhs_v = rhs.strip("'\"")
        eq = str(value) == rhs_v
        return eq if op == "=" else not eq
    if op in ("<", "<=", ">", ">="):
        try:
            v = float(value) if value is not None else float("-inf")
            r = float(rhs)
        except (TypeError, ValueError):
            return False
        return {"<": v < r, "<=": v <= r, ">": v > r, ">=": v >= r}[op]
    if op == "IN":
        # `IN (a, b, c)` or `IN [a, b, c]`
        inner = rhs.strip("()[]")
        items = [s.strip().strip("'\"") for s in inner.split(",")]
        if isinstance(value, list):
            return any(str(v) in items for v in value)
        return str(value) in items
    if op == "NOT IN":
        inner = rhs.strip("()[]")
        items = [s.strip().strip("'\"") for s in inner.split(",")]
        if isinstance(value, list):
            return not any(str(v) in items for v in value)
        return str(value) not in items
    return False


# ───────────────── authority check ─────────────────


def caller_is_manager() -> bool:
    """Cheap, conservative check. Returns True if AID_AUTH resolves to
    a MANAGER title via the AI Maestro server, OR if --user override is
    in effect (set via AMAMA_PRRD_TRUST=1 env var).

    We don't import requests; we use curl via subprocess.
    """
    if os.environ.get("AMAMA_PRRD_TRUST") == "1":
        return True
    aid = os.environ.get("AID_AUTH", "")
    api = os.environ.get("AIMAESTRO_API", "http://localhost:23000").rstrip("/")
    if not aid:
        return False
    import subprocess

    # DECOUPLE-BLOCKED ai-maestro#36 — per MANAGER core#11 (no plugin calls the
    # server /api/* directly), this MANAGER-title check must repoint to the frozen
    # CLI (aid-governance / aid-whoami). Those verbs are NOT yet installed (they
    # land via ai-maestro#36); until then this direct /api/governance call stays
    # functional. Flip to the CLI once the verb lands — do NOT patch installed
    # scripts (FROZEN-interface invariant, assistant-manager#16).
    # Build the auth header for the LOCAL AI Maestro server (localhost API).
    # Assembled in a named variable (not an inline f-string in the argv) so
    # the intent — authenticating to our own server, not shipping a token to
    # a third party — is explicit and auditable.
    auth_header = "Authorization: Bearer " + aid
    try:
        r = subprocess.run(
            [
                "curl",
                "-fsS",
                "-H",
                auth_header,
                "--max-time",
                "3",
                f"{api}/api/governance",
            ],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if r.returncode != 0:
            return False
        data = json.loads(r.stdout or "{}")
        # Conservative: look for any field that looks like a MANAGER title.
        for v in data.values():
            if isinstance(v, str) and v.lower() == "manager":
                return True
        return False
    except (subprocess.SubprocessError, OSError, ValueError, json.JSONDecodeError):
        return False


# ───────────────── error helpers ─────────────────


def die(msg: str, code: int = 1) -> NoReturn:
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(code)


def warn(msg: str) -> None:
    print(f"warning: {msg}", file=sys.stderr)
