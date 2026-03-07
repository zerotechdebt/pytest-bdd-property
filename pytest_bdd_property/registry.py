"""Strategy registry: maps natural-language names to Hypothesis strategies."""

from __future__ import annotations

from hypothesis import strategies as st

from .types import StrategyFactory

_registry: dict[str, StrategyFactory] = {}


def register_strategy(name: str, factory: StrategyFactory) -> None:
    """Register a named strategy for use in 'Given any <type> <var>' steps.

    Strategy names are case-insensitive. Registering a name that already
    exists overwrites the previous factory.

    Example::

        register_strategy("valid password", lambda: (
            st.text(min_size=8, max_size=128)
            .filter(lambda s: any(c.isupper() for c in s))
        ))

    Then in Gherkin::

        Given any valid password <P>
    """
    _registry[name.lower()] = factory


def resolve_strategy(name: str) -> st.SearchStrategy:
    """Resolve a strategy name to a Hypothesis SearchStrategy.

    Raises ValueError with a list of available strategies if not found.
    """
    factory = _registry.get(name.lower())
    if not factory:
        available = ", ".join(sorted(_registry.keys()))
        raise ValueError(f'Unknown strategy "{name}". Registered: {available}')
    return factory()


def list_strategies() -> list[str]:
    """Return all registered strategy names, sorted."""
    return sorted(_registry.keys())


# ── Built-in Strategies ─────────────────────────────────────────────────────

# Primitives
register_strategy("text", lambda: st.text())
register_strategy("non-empty text", lambda: st.text(min_size=1))
register_strategy("integer", lambda: st.integers())
register_strategy("positive integer", lambda: st.integers(min_value=1))
register_strategy("negative integer", lambda: st.integers(max_value=-1))
register_strategy("natural", lambda: st.integers(min_value=0))
register_strategy("float", lambda: st.floats(allow_nan=False, allow_infinity=False))
register_strategy("boolean", lambda: st.booleans())

# Strings
register_strategy("ascii text", lambda: st.text(alphabet=st.characters(codec="ascii")))
register_strategy(
    "alphanumeric",
    lambda: st.from_regex(r"[a-z0-9]+", fullmatch=True),
)
register_strategy(
    "hex string",
    lambda: st.from_regex(r"[0-9a-f]+", fullmatch=True),
)

# Identifiers
register_strategy("uuid", lambda: st.uuids().map(str))
register_strategy("email", lambda: st.emails())
register_strategy(
    "url", lambda: st.from_regex(r"https://[a-z]+\.[a-z]{2,4}/[a-z]*", fullmatch=True)
)

# Temporal
register_strategy("date", lambda: st.dates())

# Structured
register_strategy(
    "json value",
    lambda: st.recursive(
        st.none() | st.booleans() | st.integers() | st.floats(allow_nan=False) | st.text(),
        lambda children: st.lists(children) | st.dictionaries(st.text(), children),
        max_leaves=5,
    ),
)
register_strategy("json object", lambda: st.dictionaries(st.text(), st.text()))

# Domain defaults
register_strategy("password", lambda: st.text(min_size=8, max_size=128))
register_strategy(
    "username",
    lambda: st.from_regex(r"[a-z0-9_]{3,32}", fullmatch=True),
)
