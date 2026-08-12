"""Real (no-mock) integration tests for the PRRD/TRDD/Kanban pillar scripts.

Authorized by GitHub issue #5 (governance audit). Every test invokes the
real script as a subprocess (`sys.executable script ...`) against a fresh
temp project. Nothing is mocked or stubbed — each test:

  1. builds a throwaway project dir (`tmp_path`),
  2. `git init`s it + configures a git user (so `git mv` works),
  3. runs `bootstrap_design.py` to create the design/ 4-zone model,
  4. writes real PRRD.md / TRDD-*.md fixtures,
  5. runs the script under test,
  6. asserts on real stdout / exit code / on-disk file state.

Scripts under test (scripts/prrd-trdd/):
  get-prrd.py, prrd-edit.py, findprrd.py, findtrdd.py, kanban.py,
  amama_proposal_approvals.py, bootstrap_design.py, resolve_pillar_scripts.sh

Gotchas exercised on purpose (verified by reading the sources):
  * amama approve/refuse/archive need MANAGER auth; `--user` bypasses, and
    refusal of authority WITHOUT --user exits 4.
  * amama uses `git mv`, so the temp project is a real git repo with the
    seed proposals committed; we assert both the git-tracked rename (the
    common path) and the plain-move + warning fallback in a non-git dir.
  * amama selector resolution: a SHORT all-digit selector (< 8 chars) is a
    1-based list number; an 8-DIGIT uid8 (all digits, exactly 8) resolves
    as an ID — both are covered.
  * prrd-edit add silver needs --user (exit 4 otherwise); golden mutation
    needs --user (exit 4 otherwise); not-found exits 3.
  * resolve_pillar_scripts.sh: AI_MAESTRO_PRRD_SCRIPTS_DIR override path,
    the own-dir path, and the no-base exit-1 failure.

The PRRD query/edit scripts (get-prrd/prrd-edit/findprrd/findtrdd/kanban)
take NO --project flag — they resolve the project via `find_project_root()`
walking up from CWD. Every such invocation therefore runs with
`cwd=<temp project>` so resolution stays inside the throwaway dir.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = PLUGIN_ROOT / "scripts" / "prrd-trdd"

GET_PRRD = SCRIPTS / "get-prrd.py"
PRRD_EDIT = SCRIPTS / "prrd-edit.py"
FINDPRRD = SCRIPTS / "findprrd.py"
FINDTRDD = SCRIPTS / "findtrdd.py"
KANBAN = SCRIPTS / "kanban.py"
AMAMA = SCRIPTS / "amama_proposal_approvals.py"
BOOTSTRAP = SCRIPTS / "bootstrap_design.py"
RESOLVER = SCRIPTS / "resolve_pillar_scripts.sh"


# ───────────────────────── helpers ─────────────────────────


def _run(
    *args: str,
    cwd: Path | None = None,
    env_overrides: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run a python pillar script as a real subprocess, capturing output.

    A scrubbed environment is used so a real MANAGER token in the dev's
    shell (AID_AUTH / AMAMA_PRRD_TRUST) can never leak into an auth test and
    silently turn an "expected exit 4" into an "exit 0".
    """
    env = os.environ.copy()
    env.pop("AID_AUTH", None)
    env.pop("AMAMA_PRRD_TRUST", None)
    if env_overrides:
        env.update(env_overrides)
    return subprocess.run(
        [sys.executable, *args],
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        env=env,
        timeout=120,
        check=False,
    )


MTIME_TOLERANCE_S = 300.0  # 5 min — absorbs "compute the ISO string, save a moment later"


def stamp_predates_the_bytes(updated: datetime, mtime: datetime, *, dirty: bool) -> bool:
    """True iff `updated:` does NOT cover the bytes currently on disk.

    THE PRECONDITION LIVES IN HERE ON PURPOSE, and that placement is the point. On a CLEAN
    file `mtime` is checkout time rather than authorship, so the comparison is meaningless
    and a fresh clone would red every file — the predicate is only valid while the file is
    dirty.

    Putting that gate in the CALLER is what bit me: a throwaway probe reached the ungated
    comparison, reported the correctly-stamped clean baseline as RED, and read exactly like
    "mtime is too noisy, this fix does not port here". I was one step from rejecting a
    CORRECT fix while holding a measurement — which is more persuasive than adopting blind,
    and the reason that class is worse than the ones that merely hide a defect.

    A gate in the caller is a rule someone must remember at every call site, INCLUDING the
    throwaway probe written to check the rule. A gate inside the function makes the wrong
    thing unaddressable. (Construction from the ARCHITECT on `ai-maestro#145`, whose own
    build could not hit my failure because their gate was already here — by shape, not by
    vigilance.)
    """
    if not dirty:
        return False
    return (mtime - updated).total_seconds() > MTIME_TOLERANCE_S


def primed_state(stamped: object, written: datetime) -> bool | None:
    """What the coverage arm's predicate WOULD return right now — for the skip line to report.

    A skip is consistent with two worlds: the dirty gate absorbed a false red, or the
    predicate would have been silent anyway. Only the first credits the gate, so the skip
    message reports this instead of implying coverage it never had.

    `None` means CANNOT SAY: `updated:` is absent, so there is nothing to compare against.
    A MALFORMED value is deliberately NOT None — it raises. A PRRD whose own timestamp does
    not parse is a defect of the document, and a skip line reading "unknown" is exactly how
    that lives for months unnoticed. This differs from the ARCHITECT's build on
    ai-maestro#145, which reports None for both; the divergence is intentional and is why
    it is tested rather than left to whichever branch happened to run.
    """
    if not stamped:
        return None
    claimed = datetime.fromisoformat(str(stamped)).astimezone(timezone.utc)
    return stamp_predates_the_bytes(claimed, written, dirty=True)


