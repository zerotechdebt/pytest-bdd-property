"""Execution engine: runs accumulated property context via Hypothesis."""

from __future__ import annotations

from typing import Any

from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st

from .context import PropertyContext


def run_property_test(prop_ctx: PropertyContext) -> None:
    """Execute a property-based test using Hypothesis.

    This is Phase 2 of the two-phase execution model.

    Phase 1 (during normal pytest-bdd step execution):
      - "Given any text <P>" → registered a strategy
      - "And <P> is not equal to <Q>" → registered an assumption
      - "When <P> is hashed producing <H>" → registered an action callback
      - "Then <Q> does not verify against <H>" → registered an assertion

    Phase 2 (this function):
      - Build a composite strategy from all registered strategies
      - Wrap everything in @given:
          1. Apply assumptions (hypothesis.assume)
          2. Execute action callbacks (When steps)
          3. Execute assertion callbacks (Then steps)
      - Hypothesis runs this 100+ times with generated inputs
      - On failure, shrink to minimal counterexample
    """
    if not prop_ctx.strategies:
        raise ValueError("No strategies registered in @property-based scenario")

    # Build composite strategy: {"P": <generated>, "Q": <generated>, ...}
    composite = st.fixed_dictionaries(prop_ctx.strategies)

    num_runs = prop_ctx.settings.get("num_runs", 100)
    seed = prop_ctx.settings.get("seed", None)

    test_settings = settings(
        max_examples=num_runs,
        database=None,
        suppress_health_check=[HealthCheck.too_slow, HealthCheck.filter_too_much],
        derandomize=seed is not None,
    )

    @test_settings
    @given(vals=composite)
    def property_test(vals: dict[str, Any]) -> None:
        # 1. Apply assumptions
        for check in prop_ctx.assumptions:
            assume(check(vals))

        # 2. Execute action steps (When)
        results: dict[str, Any] = {}
        for action in prop_ctx.actions:
            action(vals, results)

        # 3. Execute assertion steps (Then)
        for assertion in prop_ctx.assertions:
            assertion(vals, results)

    property_test()
