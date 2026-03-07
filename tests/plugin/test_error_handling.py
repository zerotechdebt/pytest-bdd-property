"""Tests for error handling paths across all modules."""

from __future__ import annotations

import pytest

import pytest_bdd_property.plugin as plugin
from pytest_bdd_property.helpers import property_then, property_when


@pytest.mark.RID_PLG_ERR_001
def test_strategy_outside_property():
    """ERR-001: handle_given_step('any text <P>') when not property -> raises error."""
    plugin._is_property_scenario = False
    with pytest.raises(RuntimeError, match="@property-based"):
        plugin.handle_given_step("any text <P>")


@pytest.mark.RID_PLG_ERR_001
def test_assumption_outside_property():
    """ERR-001: assumption Given step outside property-based -> raises error."""
    plugin._is_property_scenario = False
    with pytest.raises(RuntimeError, match="@property-based"):
        plugin.handle_given_step("<P> is not equal to <Q>")


@pytest.mark.RID_PLG_ERR_002
def test_unknown_strategy_in_step(property_mode):
    """ERR-002: handle_given_step('any bogus-type <P>') -> ValueError listing strategies."""
    with pytest.raises(ValueError, match="Unknown strategy"):
        plugin.handle_given_step("any bogus-type <P>")


@pytest.mark.RID_PLG_ERR_003
def test_unrecognized_assumption(property_mode):
    """ERR-003: handle_given_step('<X> smells funny') -> raises error."""
    with pytest.raises(ValueError, match="register_assumption"):
        plugin.handle_given_step("<X> smells funny")


@pytest.mark.RID_PLG_ERR_004
def test_when_outside_property():
    """ERR-004: handle_when_step(...) when not property -> raises error."""

    @property_when(r"<(\w+)> is hashed producing <(\w+)>")
    def hash_step(vals, results, pw_var, hash_var):
        pass

    plugin._is_property_scenario = False
    with pytest.raises(RuntimeError, match="@property-based"):
        plugin.handle_when_step("<P> is hashed producing <H>")


@pytest.mark.RID_PLG_ERR_004
def test_then_outside_property():
    """ERR-004: handle_then_step(...) when not property -> raises error."""

    @property_then(r"<(\w+)> verifies against <(\w+)>")
    def verify_step(vals, results, pw_var, hash_var):
        pass

    plugin._is_property_scenario = False
    with pytest.raises(RuntimeError, match="@property-based"):
        plugin.handle_then_step("<P> verifies against <H>")