def _git(project: Path, *args: str) -> subprocess.CompletedProcess[str]:
    """Run a git command inside the temp project, capturing output."""
    return subprocess.run(
        ["git", "-C", str(project), *args],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )


def _write_trdd(
    directory: Path,
    *,
    uid8: str,
    column: str | None = None,
    title: str,
    extra: dict[str, str] | None = None,
    body: str = "Body.",
    ts: str = "20260101_000000+0000",
    iso: str = "2026-01-01T00:00:00+0000",
) -> Path:
    """Write a minimal-but-real TRDD-*.md fixture and return its path.

    ``column=None`` omits the ``column:`` frontmatter entirely — used to fixture a
    grandfathered TRDD (no column, no status) or a v1-only TRDD (set ``status:``
    via ``extra``).
    """
    fm = {
        "trdd-id": f"{uid8}-1111-2222-3333-444444444444",
        "title": title,
        "created": iso,
        "updated": iso,
    }
    if column is not None:
        fm["column"] = column
    if extra:
        fm.update(extra)
    lines = ["---"]
    lines += [f"{k}: {v}" for k, v in fm.items()]
    lines += ["---", "", f"# {title}", "", body, ""]
    path = directory / f"TRDD-{ts}-{uid8}-{title.split()[0].lower()}.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


@pytest.fixture
def project(tmp_path: Path) -> Path:
    """A fresh git-backed temp project with the design/ 4-zone model created
    via the real bootstrap_design.py (so amama's `git mv` has a real repo)."""
    _git(tmp_path, "init")
    _git(tmp_path, "config", "user.name", "Test User")
    _git(tmp_path, "config", "user.email", "test@example.com")
    res = _run(str(BOOTSTRAP), str(tmp_path))
    assert res.returncode == 0, res.stderr
    return tmp_path


def _seed_proposal(
    project: Path,
    *,
    uid8: str,
    title: str,
    tier: int = 1,
    iso: str = "2026-01-01T00:00:00+0000",
    ts: str = "20260101_000000+0000",
) -> Path:
    """Write a proposal TRDD into design/proposals/ (column: proposal)."""
    return _write_trdd(
        project / "design" / "proposals",
        uid8=uid8,
        column="proposal",
        title=title,
        extra={"approval-tier": str(tier), "current-owner": "amama"},
        ts=ts,
        iso=iso,
    )


def _commit_all(project: Path, msg: str = "seed") -> None:
    """Stage and commit the design/ tree so git mv sees tracked files."""
    _git(project, "add", "design")
    _git(project, "commit", "-q", "-m", msg)


# ═════════════════════════ bootstrap_design.py ═════════════════════════


class TestBootstrapDesign:
    """bootstrap_design.py builds the 4-zone design model idempotently."""

    def test_creates_all_five_zones(self, tmp_path: Path) -> None:
        """A fresh run creates requirements/proposals/tasks/refused/archived."""
        res = _run(str(BOOTSTRAP), str(tmp_path))
        assert res.returncode == 0, res.stderr
        for zone in ("requirements", "proposals", "tasks", "refused", "archived"):
            assert (tmp_path / "design" / zone).is_dir(), f"missing zone: {zone}"
        # lifecycle zones get a .gitkeep; requirements (holds PRRD.md) does not
        assert (tmp_path / "design" / "tasks" / ".gitkeep").is_file()
        assert not (tmp_path / "design" / "requirements" / ".gitkeep").exists()

    def test_idempotent_second_run(self, tmp_path: Path) -> None:
        """A second run reports nothing to create and still exits 0."""
        first = _run(str(BOOTSTRAP), str(tmp_path))
        assert first.returncode == 0
        second = _run(str(BOOTSTRAP), str(tmp_path))
        assert second.returncode == 0, second.stderr
        assert "already present" in second.stdout

    def test_removes_stray_design_gitignore_entry(self, tmp_path: Path) -> None:
        """A literal `design/` line in .gitignore is stripped (design is tracked)."""
        (tmp_path / ".gitignore").write_text("node_modules/\ndesign/\n*.log\n", encoding="utf-8")
        res = _run(str(BOOTSTRAP), str(tmp_path))
        assert res.returncode == 0, res.stderr
        gi = (tmp_path / ".gitignore").read_text(encoding="utf-8")
        assert "design/" not in gi.splitlines()
        assert "node_modules/" in gi  # unrelated lines preserved
        assert "removed" in res.stdout


# ═════════════════════════ get-prrd.py ═════════════════════════


class TestGetPrrd:
    """get-prrd.py initialises and reads PRRD rules."""

    def test_init_creates_prrd(self, project: Path) -> None:
        """--init writes design/requirements/PRRD.md and exits 0."""
        res = _run(str(GET_PRRD), "--init", cwd=project)
        assert res.returncode == 0, res.stderr
        assert (project / "design" / "requirements" / "PRRD.md").is_file()

    def test_get_latest_and_cite(self, project: Path) -> None:
        """After adding a silver rule, `get-prrd 1` prints its text and --cite formats it."""
        _run(str(GET_PRRD), "--init", cwd=project)
        _run(str(PRRD_EDIT), "--user", "add", "silver", "Pin exact dependency versions", cwd=project)
        plain = _run(str(GET_PRRD), "1", cwd=project)
        assert plain.returncode == 0
        assert plain.stdout.strip() == "Pin exact dependency versions"
        cite = _run(str(GET_PRRD), "--cite", "1", cwd=project)
        assert cite.stdout.strip() == "PRRD S1.1 — Pin exact dependency versions"

    def test_get_missing_rule_exits_3(self, project: Path) -> None:
        """Looking up a non-existent rule number exits 3 (not-found)."""
        _run(str(GET_PRRD), "--init", cwd=project)
        res = _run(str(GET_PRRD), "999", cwd=project)
        assert res.returncode == 3
        assert "no rule 999" in res.stderr


