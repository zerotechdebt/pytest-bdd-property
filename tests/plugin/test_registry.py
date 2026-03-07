"""Tests for strategy registry (registry.py)."""

from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from pytest_bdd_property.registry import (
    list_strategies,
    register_strategy,
    resolve_strategy,
)


@pytest.mark.RID_PLG_REG_001
def test_register_and_resolve():
    """REG-001: Register factory, resolve, check returns strategy."""
    register_strategy("test-custom", lambda: st.just("hello"))
    result = resolve_strategy("test-custom")
    assert result is not None


@pytest.mark.RID_PLG_REG_002
def test_case_insensitive():
    """REG-002: Register 'Valid Email', resolve 'valid email'."""
    register_strategy("Valid Email Test", lambda: st.just("a@b.com"))
    result = resolve_strategy("valid email test")
    assert result is not None


@pytest.mark.RID_PLG_REG_003
def test_overwrite():
    """REG-003: Register twice, second factory wins."""
    register_strategy("overwrite-test", lambda: st.just("first"))
    register_strategy("overwrite-test", lambda: st.just("second"))
    result = resolve_strategy("overwrite-test")

    @settings(max_examples=1)
    @given(val=result)
    def check(val):
        assert val == "second"

    check()


@pytest.mark.RID_PLG_REG_004
def test_unknown_raises():
    """REG-004: Resolve unknown name -> ValueError with available names."""
    with pytest.raises(ValueError, match="Unknown strategy") as exc_info:
        resolve_strategy("nonexistent-type-xyz")
    assert "Registered:" in str(exc_info.value)


@pytest.mark.RID_PLG_REG_005
def test_builtin_count():
    """REG-005: list_strategies() has >=16 entries including core types."""
    strategies = list_strategies()
    assert len(strategies) >= 16
    for name in ["text", "integer", "email", "uuid", "date"]:
        assert name in strategies
