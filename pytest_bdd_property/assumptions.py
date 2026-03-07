"""Assumption pattern matching for @property-based scenarios."""

from __future__ import annotations

import re
from collections.abc import Callable

from .types import AssumptionFn

_patterns: list[tuple[re.Pattern[str], Callable[..., AssumptionFn]]] = []


def register_assumption(pattern: str, builder: Callable[..., AssumptionFn]) -> None:
    """Register a custom assumption pattern.

    When a @property-based scenario contains a Given/And step matching
    the pattern, the builder is called with regex groups to produce an
    AssumptionFn. That function is called on every generated input;
    returning False discards the input (maps to hypothesis.assume()).

    Example::

        register_assumption(
            r"^<(\\w+)> has length greater than (\\d+)$",
            lambda var, n: lambda vals: len(str(vals[var])) > int(n)
        )

    Then in Gherkin::

        And <P> has length greater than 5
    """
    _patterns.append((re.compile(pattern), builder))


def parse_assumption(step_text: str) -> AssumptionFn | None:
    """Try to parse step text as an assumption.

    Returns an AssumptionFn if a registered pattern matches, None otherwise.
    """
    for pattern, builder in _patterns:
        match = pattern.match(step_text)
        if match:
            return builder(*match.groups())
    return None


# ── Built-in Assumption Patterns ────────────────────────────────────────────

# Equality
register_assumption(
    r"^<(\w+)> is not equal to <(\w+)>$",
    lambda a, b: lambda vals: vals[a] != vals[b],
)
register_assumption(
    r"^<(\w+)> is equal to <(\w+)>$",
    lambda a, b: lambda vals: vals[a] == vals[b],
)

# Numeric comparison (variable vs variable)
register_assumption(
    r"^<(\w+)> is greater than <(\w+)>$",
    lambda a, b: lambda vals: vals[a] > vals[b],
)
register_assumption(
    r"^<(\w+)> is less than <(\w+)>$",
    lambda a, b: lambda vals: vals[a] < vals[b],
)
register_assumption(
    r"^<(\w+)> is greater than or equal to <(\w+)>$",
    lambda a, b: lambda vals: vals[a] >= vals[b],
)
register_assumption(
    r"^<(\w+)> is less than or equal to <(\w+)>$",
    lambda a, b: lambda vals: vals[a] <= vals[b],
)

# Numeric comparison (variable vs literal)
register_assumption(
    r"^<(\w+)> is greater than (-?\d+(?:\.\d+)?)$",
    lambda a, n: lambda vals: vals[a] > float(n),
)
register_assumption(
    r"^<(\w+)> is less than (-?\d+(?:\.\d+)?)$",
    lambda a, n: lambda vals: vals[a] < float(n),
)
register_assumption(
    r"^<(\w+)> is greater than or equal to (-?\d+(?:\.\d+)?)$",
    lambda a, n: lambda vals: vals[a] >= float(n),
)
register_assumption(
    r"^<(\w+)> is less than or equal to (-?\d+(?:\.\d+)?)$",
    lambda a, n: lambda vals: vals[a] <= float(n),
)

# Emptiness
register_assumption(
    r"^<(\w+)> is not empty$",
    lambda a: lambda vals: len(vals[a]) > 0 if hasattr(vals[a], "__len__") else vals[a] is not None,
)
register_assumption(
    r"^<(\w+)> is empty$",
    lambda a: lambda vals: len(vals[a]) == 0 if hasattr(vals[a], "__len__") else vals[a] is None,
)

# Length
register_assumption(
    r"^<(\w+)> has length greater than (\d+)$",
    lambda a, n: lambda vals: len(str(vals[a])) > int(n),
)
register_assumption(
    r"^<(\w+)> has length less than (\d+)$",
    lambda a, n: lambda vals: len(str(vals[a])) < int(n),
)

# Containment
register_assumption(
    r"^<(\w+)> contains <(\w+)>$",
    lambda a, b: lambda vals: str(vals[b]) in str(vals[a]),
)
register_assumption(
    r"^<(\w+)> does not contain <(\w+)>$",
    lambda a, b: lambda vals: str(vals[b]) not in str(vals[a]),
)

# Type checks
register_assumption(
    r"^<(\w+)> is a number$",
    lambda a: lambda vals: isinstance(vals[a], (int, float)),
)
register_assumption(
    r"^<(\w+)> is a string$",
    lambda a: lambda vals: isinstance(vals[a], str),
)