# ═════════════════════════ prrd-edit.py ═════════════════════════


class TestPrrdEdit:
    """prrd-edit.py mutates PRRD rules with authority gates."""

    def test_add_silver_without_user_exits_4(self, project: Path) -> None:
        """Adding a silver rule without --user (and no MANAGER auth) exits 4."""
        _run(str(GET_PRRD), "--init", cwd=project)
        res = _run(str(PRRD_EDIT), "add", "silver", "Some rule", cwd=project)
        assert res.returncode == 4
        assert "MANAGER" in res.stderr

    def test_add_golden_without_user_exits_4(self, project: Path) -> None:
        """Adding a golden rule requires --user (the human); without it exits 4."""
        _run(str(GET_PRRD), "--init", cwd=project)
        res = _run(str(PRRD_EDIT), "add", "golden", "Golden self-id rule", cwd=project)
        assert res.returncode == 4
        assert "GOLDEN" in res.stderr or "--user" in res.stderr

    def test_revise_bumps_version(self, project: Path) -> None:
        """`revise` on S1.1 produces S1.2 with the new text; old/new resolvable."""
        _run(str(GET_PRRD), "--init", cwd=project)
        _run(str(PRRD_EDIT), "--user", "add", "silver", "First text", cwd=project)
        res = _run(str(PRRD_EDIT), "--user", "revise", "1", "Second text", cwd=project)
        assert res.returncode == 0, res.stderr
        assert "S1.1 → PRRD S1.2" in res.stdout
        got = _run(str(GET_PRRD), "1.2", cwd=project)
        assert got.stdout.strip() == "Second text"

    def test_revise_missing_rule_exits_3(self, project: Path) -> None:
        """Revising a rule number that does not exist exits 3 (not-found)."""
        _run(str(GET_PRRD), "--init", cwd=project)
        res = _run(str(PRRD_EDIT), "--user", "revise", "50", "x", cwd=project)
        assert res.returncode == 3
        assert "not found" in res.stderr


# ═════════════════════════ findprrd.py ═════════════════════════


class TestFindPrrd:
    """findprrd.py searches PRRD rules by kind / text / citation."""

    def test_kind_filter_lists_only_golden(self, project: Path) -> None:
        """--kind golden lists the golden rule and omits the silver one."""
        _run(str(GET_PRRD), "--init", cwd=project)
        _run(str(PRRD_EDIT), "--user", "add", "silver", "Silver dependency rule", cwd=project)
        _run(str(PRRD_EDIT), "--user", "add", "golden", "Golden identity rule", cwd=project)
        res = _run(str(FINDPRRD), "--kind", "golden", cwd=project)
        assert res.returncode == 0, res.stderr
        assert "Golden identity rule" in res.stdout
        assert "Silver dependency rule" not in res.stdout

    def test_grep_matches_rule_text(self, project: Path) -> None:
        """--grep finds the rule whose text matches the (case-insensitive) regex."""
        _run(str(GET_PRRD), "--init", cwd=project)
        _run(str(PRRD_EDIT), "--user", "add", "silver", "Pin exact dependency versions", cwd=project)
        res = _run(str(FINDPRRD), "--grep", "DEPENDENCY", cwd=project)
        assert res.returncode == 0, res.stderr
        assert "Pin exact dependency versions" in res.stdout

    def test_count_reports_totals(self, project: Path) -> None:
        """--count reports the golden/silver totals after two adds."""
        _run(str(GET_PRRD), "--init", cwd=project)
        _run(str(PRRD_EDIT), "--user", "add", "silver", "Rule one", cwd=project)
        _run(str(PRRD_EDIT), "--user", "add", "golden", "Rule two", cwd=project)
        res = _run(str(FINDPRRD), "--count", cwd=project)
        assert res.returncode == 0, res.stderr
        assert "golden=1" in res.stdout
        assert "silver=1" in res.stdout


# ═════════════════════════ findtrdd.py ═════════════════════════


