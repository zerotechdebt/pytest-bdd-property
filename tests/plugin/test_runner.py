"""Tests for the property test runner (runner.py)."""

from __future__ import annotations

import pytest
from hypothesis import strategies as st

from pytest_bdd_property.context import PropertyContext
from pytest_bdd_property.runner import run_property_test


@pytest.mark.RID_PLG_RUN_001
def test_composite_strategy():
    """RUN-001: Register two strategies, run, verify both keys in vals."""
    seen_keys: list[set[str]] = []

    ctx = PropertyContext()
    ctx.strategies["P"] = st.text()
    ctx.strategies["N"] = st.integers()
    ctx.settings = {"num_runs": 10}

    def check_action(vals, results):
        seen_keys.append(set(vals.keys()))

    ctx.actions.append(check_action)
    run_property_test(ctx)

    assert len(seen_keys) >= 1
    for keys in seen_keys:
        assert keys == {"P", "N"}


@pytest.mark.RID_PLG_RUN_002
def test_assumption_filtering():
    """RUN-002: Integer strategy + positive assumption -> all vals > 0."""
    seen_values: list[int] = []

    ctx = PropertyContext()
    ctx.strategies["N"] = st.integers(min_value=-100, max_value=100)
    ctx.assumptions.append(lambda vals: vals["N"] > 0)
    ctx.settings = {"num_runs": 20}

    def collect_action(vals, results):
        seen_values.append(vals["N"])

    ctx.actions.append(collect_action)
    run_property_test(ctx)

    assert len(seen_values) >= 1
    assert all(v > 0 for v in seen_values)


@pytest.mark.RID_PLG_RUN_003
def test_action_ordering():
    """RUN-003: Two actions, verify order via side effects."""
    order: list[str] = []

    ctx = PropertyContext()
    ctx.strategies["X"] = st.just(1)
    ctx.settings = {"num_runs": 5}

    ctx.actions.append(lambda vals, results: order.append("A"))
    ctx.actions.append(lambda vals, results: order.append("B"))

    run_property_test(ctx)

    # Each run should produce "A", "B" in order
    assert len(order) >= 2
    for i in range(0, len(order), 2):
        assert order[i] == "A"
        assert order[i + 1] == "B"


@pytest.mark.RID_PLG_RUN_004
def test_assertion_after_action():
    """RUN-004: Action stores result, assertion reads it."""
    ctx = PropertyContext()
    ctx.strategies["X"] = st.integers(min_value=1, max_value=100)
    ctx.settings = {"num_runs": 10}

    def store_action(vals, results):
        results["doubled"] = vals["X"] * 2

    def check_assertion(vals, results):
        assert results["doubled"] == vals["X"] * 2

    ctx.actions.append(store_action)
    ctx.assertions.append(check_assertion)

    run_property_test(ctx)


@pytest.mark.RID_PLG_RUN_005
def test_shrinking():
    """RUN-005: Failing property -> error contains counterexample."""
    ctx = PropertyContext()
    ctx.strategies["N"] = st.integers(min_value=0, max_value=100)
    ctx.settings = {"num_runs": 50}

    def failing_assertion(vals, results):
        assert vals["N"] <= 5, f"N={vals['N']} is too large"

    ctx.assertions.append(failing_assertion)

    with pytest.raises(Exception) as exc_info:
        run_property_test(ctx)
    # Hypothesis wraps failures; check that we get useful info
    error_text = str(exc_info.value)
    assert "N" in error_text or "too large" in error_text or "Falsifying" in str(exc_info.typename)


@pytest.mark.RID_PLG_RUN_006
def test_no_strategies_raises():
    """RUN-006: Empty ctx -> ValueError 'No strategies registered'."""
    ctx = PropertyContext()
    with pytest.raises(ValueError, match="No strategies registered"):
        run_property_test(ctx)


@pytest.mark.RID_PLG_RUN_007
def test_settings_control_execution():
    """RUN-007: numRuns=7 and seed=42 -> action runs exactly 7 times."""
    call_count = 0

    ctx = PropertyContext()
    ctx.strategies["X"] = st.integers(min_value=0, max_value=1000)
    ctx.settings = {"num_runs": 7, "seed": 42}

    def count_action(vals, results):
        nonlocal call_count
        call_count += 1

    ctx.actions.append(count_action)
    run_property_test(ctx)

    assert call_count == 7
