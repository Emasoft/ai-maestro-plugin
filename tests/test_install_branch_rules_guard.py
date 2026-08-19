#!/usr/bin/env python3
"""`--install-branch-rules` must REFUSE on a repo carrying the ratified baseline.

`publish.install_branch_rules` shells out to `uvx cpv-setup-branch-rules` so
downstream plugins do not have to vendor that script — which means the hazard
below shipped from HERE, to every plugin that copied this pipeline.

Read first-hand in CPV v5.3.0 `scripts/setup_branch_rules.py`:

  * `:110  RULESET_NAME = "cpv-branch-rules"` is hardcoded, and the file
    contains ZERO occurrences of "baseline-". It cannot see the ratified
    rulesets, so on a conforming repo it can only ADD a third one beside them
    — `manager-approval-defaults` §F "adding a new ruleset affecting the
    default branch", i.e. NON-exempt.
  * `:326  fetch_legacy_protection_rulesets()` calls any non-cpv ruleset
    "legacy" when its rules intersect {pull_request, required_status_checks,
    required_signatures, code_quality}. `baseline-pr-and-checks` carries the
    first two, so it ALWAYS matches, and `:694` prints
    `gh api --method DELETE .../rulesets/<id>` for it.

So an author following the flag's own output ends up with the ratified pair
half-deleted and a non-ratified ruleset in its place. Upstream report:
claude-plugins-validation#203 (found by the INTEGRATOR plugin).

These are REAL calls against the real origin — no mocks. The guard's whole
value is that it reads the LIVE ruleset list, so a test that substituted that
read would be testing a different function than the one that ships.
"""
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import publish  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SLUG = "Emasoft/ai-maestro-plugin"


def _gh_is_usable() -> bool:
    if shutil.which("gh") is None:
        return False
    r = subprocess.run(["gh", "auth", "status"], capture_output=True, check=False)
    return r.returncode == 0


needs_gh = pytest.mark.skipif(
    not _gh_is_usable(),
    reason="needs an authenticated gh; the guard reads the LIVE ruleset list and "
    "mocking that read would test a different function than the one that ships",
)


def test_the_ratified_names_are_the_ones_the_guard_looks_for() -> None:
    """The constant is not a free-form label — CPV matches rulesets by NAME (ratified TRIO per janitor#14)."""
    assert publish.RATIFIED_BASELINE_RULESETS == (
        "baseline-history-protect",
        "baseline-pr-and-checks",
        "baseline-tag-protect",
    )


@needs_gh
def test_this_repo_really_carries_the_ratified_baseline() -> None:
    """Establish the premise before asserting the behaviour that depends on it.

    Without this, a guard that refused for the WRONG reason (an unreadable
    list, a typo'd slug) would look identical to one working correctly.
    """
    names = publish._fetch_ruleset_names(SLUG)
    assert names is not None, "could not read rulesets — the next test would be vacuous"
    assert "baseline-history-protect" in names
    assert "baseline-pr-and-checks" in names
    assert "baseline-tag-protect" in names


@needs_gh
def test_install_branch_rules_refuses_on_a_baselined_repo() -> None:
    """The refusal itself: non-zero, and cpv-setup-branch-rules never runs.

    Falsify by deleting the `if present:` block in install_branch_rules — this
    goes green-to-red, and on a repo carrying the ratified pair the real
    command would then advise deleting baseline-pr-and-checks.
    """
    assert publish.install_branch_rules(ROOT) != 0


@needs_gh
def test_an_unreadable_ruleset_list_fails_closed() -> None:
    """A slug that cannot be read must return None, never an empty list.

    This is the direction that matters: `[]` would mean "no ratified baseline
    present", the guard would step aside, and the destructive command would
    run against a repo nobody could inspect. A nonexistent repo is the
    cheapest real way to produce that failure — no mock required.
    """
    assert publish._fetch_ruleset_names("Emasoft/this-repo-does-not-exist-xyzzy") is None