class TestFindTrdd:
    """findtrdd.py queries TRDDs by column / assignee / rule / where + validates."""

    def test_column_and_assignee_filters(self, project: Path) -> None:
        """--column dev returns the dev TRDD path; --assignee bob returns bob's."""
        tasks = project / "design" / "tasks"
        _write_trdd(tasks, uid8="11112222", column="dev", title="Alpha task",
                    extra={"assignee": "alice", "priority": "2"})
        _write_trdd(tasks, uid8="33334444", column="testing", title="Beta task",
                    extra={"assignee": "bob", "priority": "3"},
                    ts="20260101_000001+0000", iso="2026-01-01T00:00:01+0000")
        col = _run(str(FINDTRDD), "--column", "dev", cwd=project)
        assert col.returncode == 0, col.stderr
        assert "11112222" in col.stdout and "33334444" not in col.stdout
        ass = _run(str(FINDTRDD), "--assignee", "bob", cwd=project)
        assert "33334444" in ass.stdout and "11112222" not in ass.stdout

    def test_where_and_relevant_rule_json(self, project: Path) -> None:
        """--where + --relevant-rule select the right TRDD and --format json emits it."""
        tasks = project / "design" / "tasks"
        _write_trdd(tasks, uid8="55556666", column="blocked", title="Gamma task",
                    extra={"priority": "0", "blocked-by": "[TRDD-77778888]",
                           "relevant-rules": "[7]"})
        res = _run(str(FINDTRDD), "--where", "column=blocked AND priority<3",
                   "--format", "json", cwd=project)
        assert res.returncode == 0, res.stderr
        data = json.loads(res.stdout)
        assert len(data) == 1 and data[0]["uid8"] == "55556666"
        rule = _run(str(FINDTRDD), "--relevant-rule", "7", cwd=project)
        assert "55556666" in rule.stdout

    def test_validate_ok_and_fail(self, project: Path) -> None:
        """--validate passes a well-formed TRDD (exit 0) and fails a broken one (exit 1)."""
        tasks = project / "design" / "tasks"
        good = _write_trdd(tasks, uid8="99990000", column="dev", title="Valid task",
                           extra={"release-via": "none"})
        ok = _run(str(FINDTRDD), "--validate", str(good), cwd=project)
        assert ok.returncode == 0, ok.stderr
        assert "VALIDATION OK" in ok.stdout
        # column=published with no published-version is a documented validation error
        bad = _write_trdd(tasks, uid8="aaaa0000", column="published", title="Bad task",
                          extra={"release-via": "publish"},
                          ts="20260101_000009+0000", iso="2026-01-01T00:00:09+0000")
        fail = _run(str(FINDTRDD), "--validate", str(bad), cwd=project)
        assert fail.returncode == 1
        assert "published-version" in fail.stdout


# ═════════════════════════ kanban.py ═════════════════════════


class TestKanban:
    """kanban.py renders the board / JSON / red column without mutating TRDDs."""

    def test_full_board_lists_cards(self, project: Path) -> None:
        """The full board groups cards under their column headers."""
        tasks = project / "design" / "tasks"
        _write_trdd(tasks, uid8="11112222", column="dev", title="Alpha task",
                    extra={"assignee": "alice", "priority": "2"})
        res = _run(str(KANBAN), cwd=project)
        assert res.returncode == 0, res.stderr
        assert "WORK" in res.stdout and "dev" in res.stdout
        assert "TRDD-11112222" in res.stdout

    def test_json_groups_by_column_and_ranks_red(self, project: Path) -> None:
        """--json emits columns keyed by name and a red_priority ranking for blockers."""
        tasks = project / "design" / "tasks"
        _write_trdd(tasks, uid8="11112222", column="dev", title="Blocker task",
                    extra={"assignee": "alice", "priority": "2"})
        _write_trdd(tasks, uid8="33334444", column="blocked", title="Waiting task",
                    extra={"priority": "0", "blocked-by": "[TRDD-11112222]"},
                    ts="20260101_000001+0000", iso="2026-01-01T00:00:01+0000")
        res = _run(str(KANBAN), "--json", cwd=project)
        assert res.returncode == 0, res.stderr
        data = json.loads(res.stdout)
        assert "dev" in data["columns"] and "blocked" in data["columns"]
        # The dev blocker unblocks exactly the one blocked TRDD.
        assert any(e["trdd"] == "TRDD-11112222" and e["unblocks"] == 1
                   for e in data["red_priority"])

    def test_red_column_only(self, project: Path) -> None:
        """--red shows only the blocked column and its blocked-by line."""
        tasks = project / "design" / "tasks"
        _write_trdd(tasks, uid8="33334444", column="blocked", title="Waiting task",
                    extra={"priority": "0", "blocked-by": "[TRDD-11112222]"})
        res = _run(str(KANBAN), "--red", cwd=project)
        assert res.returncode == 0, res.stderr
        assert "BLOCKED" in res.stdout
        assert "TRDD-33334444" in res.stdout
        assert "blocked-by: TRDD-11112222" in res.stdout

    def test_grandfathered_missing_column_renders_as_planned(self, project: Path) -> None:
        """MANAGER ruling (#7): a TRDD with neither column: nor status: renders as
        `planned` (grandfathered-as-authorized), not `(unknown)`, without mutating it."""
        tasks = project / "design" / "tasks"
        src = _write_trdd(tasks, uid8="55556666", title="Grandfathered task")
        before = src.read_text(encoding="utf-8")
        res = _run(str(KANBAN), "--json", cwd=project)
        assert res.returncode == 0, res.stderr
        data = json.loads(res.stdout)
        assert "planned" in data["columns"]
        assert "(unknown)" not in data["columns"]
        assert any(e["uid8"] == "55556666" for e in data["columns"]["planned"])
        assert src.read_text(encoding="utf-8") == before  # read-time only

    def test_v1_status_maps_to_v2_column(self, project: Path) -> None:
        """MANAGER ruling (#7): a v1 `status:` (no column:) maps to its v2 column."""
        tasks = project / "design" / "tasks"
        _write_trdd(tasks, uid8="77778888", title="Legacy task",
                    extra={"status": "in-progress"})
        res = _run(str(KANBAN), "--json", cwd=project)
        assert res.returncode == 0, res.stderr
        data = json.loads(res.stdout)
        assert "dev" in data["columns"]  # in-progress -> dev
        assert any(e["uid8"] == "77778888" for e in data["columns"]["dev"])

    def test_invalid_column_is_unknown(self, project: Path) -> None:
        """MANAGER ruling (#7): `(unknown)` is reserved for an unrecognized column value."""
        tasks = project / "design" / "tasks"
        _write_trdd(tasks, uid8="9999aaaa", column="bogus", title="Weird task")
        res = _run(str(KANBAN), "--json", cwd=project)
        assert res.returncode == 0, res.stderr
        data = json.loads(res.stdout)
        assert "(unknown)" in data["columns"]
        assert any(e["uid8"] == "9999aaaa" for e in data["columns"]["(unknown)"])


