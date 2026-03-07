"""Tests for property_when / property_then helpers (helpers.py)."""

from __future__ import annotations

import pytest

from pytest_bdd_property.helpers import (
    _then_patterns,
    _when_patterns,
    match_property_then,
    match_property_when,
    property_then,
    property_when,
)


@pytest.mark.RID_PLG_HELP_001
def test_property_when_registers():
    """HELP-001: Decorator adds to _when_patterns."""
    assert len(_when_patterns) == 0

    @property_when(r"<(\w+)> is hashed producing <(\w+)>")
    def hash_step(vals, results, pw_var, hash_var):
        pass

    assert len(_when_patterns) == 1


@pytest.mark.RID_PLG_HELP_002
def test_property_then_registers():
    """HELP-002: Decorator adds to _then_patterns."""
    assert len(_then_patterns) == 0

    @property_then(r"<(\w+)> verifies against <(\w+)>")
    def verify_step(vals, results, pw_var, hash_var):
        pass

    assert len(_then_patterns) == 1


@pytest.mark.RID_PLG_HELP_003
def test_captures_forwarded():
    """HELP-003: Match returns (fn, captures) with correct groups."""
    captured_args = []

    @property_when(r"<(\w+)> produces <(\w+)>")
    def produce_step(vals, results, *args):
        captured_args.extend(args)

    result = match_property_when("<X> produces <Y>")
    assert result is not None
    fn, captures = result
    assert captures == ("X", "Y")

    # Execute the function to verify captures are forwarded
    fn({}, {}, *captures)
    assert captured_args == ["X", "Y"]


@pytest.mark.RID_PLG_HELP_004
def test_no_match():
    """HELP-004: match_property_when returns None for unmatched text."""
    result = match_property_when("unrelated step text")
    assert result is None

    result = match_property_then("unrelated step text")
    assert result is None
