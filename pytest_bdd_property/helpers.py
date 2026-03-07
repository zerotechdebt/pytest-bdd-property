"""property_when / property_then: step definition helpers for property scenarios."""

from __future__ import annotations

import re
from collections.abc import Callable

# Global registries for property-only steps
_when_patterns: list[tuple[re.Pattern[str], Callable[..., None]]] = []
_then_patterns: list[tuple[re.Pattern[str], Callable[..., None]]] = []


def property_when(pattern: str) -> Callable[[Callable[..., None]], Callable[..., None]]:
    """Decorator to register a When step for @property-based scenarios.

    Unlike regular @when, the callback is NOT executed immediately during
    Phase 1. Instead, it's registered as an action callback that Hypothesis
    invokes on every generated input during Phase 2.

    Example::

        @property_when(r"<(\\w+)> is hashed producing <(\\w+)>")
        def hash_step(vals, results, input_var, output_var):
            results[output_var] = hash_password(vals[input_var])

    Then in Gherkin::

        When <P> is hashed producing <H>
    """
    compiled = re.compile(pattern)

    def decorator(fn: Callable[..., None]) -> Callable[..., None]:
        _when_patterns.append((compiled, fn))
        return fn

    return decorator


def property_then(pattern: str) -> Callable[[Callable[..., None]], Callable[..., None]]:
    """Decorator to register a Then step for @property-based scenarios.

    Like property_when(), the callback is registered (not executed)
    during Phase 1. Hypothesis calls it during Phase 2.

    Raise AssertionError to signal a property violation. Hypothesis will
    then shrink to find the minimal counterexample.

    Example::

        @property_then(r"<(\\w+)> does not verify against <(\\w+)>")
        def no_verify(vals, results, pw_var, hash_var):
            assert not verify_password(vals[pw_var], results[hash_var])
    """
    compiled = re.compile(pattern)

    def decorator(fn: Callable[..., None]) -> Callable[..., None]:
        _then_patterns.append((compiled, fn))
        return fn

    return decorator


def match_property_when(
    step_text: str,
) -> tuple[Callable[..., None], tuple[str, ...]] | None:
    """Match step text against registered property_when patterns."""
    for pattern, fn in _when_patterns:
        m = pattern.match(step_text)
        if m:
            return fn, m.groups()
    return None


def match_property_then(
    step_text: str,
) -> tuple[Callable[..., None], tuple[str, ...]] | None:
    """Match step text against registered property_then patterns."""
    for pattern, fn in _then_patterns:
        m = pattern.match(step_text)
        if m:
            return fn, m.groups()
    return None