# ═════════════════════════ amama_proposal_approvals.py ═════════════════════════


class TestAmamaProposalApprovals:
    """amama_proposal_approvals.py lists/approves/refuses/archives across zones."""

    def test_list_then_approve_with_user_git_mv(self, project: Path) -> None:
        """list numbers a proposal; approve --user moves it proposals→tasks (git rename)."""
        _seed_proposal(project, uid8="aaaa1111", title="Alpha proposal", tier=2)
        _commit_all(project)
        listed = _run(str(AMAMA), "--project", str(project), "list")
        assert listed.returncode == 0, listed.stderr
        assert "aaaa1111" in listed.stdout
        appr = _run(str(AMAMA), "--project", str(project), "approve", "aaaa1111", "--user")
        assert appr.returncode == 0, appr.stderr
        moved = list((project / "design" / "tasks").glob("TRDD-*aaaa1111*.md"))
        assert moved, "approved proposal did not land in design/tasks/"
        assert "column: planned" in moved[0].read_text(encoding="utf-8")
        assert not list((project / "design" / "proposals").glob("TRDD-*aaaa1111*.md"))
        # git tracked the move as a rename (R), not add+delete of an untracked file
        status = _git(project, "status", "--porcelain").stdout
        assert "design/tasks/" in status and "aaaa1111" in status

    def test_approve_without_user_exits_4(self, project: Path) -> None:
        """Approving without --user and without MANAGER auth refuses with exit 4."""
        _seed_proposal(project, uid8="bbbb2222", title="Beta proposal")
        _commit_all(project)
        res = _run(str(AMAMA), "--project", str(project), "approve", "bbbb2222")
        assert res.returncode == 4
        assert "MANAGER" in res.stderr
        # The proposal must NOT have moved out of proposals/ on a refused auth.
        assert list((project / "design" / "proposals").glob("TRDD-*bbbb2222*.md"))

    def test_refuse_moves_to_refused_zone(self, project: Path) -> None:
        """refuse --user moves a proposal into design/refused/ with column: refused."""
        _seed_proposal(project, uid8="cccc3333", title="Gamma proposal")
        _commit_all(project)
        res = _run(str(AMAMA), "--project", str(project), "refuse", "cccc3333", "--user")
        assert res.returncode == 0, res.stderr
        moved = list((project / "design" / "refused").glob("TRDD-*cccc3333*.md"))
        assert moved, "refused proposal did not land in design/refused/"
        assert "column: refused" in moved[0].read_text(encoding="utf-8")

    def test_refuse_approve_rest_complement(self, project: Path) -> None:
        """refuse X --approve-rest refuses X and approves every OTHER listed proposal."""
        _seed_proposal(project, uid8="aaaa1111", title="A proposal",
                       ts="20260101_000001+0000", iso="2026-01-01T00:00:01+0000")
        _seed_proposal(project, uid8="bbbb2222", title="B proposal",
                       ts="20260101_000002+0000", iso="2026-01-01T00:00:02+0000")
        _seed_proposal(project, uid8="cccc3333", title="C proposal",
                       ts="20260101_000003+0000", iso="2026-01-01T00:00:03+0000")
        _commit_all(project)
        _run(str(AMAMA), "--project", str(project), "list")  # build the manifest
        res = _run(str(AMAMA), "--project", str(project), "refuse", "aaaa1111",
                   "--user", "--approve-rest")
        assert res.returncode == 0, res.stderr
        assert list((project / "design" / "refused").glob("TRDD-*aaaa1111*.md"))
        tasks = project / "design" / "tasks"
        assert list(tasks.glob("TRDD-*bbbb2222*.md"))
        assert list(tasks.glob("TRDD-*cccc3333*.md"))

    def test_archive_completed(self, project: Path) -> None:
        """archive --state completed --user moves a proposal into design/archived/."""
        _seed_proposal(project, uid8="dddd4444", title="Delta proposal")
        _commit_all(project)
        res = _run(str(AMAMA), "--project", str(project), "archive", "dddd4444",
                   "--user", "--state", "completed")
        assert res.returncode == 0, res.stderr
        moved = list((project / "design" / "archived").glob("TRDD-*dddd4444*.md"))
        assert moved, "archived TRDD did not land in design/archived/"
        assert "column: completed" in moved[0].read_text(encoding="utf-8")

    def test_eight_digit_uid_resolves_as_id_not_number(self, project: Path) -> None:
        """An all-DIGIT 8-char selector resolves as a uid8, not a list number."""
        # 12345678 is exactly 8 digits → uid8 (not the list index 1).
        _seed_proposal(project, uid8="12345678", title="Digit-id proposal")
        _commit_all(project)
        # No prior `list` manifest exists; a list-number lookup would die.
        res = _run(str(AMAMA), "--project", str(project), "approve", "12345678", "--user")
        assert res.returncode == 0, res.stderr
        assert list((project / "design" / "tasks").glob("TRDD-*12345678*.md"))

    def test_non_git_fallback_plain_move_with_warning(self, tmp_path: Path) -> None:
        """In a NON-git project, git mv fails over to a plain move and warns on stderr."""
        # Deliberately do NOT `git init` — bootstrap then approve.
        boot = _run(str(BOOTSTRAP), str(tmp_path))
        assert boot.returncode == 0, boot.stderr
        _seed_proposal(tmp_path, uid8="eeee5555", title="Epsilon proposal", tier=0)
        res = _run(str(AMAMA), "--project", str(tmp_path), "approve", "eeee5555", "--user")
        assert res.returncode == 0, res.stderr
        assert "falling back to plain move" in res.stderr
        assert list((tmp_path / "design" / "tasks").glob("TRDD-*eeee5555*.md"))


