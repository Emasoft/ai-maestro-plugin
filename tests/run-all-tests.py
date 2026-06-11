#!/usr/bin/env python3
"""run-all-tests.py — run the plugin's full Python test suite as a gate.

This is the entry point a publish gate (e.g. CPV's publish.py `_gate_tests`)
invokes: it runs every test under tests/ via pytest and propagates pytest's
exit status, so:

    exit 0   → all tests passed (gate is green)
    exit !=0 → at least one test failed / errored (gate blocks the publish)

It deliberately shells out to `pytest` rather than importing it, so the exit
code is exactly pytest's own (0 pass, 1 failures, 2 usage error, 5 no tests
collected, …) and the gate sees the same result a human running pytest sees.

Usage:
    python3 tests/run-all-tests.py            # run the whole suite
    python3 tests/run-all-tests.py -k pillars # forward extra args to pytest
    uv run tests/run-all-tests.py             # under uv (recommended locally)

Any extra CLI args are forwarded verbatim to pytest.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
PLUGIN_ROOT = TESTS_DIR.parent


def _pytest_argv() -> list[str]:
    """Prefer the importable pytest module (works under `uv run` and any venv);
    fall back to a `pytest` console script on PATH."""
    try:
        import pytest  # noqa: F401  (import is the capability probe)

        return [sys.executable, "-m", "pytest"]
    except ImportError:
        exe = shutil.which("pytest")
        if exe:
            return [exe]
    print(
        "error: pytest is not installed. Install dev deps first, e.g.\n"
        "  uv sync --extra dev      (or)  pip install pytest",
        file=sys.stderr,
    )
    sys.exit(2)


def main(argv: list[str] | None = None) -> int:
    extra = sys.argv[1:] if argv is None else argv
    cmd = [*_pytest_argv(), str(TESTS_DIR), *extra]
    # Run from the plugin root so relative paths inside tests resolve the same
    # way they do for a developer running pytest from the repo root.
    proc = subprocess.run(cmd, cwd=str(PLUGIN_ROOT), check=False)
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
