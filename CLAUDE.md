# pytest-bdd-property

Property-based testing plugin for pytest-bdd. Express universal invariants as Gherkin scenarios, executed by Hypothesis.

## What This Is

A pytest plugin that lets you write property-based tests in standard Gherkin. Tag a scenario `@property-based` and the plugin generates hundreds of random inputs, searching for counterexamples via Hypothesis's shrinking.

## Independence Model

This plugin is **standalone**. Users get BDD + property-based testing integration without needing any other tools. Specdrive is an optional dev dependency used only for conformance testing against `bdd-pbt-spec`.

**RID traceability** (getting `@RID-*` markers into JUnit XML) is NOT this plugin's job. That responsibility belongs to specdrive via `specdrive init`, which generates a conftest.py hook. This plugin was decoupled from RID bridging to maintain clean separation of concerns.

## Architecture

Two-phase execution model:

1. **Phase 1 (Registration)**: pytest-bdd runs steps normally, but property steps register strategies, assumptions, and callbacks rather than executing immediately.
2. **Phase 2 (Execution)**: A `pytest_runtest_call` hook (trylast) builds a composite Hypothesis strategy, runs `@given(vals=composite)` with all registered callbacks, and lets Hypothesis shrink any failure to a minimal counterexample.

## Source Layout

```
pytest_bdd_property/
├── __init__.py       # Public API exports
├── types.py          # Core types: StrategyFactory, StepCallback, AssumptionFn
├── registry.py       # Strategy registry (16 built-in strategies: text, integer, email, etc.)
├── assumptions.py    # Assumption patterns (18 built-in: equality, numeric, emptiness, etc.)
├── context.py        # PropertyContext dataclass: strategies, assumptions, actions, assertions, settings
├── helpers.py        # property_when() / property_then() — register Phase 2 callbacks
├── runner.py         # run_property_test(): builds composite strategy, runs Hypothesis
└── plugin.py         # pytest hooks + step handlers (handle_given_step, handle_when_step, handle_then_step)
```

## Specs

```
specs/
├── plugin/                          # Local specs (plugin internals, 7 files, 27 RIDs)
│   ├── registry.feature             # Strategy registry (REG-001–005)
│   ├── context.feature              # PropertyContext lifecycle (CTX-001–004)
│   ├── step-helpers.feature         # property_when/then helpers (HELP-001–004)
│   ├── step-handlers.feature        # Step dispatch routing (DISPATCH-001–005)
│   ├── settings.feature             # Tag parsing (SET-001–004)
│   ├── error-handling.feature       # Error conditions (ERR-001–004)
│   ├── assumptions.feature          # Assumption pattern registry (ASM-001–004)
│   └── runner.feature               # Phase 2 execution (RUN-001–007)
└── _specdrive/bdd-pbt-spec/         # Installed shared spec (40 RIDs, vendored by specdrive)
```

Local specs describe implementation structure, not user-observable behavior — they are internal to this plugin.

## Tests

79 tests total (39 plugin unit tests + 40 conformance tests).

```bash
pip install -e .                          # Install in editable mode
python -m pytest                          # Run all tests
python -m pytest tests/plugin/            # Plugin unit tests only
python -m pytest --junitxml=test-results.xml  # With JUnit XML output
```

`just check-all` runs everything locally (auto-fixes formatting). `just ci` is the read-only version GitHub CI runs. On a fresh clone, fetch the shared specs first: `pnpm install && pnpm exec specdrive install` (`specs/_specdrive/` is not committed).

Releasing: see RELEASING.md (`just release` tags; GitHub Actions publishes to PyPI).

Note: `specdrive verify` requires RID->JUnit bridging. Run `specdrive init` in the project to set that up.

## Public API

```python
# Strategy registration
register_strategy(name: str, factory: Callable[[], SearchStrategy])
resolve_strategy(name: str) -> SearchStrategy
list_strategies() -> list[str]

# Assumption patterns
register_assumption(pattern: re.Pattern, builder: Callable[..., AssumptionFn])
parse_assumption(step_text: str) -> AssumptionFn | None

# Step helpers (register Phase 2 callbacks)
property_when(pattern: str)   # decorator
property_then(pattern: str)   # decorator

# Context + execution
PropertyContext              # dataclass
run_property_test(ctx: PropertyContext)
```

## Integration Pattern

Projects using this plugin need a `conftest.py` with catch-all step definitions:

```python
import pytest_bdd_property.plugin  # registers pytest hooks
from pytest_bdd_property.plugin import handle_given_step, handle_when_step, handle_then_step
from pytest_bdd import given, when, then, parsers

@given(parsers.re(r"(?P<text>any .+|<.+)"))
def property_given_step(text):
    handle_given_step(text)

@when(parsers.re(r"(?P<text><.+)"))
def property_when_step(text):
    handle_when_step(text)

@then(parsers.re(r"(?P<text><.+)"))
def property_then_step(text):
    handle_then_step(text)
```

## Configuration Tags

- `@property-based` — activates the plugin for a scenario
- `@num-runs:N` — number of generated examples (default: 100)
- `@seed:N` — fixed seed for reproducibility (enables `derandomize=True`)
- `@verbose` — log all generated examples

## Dependencies

- `pytest >= 8.0`
- `pytest-bdd >= 7.0`
- `hypothesis >= 6.0`
- Python >= 3.11

## Roadmap

- Expand built-in strategy and assumption libraries
- Add support for composite/nested strategies in Gherkin
- Improve error messages and counterexample reporting