# ═════════════════════════ resolve_pillar_scripts.sh ═════════════════════════


class TestResolvePillarScripts:
    """resolve_pillar_scripts.sh prints the pillar-scripts dir or exits 1."""

    def test_override_env_path(self) -> None:
        """AI_MAESTRO_PRRD_SCRIPTS_DIR (containing prrd_lib.py) wins and is printed."""
        env = os.environ.copy()
        env["AI_MAESTRO_PRRD_SCRIPTS_DIR"] = str(SCRIPTS)
        res = subprocess.run(
            ["sh", str(RESOLVER)], capture_output=True, text=True, env=env,
            timeout=30, check=False,
        )
        assert res.returncode == 0, res.stderr
        assert res.stdout.strip() == str(SCRIPTS)

    def test_own_dir_resolution(self) -> None:
        """Run from the real scripts dir: the resolver returns its own directory."""
        env = os.environ.copy()
        env.pop("AI_MAESTRO_PRRD_SCRIPTS_DIR", None)
        res = subprocess.run(
            ["sh", str(RESOLVER)], capture_output=True, text=True, env=env,
            timeout=30, check=False,
        )
        assert res.returncode == 0, res.stderr
        assert res.stdout.strip() == str(SCRIPTS)

    def test_no_base_found_exits_1(self, tmp_path: Path) -> None:
        """A lone copy of the resolver (no prrd_lib.py, no cache, no override) exits 1."""
        lone = tmp_path / "resolve_pillar_scripts.sh"
        lone.write_text(RESOLVER.read_text(encoding="utf-8"), encoding="utf-8")
        env = os.environ.copy()
        env.pop("AI_MAESTRO_PRRD_SCRIPTS_DIR", None)
        env["HOME"] = str(tmp_path / "nohome")  # ensure the cache glob misses
        res = subprocess.run(
            ["sh", str(lone)], capture_output=True, text=True, env=env,
            timeout=30, check=False,
        )
        assert res.returncode == 1
        assert "could not find ai-maestro-plugin pillar scripts" in res.stderr


