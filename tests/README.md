# Tests

Python test suite for the `ai-maestro-plugin`. All tests are **real** — they
invoke the actual scripts as subprocesses against throwaway temp projects. No
mocks, no stubs (per this project's no-mock rule).

## Running the whole suite (the publish gate)

`tests/run-all-tests.py` is the entry point a publish gate invokes. It runs
every test under `tests/` via pytest and exits **0 on all-pass**, **non-zero on
any failure** (it propagates pytest's own exit code).

```bash
# Recommended (resolves dev deps via the project's pyproject [dev] extra):
uv run tests/run-all-tests.py

# Or with a plain interpreter that already has pytest installed:
python3 tests/run-all-tests.py
```

Extra arguments are forwarded verbatim to pytest:

```bash
uv run tests/run-all-tests.py -k pillars        # only the pillar tests
uv run tests/run-all-tests.py -v                # verbose
uv run tests/run-all-tests.py -x                # stop at first failure
```

## Running a single file directly with pytest

```bash
uv run pytest tests/test_prrd_trdd_pillars.py -q
uv run pytest tests/test_memory_protocol_components.py -q
uv run pytest tests/test_cpv_network_resilience.py -q
```

## What each test file covers

| File | Scope |
|------|-------|
| `test_prrd_trdd_pillars.py` | PRRD/TRDD/Kanban pillar scripts in `scripts/prrd-trdd/` — `get-prrd.py`, `prrd-edit.py`, `findprrd.py`, `findtrdd.py`, `kanban.py`, `amama_proposal_approvals.py`, `bootstrap_design.py`, `resolve_pillar_scripts.sh`. Real subprocess invocation against fresh git-backed temp projects. |
| `test_memory_protocol_components.py` | Memory-protocol components (issue #4): `install-memgrep.sh` deterministic paths + structural checks on the canonical skills/rule/crate. |
| `test_cpv_network_resilience.py` | The transient-error classifiers in `scripts/cpv_network_resilience.py`. |

## Conventions

- **No mocks.** A test that needs a service asks for the real thing or exercises
  a deterministic, side-effect-free path. Mocked tests are forbidden here.
- **Fresh temp project per test.** The pillar tests build a throwaway dir with
  `tmp_path`, `git init` it, run the real `bootstrap_design.py`, write real
  `PRRD.md` / `TRDD-*.md` fixtures, then run the script under test and assert on
  real stdout / exit code / on-disk state.
- **Scrubbed env for auth tests.** Auth tests pop `AID_AUTH` / `AMAMA_PRRD_TRUST`
  from the subprocess env so a real MANAGER token in the developer's shell can
  never silently turn an "expected refusal (exit 4)" into a pass.
- **One-line docstring per test** describing exactly what it checks.

## Requirements

- Python ≥ 3.12, `pytest` (in the `[project.optional-dependencies] dev` group;
  `uv sync --extra dev` installs it).
- `git` on PATH (the pillar tests create real git repos so `git mv` works).
- A POSIX `sh` (for the `resolve_pillar_scripts.sh` tests).
