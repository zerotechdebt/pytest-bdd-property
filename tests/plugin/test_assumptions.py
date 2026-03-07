"""Tests for assumption pattern registry (assumptions.py)."""

from __future__ import annotations

import pytest

from pytest_bdd_property.assumptions import (
    _patterns,
    parse_assumption,
    register_assumption,
)


@pytest.mark.RID_PLG_ASM_001
def test_register_and_parse():
    """ASM-001: Register custom pattern, parse step text, get AssumptionFn."""
    register_assumption(
        r"^<(\w+)> is positive$",
        lambda var: lambda vals: vals[var] > 0,
    )
    fn = parse_assumption("<N> is positive")
    assert fn is not None
    assert fn({"N": 5}) is True
    assert fn({"N": -1}) is False


@pytest.mark.RID_PLG_ASM_002
def test_unrecognized_returns_none():
    """ASM-002: Parse unknown text -> None."""
    result = parse_assumption("something completely unknown")
    assert result is None


@pytest.mark.RID_PLG_ASM_003
def test_builtin_count():
    """ASM-003: Count patterns >= 12."""
    assert len(_patterns) >= 12


@pytest.mark.RID_PLG_ASM_004
def test_emptiness_generalizes_to_arrays_and_nulls():
    """ASM-004: is empty / is not empty handle arrays and None."""
    not_empty = parse_assumption("<X> is not empty")
    assert not_empty is not None
    assert not_empty({"X": [1, 2]}) is True
    assert not_empty({"X": []}) is False
    assert not_empty({"X": None}) is False

    is_empty = parse_assumption("<X> is empty")
    assert is_empty is not None
    assert is_empty({"X": []}) is True
    assert is_empty({"X": None}) is True
    assert is_empty({"X": [1, 2]}) is False
