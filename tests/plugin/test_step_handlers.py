"""Tests for step dispatch in plugin.py."""

from __future__ import annotations

import pytest

import pytest_bdd_property.plugin as plugin
from pytest_bdd_property.helpers import property_then, property_when


@pytest.mark.RID_PLG_DISPATCH_001
def test_given_binds_strategy(property_mode):
    """DISPATCH-001: handle_given_step('any text <P>') adds to ctx.strategies."""
    result = plugin.handle_given_step("any text <P>")
    assert result is True
    ctx = plugin.get_context()
    assert ctx is not None
    assert "P" in ctx.strategies


@pytest.mark.RID_PLG_DISPATCH_002
def test_given_registers_assumption(property_mode):
    """DISPATCH-002: handle_given_step('<P> is not equal to <Q>') adds assumption."""
    # First register strategies so the assumption has variables to reference
    plugin.handle_given_step("any text <P>")
    plugin.handle_given_step("any text <Q>")

    result = plugin.handle_given_step("<P> is not equal to <Q>")
    assert result is True
    ctx = plugin.get_context()
    assert ctx is not None
    assert len(ctx.assumptions) == 1


@pytest.mark.RID_PLG_DISPATCH_003
def test_non_property_skipped():
    """DISPATCH-003: When _is_property_scenario=False, non-property steps return False."""
    plugin._is_property_scenario = False
    # A step that doesn't match any property pattern is silently skipped
    result = plugin.handle_given_step("some unrelated step text")
    assert result is False
    # When/Then steps that don't match patterns also return False
    result = plugin.handle_when_step("some unrelated when step")
    assert result is False
    result = plugin.handle_then_step("some unrelated then step")
    assert result is False


@pytest.mark.RID_PLG_DISPATCH_004
def test_when_dispatches_action(property_mode):
    """DISPATCH-004: handle_when_step with matching pattern -> ctx.actions."""

    @property_when(r"<(\w+)> is hashed producing <(\w+)>")
    def hash_step(vals, results, pw_var, hash_var):
        pass

    result = plugin.handle_when_step("<P> is hashed producing <H>")
    assert result is True
    ctx = plugin.get_context()
    assert ctx is not None
    assert len(ctx.actions) == 1


@pytest.mark.RID_PLG_DISPATCH_005
def test_then_dispatches_assertion(property_mode):
    """DISPATCH-005: handle_then_step with matching pattern -> ctx.assertions."""

    @property_then(r"<(\w+)> verifies against <(\w+)>")
    def verify_step(vals, results, pw_var, hash_var):
        pass

    result = plugin.handle_then_step("<P> verifies against <H>")
    assert result is True
    ctx = plugin.get_context()
    assert ctx is not None
    assert len(ctx.assertions) == 1
