# pytest-bdd-property

Property-based testing for Gherkin scenarios, powered by [Hypothesis](https://hypothesis.readthedocs.io/).

Express universal invariants in standard Gherkin, and have Hypothesis generate 100+ inputs to find counterexamples automatically.

## Quick Start

### 1. Tag your scenario with `@property-based`

```gherkin
@property-based
Feature: Password Hashing Properties

  Scenario: A password always verifies against its own hash
    Given any valid password <P>
    When <P> is hashed producing <H>
    Then <P> verifies against <H>
```

### 2. Register your conftest step definitions

In your root `conftest.py`:

```python
import pytest_bdd_property.plugin  # registers pytest hooks

from pytest_bdd import given, when, then, parsers
from pytest_bdd_property.plugin import (
    handle_given_step,
    handle_when_step,
    handle_then_step,
)

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

### 3. Write property step definitions

```python
from pytest_bdd import scenarios
from pytest_bdd_property import register_strategy, property_when, property_then
from hypothesis import strategies as st

scenarios("my_feature.feature")

register_strategy("valid password", lambda: st.text(min_size=8, max_size=128))

@property_when(r"<(\w+)> is hashed producing <(\w+)>")
def hash_step(vals, results, pw_var, hash_var):
    results[hash_var] = hash_password(vals[pw_var])

@property_then(r"<(\w+)> verifies against <(\w+)>")
def verify_step(vals, results, pw_var, hash_var):
    assert verify_password(vals[pw_var], results[hash_var])
```

### 4. Run tests

```bash
pytest tests/ -v
```

Hypothesis runs each `@property-based` scenario 100 times with generated inputs. On failure, it **shrinks** to find the minimal counterexample.

---

## How It Works

### Two-Phase Execution Model

**Phase 1 (Registration):** During normal pytest-bdd step execution:
- `Given any <type> <var>` → registers a Hypothesis strategy
- `And <A> is not equal to <B>` → registers an assumption (filter)
- `When`/`Then` steps → register callbacks (don't execute yet)

**Phase 2 (Execution):** After all steps run, a pytest hook triggers:
- Hypothesis builds a composite strategy from all registered strategies
- Runs the property 100+ times with generated inputs
- Applies assumptions via `hypothesis.assume()`
- Executes When callbacks (actions), then Then callbacks (assertions)
- On failure: shrinks to find the minimal counterexample

### Architecture

```
conftest.py                    test_my_feature.py
  ├── plugin hooks               ├── scenarios("my.feature")
  └── catch-all steps            ├── register_strategy(...)
       │                         ├── @property_when(...)
       ▼                         └── @property_then(...)
  plugin.py
  ├── pytest_runtest_setup → detect @property-based tag
  ├── handle_given_step → strategy + assumption registration
  ├── handle_when_step → action callback registration
  ├── handle_then_step → assertion callback registration
  └── pytest_runtest_call → run_property_test() via Hypothesis
```

---

## Built-in Strategies

Use these directly in your feature files with `Given any <type> <var>`:

### Primitives

| Strategy Name | Description | Hypothesis Equivalent |
|---------------|-------------|-----------------------|
| `text` | Arbitrary Unicode strings | `st.text()` |
| `non-empty text` | Strings with length ≥ 1 | `st.text(min_size=1)` |
| `integer` | Arbitrary integers | `st.integers()` |
| `positive integer` | Integers ≥ 1 | `st.integers(min_value=1)` |
| `negative integer` | Integers ≤ -1 | `st.integers(max_value=-1)` |
| `natural` | Integers ≥ 0 | `st.integers(min_value=0)` |
| `float` | Floats (no NaN/Infinity) | `st.floats(allow_nan=False, allow_infinity=False)` |
| `boolean` | True or False | `st.booleans()` |

### Strings

| Strategy Name | Description | Hypothesis Equivalent |
|---------------|-------------|-----------------------|
| `ascii text` | ASCII-only strings | `st.text(alphabet=st.characters(codec="ascii"))` |
| `alphanumeric` | `[a-z0-9]+` strings | `st.from_regex(r"[a-z0-9]+")` |
| `hex string` | `[0-9a-f]+` strings | `st.from_regex(r"[0-9a-f]+")` |

### Identifiers

| Strategy Name | Description | Hypothesis Equivalent |
|---------------|-------------|-----------------------|
| `uuid` | UUID v4 strings | `st.uuids().map(str)` |
| `email` | Email-shaped strings | `st.emails()` |
| `url` | URL-shaped strings | `st.from_regex(...)` |

### Temporal

| Strategy Name | Description | Hypothesis Equivalent |
|---------------|-------------|-----------------------|
| `date` | Date objects | `st.dates()` |

### Structured

| Strategy Name | Description | Hypothesis Equivalent |
|---------------|-------------|-----------------------|
| `json value` | Recursive JSON values | `st.recursive(...)` |
| `json object` | `dict[str, str]` | `st.dictionaries(st.text(), st.text())` |

### Domain Defaults

| Strategy Name | Description | Hypothesis Equivalent |
|---------------|-------------|-----------------------|
| `password` | Text, 8-128 chars | `st.text(min_size=8, max_size=128)` |
| `username` | `[a-z0-9_]{3,32}` | `st.from_regex(...)` |

### Custom Strategies

Register domain-specific strategies in your test file:

```python
from pytest_bdd_property import register_strategy
from hypothesis import strategies as st

register_strategy("valid password", lambda: (
    st.tuples(
        st.text(alphabet="abcdefghijklmnopqrstuvwxyz", min_size=2, max_size=10),
        st.text(alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ", min_size=2, max_size=10),
        st.text(alphabet="0123456789", min_size=2, max_size=5),
        st.text(alphabet="!@#$%^&*", min_size=2, max_size=3),
    ).map(lambda parts: parts[0] + parts[1] + parts[2] + parts[3])
))
```

Then in Gherkin:
```gherkin
Given any valid password <P>
```

---

## Built-in Assumptions

Use these in `Given`/`And` steps to filter generated inputs:

### Equality

| Pattern | Meaning | Maps To |
|---------|---------|---------|
| `<A> is not equal to <B>` | A ≠ B | `assume(A != B)` |
| `<A> is equal to <B>` | A = B | `assume(A == B)` |

### Numeric Comparison

| Pattern | Meaning | Maps To |
|---------|---------|---------|
| `<A> is greater than <B>` | A > B | `assume(A > B)` |
| `<A> is less than <B>` | A < B | `assume(A < B)` |
| `<A> is greater than or equal to <B>` | A ≥ B | `assume(A >= B)` |
| `<A> is less than or equal to <B>` | A ≤ B | `assume(A <= B)` |

### Emptiness

| Pattern | Meaning | Maps To |
|---------|---------|---------|
| `<A> is not empty` | len(A) > 0 | `assume(len(A) > 0)` |
| `<A> is empty` | len(A) = 0 | `assume(len(A) == 0)` |

### Length

| Pattern | Meaning | Maps To |
|---------|---------|---------|
| `<A> has length greater than N` | len(A) > N | `assume(len(A) > N)` |
| `<A> has length less than N` | len(A) < N | `assume(len(A) < N)` |

### Containment

| Pattern | Meaning | Maps To |
|---------|---------|---------|
| `<A> contains <B>` | B in A | `assume(B in A)` |
| `<A> does not contain <B>` | B not in A | `assume(B not in A)` |

### Type Checks

| Pattern | Meaning | Maps To |
|---------|---------|---------|
| `<A> is a number` | isinstance(A, (int, float)) | `assume(isinstance(A, (int, float)))` |
| `<A> is a string` | isinstance(A, str) | `assume(isinstance(A, str))` |

### Custom Assumptions

```python
from pytest_bdd_property import register_assumption

register_assumption(
    r"^<(\w+)> is a valid email$",
    lambda var: lambda vals: "@" in str(vals[var])
)
```

---

## Configuration via Tags

```gherkin
@property-based @num-runs:500 @seed:42 @verbose
Scenario: Stress test hashing
  ...
```

| Tag | Effect |
|-----|--------|
| `@num-runs:<n>` | Override number of generated examples (default: 100) |
| `@seed:<n>` | Fix the random seed for reproducibility |
| `@verbose` | Enable verbose output |

---

## Common Patterns

### Round-trip (Serialization)

```gherkin
@property-based
Scenario: JSON round-trip preserves data
  Given any json object <D>
  When <D> is serialized to JSON producing <J>
  And <J> is deserialized producing <D2>
  Then <D> is equal to <D2>
```

### Idempotency

```gherkin
@property-based
Scenario: Normalizing email twice gives the same result
  Given any email <E>
  When <E> is normalized producing <N1>
  And <N1> is normalized producing <N2>
  Then <N1> is equal to <N2>
```

### No False Positives

```gherkin
@property-based
Scenario: Wrong password never verifies
  Given any valid password <P>
  And any valid password <Q>
  And <P> is not equal to <Q>
  When <P> is hashed producing <H>
  Then <Q> does not verify against <H>
```

### No Information Leakage

```gherkin
@property-based
Scenario: Hash never contains plaintext
  Given any valid password <P>
  When <P> is hashed producing <H>
  Then <H> does not contain <P>
```

---

## API Reference

### `register_strategy(name, factory)`

Register a named strategy for `Given any <name> <var>`.

- `name`: Case-insensitive strategy name
- `factory`: `() -> SearchStrategy` callable

### `property_when(pattern)`

Decorator to register a When step for property-based scenarios.

```python
@property_when(r"<(\w+)> is hashed producing <(\w+)>")
def hash_step(vals, results, pw_var, hash_var):
    results[hash_var] = hash_password(vals[pw_var])
```

- `vals`: `dict[str, Any]` — generated values keyed by variable name
- `results`: `dict[str, Any]` — intermediate results from When steps
- Additional args: regex capture groups from the pattern

### `property_then(pattern)`

Decorator to register a Then step for property-based scenarios.

```python
@property_then(r"<(\w+)> verifies against <(\w+)>")
def verify_step(vals, results, pw_var, hash_var):
    assert verify_password(vals[pw_var], results[hash_var])
```

Raise `AssertionError` to signal a property violation. Hypothesis shrinks to minimal counterexample.

### `register_assumption(pattern, builder)`

Register a custom assumption pattern.

```python
register_assumption(
    r"^<(\w+)> is a valid email$",
    lambda var: lambda vals: "@" in str(vals[var])
)
```

### `resolve_strategy(name)`

Resolve a strategy name to a Hypothesis `SearchStrategy`. Raises `ValueError` if not found.

### `list_strategies()`

Return all registered strategy names, sorted.

---

## Coexistence with Behavioral Scenarios

Property-based and behavioral scenarios coexist naturally:

```gherkin
Feature: User Authentication

  # Behavioral (concrete examples)
  Scenario: User can log in with correct password
    Given a user with password "hunter2"
    When they log in with "hunter2"
    Then they are authenticated

  # Property (universal invariant)
  @property-based
  Scenario: Wrong password never authenticates
    Given any text <P>
    And any text <Q>
    And <P> is not equal to <Q>
    Given a user with password <P>
    When they log in with <Q>
    Then they are rejected
```

The `@property-based` tag tells the plugin to intercept execution. Scenarios without the tag run normally through pytest-bdd.
