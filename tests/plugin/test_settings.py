"""Tests for settings parsing from tags (plugin.py)."""

from __future__ import annotations

import pytest

from pytest_bdd_property.plugin import _parse_settings_from_tags


@pytest.mark.RID_PLG_SET_001
def test_num_runs():
    """SET-001: num-runs:50 -> {'num_runs': 50}."""
    result = _parse_settings_from_tags({"num-runs:50"})
    assert result["num_runs"] == 50


@pytest.mark.RID_PLG_SET_002
def test_seed():
    """SET-002: seed:42 -> {'seed': 42}."""
    result = _parse_settings_from_tags({"seed:42"})
    assert result["seed"] == 42


@pytest.mark.RID_PLG_SET_003
def test_verbose():
    """SET-003: verbose -> {'verbose': True}."""
    result = _parse_settings_from_tags({"verbose"})
    assert result["verbose"] is True


@pytest.mark.RID_PLG_SET_004
def test_unknown_ignored():
    """SET-004: unknown-tag -> {}."""
    result = _parse_settings_from_tags({"unknown-tag"})
    assert result == {}
