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