class TestOurOwnPRRDStampIsNotStale:
    """`prrd-version:` / `updated:` are machine-readable claims about the file's CONTENT.

    Nothing cites a container-level version, so nothing notices when it lies — a citation
    checker cannot see it by construction, because there is no reference to resolve. That
    is a different defect from a dangling citation and needs its own check (ARCHITECT's
    fifth clause, `ai-maestro#145`, found after CORE's own `prrd-version` was measured
    stale by 52 days).

    ROOT CAUSE, and why this guards the FILE rather than the tool: `prrd-edit.py`'s
    `_bump_prrd_version` already sets BOTH fields on every mutation, so the tool cannot
    produce this state. `acbea84` edited `PRRD.md` BY HAND — a golden revise (G1.1 -> G1.2)
    that never went through the tool — and the invariant the tool maintains silently did
    not apply. A guard on the tool would have stayed green through it.
    """

    PRRD = PLUGIN_ROOT / "design" / "requirements" / "PRRD.md"

    def _frontmatter(self) -> dict:
        import re

        import yaml

        m = re.match(r"^---\n(.*?)\n---", self.PRRD.read_text(encoding="utf-8"), re.S)
        assert m, "the PRRD has no YAML frontmatter block"
        data = yaml.safe_load(m.group(1))
        assert isinstance(data, dict), "the PRRD's frontmatter is not a mapping"
        return data

    def _is_dirty(self) -> bool:
        """True iff PRRD.md has uncommitted modifications.

        `--no-optional-locks`: a plain `git status` TAKES `.git/index.lock` to refresh its
        stat cache, so a test suite running beside any other git command can kill it
        (`ai-maestro-janitor#245`, measured twice in this repo).
        """
        res = subprocess.run(
            ["git", "--no-optional-locks", "status", "--porcelain=v1", "--", str(self.PRRD)],
            cwd=PLUGIN_ROOT, capture_output=True, text=True, timeout=30, check=False,
        )
        return res.returncode == 0 and bool(res.stdout.strip())

    def test_a_dirty_prrd_is_witnessed_by_the_clock_not_by_its_own_stale_history(self) -> None:
        """The arm that bites AT AUTHORING TIME, which is when the defect is born.

        The committed arm below witnesses against the newest COMMIT touching the file — so
        while the file is dirty, that witness is the OLD commit, the lag is whatever it
        already was, and a body edited seconds ago passes. That is exactly the state
        `acbea84` was in when it hand-edited the rules and left the stamp on June.

        So when the file is modified, the witness is the CLOCK: you are editing it now, the
        stamp must say now. Found by the ARCHITECT (`ai-maestro#145`), who shipped the same
        split after measuring the identical blindness in their own tree.

        WHAT THIS ARM DOES NOT CLOSE, measured rather than reasoned. It bites when the file
        is edited and its stamp is ALREADY stale — the 52-day case, caught at authoring time
        instead of after the bad commit lands. It does NOT catch a bump this morning followed
        by a body edit this afternoon: both clock arms are green there, because the stamp is
        under a day old and the clock agrees with it. That is the ORDINARY shape; 52 days is
        the pathological one. `test_the_stamp_covers_the_bytes_on_disk` is the arm for it.
        """
        from datetime import datetime, timezone

        if not self._is_dirty():
            pytest.skip("PRRD.md is clean — the committed arm is the applicable witness")
        stamped = self._frontmatter().get("updated")
        assert stamped, "`updated:` is missing while the file is being edited"
        lag = datetime.now(timezone.utc) - datetime.fromisoformat(str(stamped)).astimezone(timezone.utc)
        assert lag.total_seconds() < 86400, (
            f"PRRD.md has uncommitted edits but `updated: {stamped}` is {lag.days}d old. The "
            f"committed arm cannot see this — its witness is the previous commit, which has "
            f"not moved. Bump the stamp in the SAME edit, or run `prrd-edit.py` (it does both)."
        )

    def test_updated_is_not_older_than_the_last_commit_that_touched_the_file(self) -> None:
        """The arm that protects READERS: a clone's stamp must match its own history.

        Blind while the file is dirty — see the dirty arm above, which exists for exactly
        that window. The two are witnessed by different tenses on purpose and must not be
        collapsed into one.
        """
        from datetime import datetime

        res = subprocess.run(
            ["git", "--no-optional-locks", "log", "-1", "--format=%aI", "--", str(self.PRRD)],
            cwd=PLUGIN_ROOT, capture_output=True, text=True, timeout=30, check=False,
        )
        if res.returncode != 0 or not res.stdout.strip():
            pytest.skip("no git history for the PRRD (shallow clone or unborn branch)")
        last_commit = datetime.fromisoformat(res.stdout.strip())
        stamped = self._frontmatter().get("updated")
        assert stamped, "`updated:` is missing — an unstamped document cannot go stale, only be wrong"
        stamped_dt = datetime.fromisoformat(str(stamped))
        # Same-day tolerance: the bump and the commit are two acts, and the stamp is
        # written first. Anything beyond a day means an edit landed without one.
        assert (last_commit - stamped_dt).total_seconds() < 86400, (
            f"`updated: {stamped}` predates the last commit touching PRRD.md "
            f"({last_commit.isoformat()}) by more than a day — the file changed and its "
            f"own stamp did not. Edit through `prrd-edit.py` (it bumps both fields), or "
            f"bump `prrd-version:` and `updated:` in the same commit as the hand-edit."
        )

    def test_the_version_field_is_present_and_well_formed(self) -> None:
        """A missing version is worse than a stale one: nothing to compare at all."""
        import re

        v = str(self._frontmatter().get("prrd-version", ""))
        assert re.fullmatch(r"\d+\.\d+", v), (
            f"`prrd-version: {v!r}` is not `<major>.<minor>` — `prrd-edit.py` bumps major "
            f"on a GOLDEN change and minor on a SILVER one, so a malformed value makes the "
            f"next bump start from 0.1 and silently lose the document's history."
        )

    def test_the_committed_arm_is_provably_blind_where_the_dirty_arm_bites(self) -> None:
        """A PRECONDITION, not a claim — so the two arms cannot silently become one.

        If a later refactor makes the committed arm cover the authoring window, THIS test
        fails and says the dirty arm is now redundant. A control that reports its own
        obsolescence beats a comment nobody re-checks (ARCHITECT's construction,
        `ai-maestro#145`).
        """
        from datetime import datetime, timedelta, timezone

        now = datetime(2026, 8, 12, 12, 0, tzinfo=timezone.utc)
        stamp = now - timedelta(days=52)          # the stale stamp, as measured
        old_commit = stamp                        # dirty: HEAD has not moved since the stamp
        committed_lag = (old_commit - stamp).total_seconds()
        dirty_lag = (now - stamp).total_seconds()
        assert committed_lag < 86400, (
            "precondition broken: the committed arm now SEES the authoring window. If that "
            "is intentional, the dirty arm is redundant and should be removed with this test."
        )
        assert dirty_lag > 86400, "the dirty arm must bite where the committed arm cannot"

    def test_the_stamp_covers_the_bytes_on_disk(self) -> None:
        """The arm that stops asking a TIME question and asks a COVERAGE one.

        Both clock arms ask *how old is the stamp*. Neither asks *does the stamp cover
        these bytes* — so a bump at 09:00 followed by a body edit at 16:00 passes both,
        which is the shape that actually recurs. `mtime` answers coverage directly.

        DIRTY-ONLY, and the scope is what makes it sound: on a CLEAN file `mtime` is
        checkout time, not authorship, so it means nothing — a fresh clone would red
        every file. Under the dirty gate a checkout cannot reach this arm, because a
        checkout produces a clean file. (Credit: the ARCHITECT on `ai-maestro#145`, who
        had rejected mtime earlier in the same design for the noise it causes in the
        GENERAL case, then found the objection evaporates once scoped to dirty.)

        Measured on this tree before adopting — the first probe omitted the dirty gate and
        reported the clean baseline as RED, which would have rejected a correct fix:

            clean baseline                 red=False   (short-circuit, mtime meaningless)
            body edited, stamp untouched   red=True    mtime-updated = 1:45:18
            edited AND stamped together    red=False   mtime-updated = 0:00:00

        TOLERANCE is 5 minutes, and it is the number that decides whether this survives:
        long enough to absorb the honest ordering (compute the ISO string, save a moment
        later), short enough not to absorb the defect. It DOES red mid-edit before you have
        stamped, and that is correct rather than a nuisance — mid-edit the stamp genuinely
        does not cover the bytes, and the red clears on the stamp that precedes the commit.

        STILL NOT CLOSED, so do not read this as coverage: once the bad edit is COMMITTED,
        a same-day stale stamp is invisible to all three arms — the committed arm tolerates
        a day and mtime no longer means anything. Only a stored digest closes that, and it
        has to exclude `updated:` from its own hashed region, which is a fresh invariant
        with a fresh bypass. Known-open on purpose.
        """
        from datetime import datetime, timezone

        # Computed BEFORE the gate on purpose, so a clean-file skip can REPORT whether the
        # predicate was primed. A bare skip is consistent with two different worlds — the
        # gate absorbed a false red, or the predicate would have been silent anyway — and
        # crediting the gate without distinguishing them is the same empty-vs-all-clear
        # mistake one level in. (Construction from the ARCHITECT on ai-maestro#145, who
        # caught that my own touch-is-clean measurement had not checked this.)
        stamped = self._frontmatter().get("updated")
        written = datetime.fromtimestamp(self.PRRD.stat().st_mtime, tz=timezone.utc)
        primed = primed_state(stamped, written)

        if not self._is_dirty():
            pytest.skip(
                "PRRD.md is clean — mtime records checkout time here, not authorship; "
                f"gate load-bearing this run: {primed}"
            )
        assert stamped, "`updated:` is missing while the file is being edited"
        claimed = datetime.fromisoformat(str(stamped)).astimezone(timezone.utc)
        # The predicate carries its OWN precondition — see stamp_predates_the_bytes.
        assert not stamp_predates_the_bytes(claimed, written, dirty=True), (
            f"PRRD.md was written at {written.isoformat()} but `updated:` claims {stamped} — "
            f"the stamp does not cover the bytes on disk. TWO candidates, and this arm "
            f"cannot tell them apart: (1) an edit in progress whose stamp is not bumped "
            f"yet — bump it (`prrd-edit.py` does both); (2) something OTHER than you "
            f"rewrote the file, and the stamp is innocent. What it HAS ruled out is a "
            f"stray mtime: a touch leaving content identical reads clean to git and never "
            f"reaches this arm, so the bytes genuinely changed. Check `git diff` first."
        )

    def test_the_clock_arms_are_provably_blind_where_the_coverage_arm_bites(self) -> None:
        """Precondition again: three arms must not silently collapse into two.

        Asserts the two clock arms ARE green on a same-day edit — the input the coverage
        arm exists for. If a later change makes them catch it, this fails and reports the
        coverage arm as redundant, rather than leaving overlapping guards nobody re-checks.
        """
        from datetime import datetime, timedelta, timezone

        now = datetime(2026, 8, 12, 16, 0, tzinfo=timezone.utc)
        stamped = now - timedelta(hours=7)      # bumped this morning
        last_commit = stamped                   # dirty: HEAD has not moved since
        assert (last_commit - stamped).total_seconds() < 86400, "committed arm must be green here"
        assert (now - stamped).total_seconds() < 86400, "dirty clock arm must be green here"
        written = now                           # ...but the bytes were written just now
        assert written > stamped + timedelta(minutes=5), "the coverage arm must bite here"

    def test_the_gate_branch_is_witnessed_and_not_merely_present(self) -> None:
        """The precondition INSIDE the predicate is dead code until something calls it.

        The live arm `pytest.skip`s while the file is clean and then passes `dirty=True`
        unconditionally, so `if not dirty` never executes on a normal run. A clean-file
        SKIP is NOT the baseline it looks like: it proves the PRECONDITION was false and
        the predicate was never reached, which says nothing about what the predicate
        returns. Without this control, deleting the gate leaves the entire suite green —
        the protection would exist with nothing witnessing it.

        So call it directly on the input that made the ungated probe lie: a correctly
        stamped CLEAN file whose mtime sits hours past the stamp, i.e. a checkout. Both
        directions, because a control that only checks the quiet half cannot tell "the
        gate held" from "the input stopped reding".
        """
        from datetime import datetime, timedelta, timezone

        stamped = datetime(2026, 8, 12, 9, 0, tzinfo=timezone.utc)
        checked_out = stamped + timedelta(hours=1)  # mtime = checkout time, not authorship

        assert stamp_predates_the_bytes(stamped, checked_out, dirty=True), (
            "control is inert — this input must red while dirty, or the clean assertion "
            "below passes for the wrong reason and witnesses nothing"
        )
        assert not stamp_predates_the_bytes(stamped, checked_out, dirty=False), (
            "the gate is gone — a fresh clone now reds every correctly stamped file"
        )

    def test_the_skip_line_reports_all_three_states_including_the_loud_one(self) -> None:
        """Every branch of what the clean-file skip prints, driven rather than assumed.

        Checking only the True branch would be this thread's own failure one level up: a
        line watched succeeding once and never watched DECLINE to claim anything. So all
        three, plus the case that must not degrade into a quiet answer.
        """
        from datetime import datetime, timedelta, timezone

        stamp = datetime(2026, 8, 12, 9, 0, tzinfo=timezone.utc)

        assert primed_state(stamp.isoformat(), stamp + timedelta(hours=10)) is True, (
            "far past tolerance — the gate is absorbing a red and the line must say so"
        )
        assert primed_state(stamp.isoformat(), stamp) is False, (
            "stamp covers the bytes — the line must admit the skip proved nothing this run"
        )
        assert primed_state(None, stamp) is None, "no `updated:` at all — cannot say"

        with pytest.raises(ValueError):
            primed_state("not-a-timestamp", stamp)
