# Contributing to pytest-bdd-property

Thank you for your interest in contributing to pytest-bdd-property.

## Development Setup

### Prerequisites

- Python 3.11+
- pip or uv
- Node.js + pnpm (only for conformance testing with specdrive)

### Install

```bash
git clone https://github.com/bryonjacob/pytest-bdd-property.git
cd pytest-bdd-property
uv sync --group dev
```

### Conformance Testing (Optional)

The shared behavioral spec (`bdd-pbt-spec`) is managed by specdrive. If you need to run conformance tests or update the shared spec:

```bash
pnpm install        # Installs specdrive CLI
npx specdrive install   # Vendors shared specs into specs/_specdrive/
```

This is only needed if you are working on conformance test changes. The plugin unit tests (`tests/plugin/`) run without specdrive.

## Running Tests

```bash
# Run all tests (79 tests)
python -m pytest

# Plugin unit tests only (39 tests, no specdrive needed)
python -m pytest tests/plugin/ -v

# With coverage
python -m pytest --cov=pytest_bdd_property --cov-report=term-missing

# With JUnit XML output
python -m pytest --junitxml=test-results.xml
```

## Code Style

- **Formatter/Linter:** [ruff](https://docs.astral.sh/ruff/) (`ruff check .` and `ruff format .`)
- **Type checker:** [mypy](https://mypy.readthedocs.io/) (`mypy pytest_bdd_property/`)
- **Max complexity:** 10 (enforced by ruff mccabe)
- **Line length:** 100 characters
- **Coverage threshold:** 96%

Run all checks:

```bash
just check-all         # format, lint, typecheck, specdrive (full gate)
just test              # tests only
just coverage          # with 96% threshold
just complexity        # per-function complexity report
```

## Architecture Overview

The plugin uses a **two-phase execution model**:

1. **Phase 1 (Registration):** During normal pytest-bdd step execution, property steps register Hypothesis strategies, assumptions, and When/Then callbacks into a `PropertyContext` -- nothing executes yet.

2. **Phase 2 (Execution):** After all steps run, a `pytest_runtest_call` hook (trylast) builds a composite Hypothesis strategy from registered strategies, generates random inputs, applies assumption filters, and executes the When/Then callbacks hundreds of times. On failure, Hypothesis shrinks to a minimal counterexample.

Key modules:
- `registry.py` -- Strategy name resolution (16 built-in strategies)
- `assumptions.py` -- Assumption pattern matching (18 built-in patterns)
- `helpers.py` -- `property_when()` / `property_then()` decorators
- `runner.py` -- Composite strategy construction and Hypothesis execution
- `plugin.py` -- pytest hooks and step dispatch

## Submitting Changes

1. Fork the repository and create a feature branch from `main`
2. Make your changes
3. Ensure all tests pass: `python -m pytest`
4. Ensure code style checks pass: `ruff check .` and `mypy pytest_bdd_property/`
5. Write or update tests for your changes
6. Submit a pull request against `main`

Please keep PRs focused on a single concern. If you are fixing a bug and adding a feature, submit them as separate PRs.
