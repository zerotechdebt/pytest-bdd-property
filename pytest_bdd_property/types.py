"""Type definitions for pytest-bdd-property."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol

from hypothesis import strategies as st

# A factory that produces a Hypothesis SearchStrategy.
StrategyFactory = Callable[[], st.SearchStrategy[Any]]

# A callback registered by property_when() or property_then().
# vals: generated values keyed by variable name
# results: intermediate results from When steps
StepCallback = Callable[[dict[str, Any], dict[str, Any]], None]

# A predicate that filters generated inputs.
# Returns True to keep the input, False to discard and regenerate.
AssumptionFn = Callable[[dict[str, Any]], bool]


class AssumptionPattern(Protocol):
    """A registered pattern for parsing assumption steps."""

    pattern: str
    build: Callable[..., AssumptionFn]
