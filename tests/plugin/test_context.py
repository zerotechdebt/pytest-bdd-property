"""Tests for PropertyContext lifecycle (context.py + plugin.py context management)."""

from __future__ import annotations

import pytest

import pytest_bdd_property.plugin as plugin
from pytest_bdd_property.context import PropertyContext


@pytest.mark.RID_PLG_CTX_001
def test_fresh_context_empty():
    """CTX-001: PropertyContext() has empty strategies, assumptions, actions, assertions."""
    ctx = PropertyContext()
    assert ctx.strategies == {}
    assert ctx.assumptions == []
    assert ctx.actions == []
    assert ctx.assertions == []


@pytest.mark.RID_PLG_CTX_002
def test_context_created_on_demand(property_mode):
    """CTX-002: _get_or_create_context() creates when None."""
    assert plugin._active_context is None
    ctx = plugin._get_or_create_context()
    assert ctx is not None
    assert isinstance(ctx, PropertyContext)
    assert plugin._active_context is ctx


@pytest.mark.RID_PLG_CTX_003
def test_context_reset():
    """CTX-003: _reset_context() clears everything."""
    plugin._is_property_scenario = True
    plugin._get_or_create_context()
    assert plugin._active_context is not None

    plugin._reset_context()
    assert plugin._active_context is None
    assert plugin._is_property_scenario is False


@pytest.mark.RID_PLG_CTX_004
def test_no_context_non_property():
    """CTX-004: get_context() is None when not property-based."""
    plugin._is_property_scenario = False
    assert plugin.get_context() is None
    assert plugin.is_property_based() is False
