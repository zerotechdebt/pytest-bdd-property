"""Shared fixtures for plugin unit tests."""

from __future__ import annotations

import pytest

import pytest_bdd_property.plugin as plugin
from pytest_bdd_property.helpers import _then_patterns, _when_patterns


@pytest.fixture(autouse=True)
def _reset_plugin_state():
    """Reset plugin global state between tests."""
    plugin._reset_context()
    yield
    plugin._reset_context()


@pytest.fixture(autouse=True)
def _reset_helpers():
    """Clear helper registries between tests, preserving original patterns."""
    original_when = list(_when_patterns)
    original_then = list(_then_patterns)
    _when_patterns.clear()
    _then_patterns.clear()
    yield
    _when_patterns.clear()
    _when_patterns.extend(original_when)
    _then_patterns.clear()
    _then_patterns.extend(original_then)


@pytest.fixture()
def property_mode():
    """Enable property-based mode for the duration of the test."""
    plugin._is_property_scenario = True
    plugin._active_context = None
    yield
    plugin._reset_context()
