"""pytest plugin: integrates property-based testing with pytest-bdd.

This plugin intercepts pytest-bdd scenario execution for scenarios tagged
with @property-based, replacing normal step-by-step execution with the
two-phase registration/execution model powered by Hypothesis.

Architecture:
  Phase 1 — During normal step execution, property-based steps register
  strategies, assumptions, and callbacks into a shared PropertyContext.

  Phase 2 — After all steps run, a pytest hook triggers Hypothesis to
  run the registered property 100+ times with generated inputs.
"""

from __future__ import annotations

import re
from typing import Any

import pytest

from .assumptions import parse_assumption
from .context import PropertyContext
from .helpers import match_property_then, match_property_when
from .registry import resolve_strategy
from .runner import run_property_test
from .types import StepCallback

# ── Thread-local property context ──────────────────────────────────────────

_active_context: PropertyContext | None = None
_is_property_scenario: bool = False


def _get_or_create_context() -> PropertyContext:
    global _active_context
    if _active_context is None:
        _active_context = PropertyContext()
    return _active_context


def _reset_context() -> None:
    global _active_context, _is_property_scenario
    _active_context = None
    _is_property_scenario = False


def get_context() -> PropertyContext | None:
    """Get the current property context (public API)."""
    return _active_context


def is_property_based() -> bool:
    """Check if currently executing a property-based scenario."""
    return _is_property_scenario


# ── Tag patterns ───────────────────────────────────────────────────────────

_NUM_RUNS_RE = re.compile(r"num-runs:(\d+)")
_SEED_RE = re.compile(r"seed:(\d+)")


def _parse_settings_from_tags(tags: set[str]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for tag in tags:
        m = _NUM_RUNS_RE.match(tag)
        if m:
            result["num_runs"] = int(m.group(1))
        m = _SEED_RE.match(tag)
        if m:
            result["seed"] = int(m.group(1))
        if tag == "verbose":
            result["verbose"] = True
    return result


# ── Step interpretation (called from conftest step definitions) ────────────

_STRATEGY_RE = re.compile(r"^any (.+) <(\w+)>$")


def handle_given_step(step_text: str) -> bool:
    """Process a Given step for property-based scenarios.

    Returns True if the step was handled (strategy or assumption).
    """
    # Strategy binding: "any <type> <var>"
    m = _STRATEGY_RE.match(step_text)
    if m:
        if not _is_property_scenario:
            raise RuntimeError("'Given any <type> <var>' requires @property-based tag")
        type_name, var_name = m.groups()
        ctx = _get_or_create_context()
        ctx.strategies[var_name] = resolve_strategy(type_name)
        return True

    # Assumption pattern
    assumption = parse_assumption(step_text)
    if assumption:
        if not _is_property_scenario:
            raise RuntimeError("Assumption steps require @property-based tag")
        ctx = _get_or_create_context()
        ctx.assumptions.append(assumption)
        return True

    # Looks like it could be an assumption but didn't match any pattern
    if _is_property_scenario and re.match(r"<\w+>", step_text):
        raise ValueError(
            f'Unrecognized assumption: "{step_text}". '
            "Register a custom pattern with register_assumption()."
        )

    return False


def handle_when_step(step_text: str) -> bool:
    """Process a When step for property-based scenarios."""
    match = match_property_when(step_text)
    if match:
        if not _is_property_scenario:
            raise RuntimeError("property_when steps require @property-based tag")
        fn, captures = match
        ctx = _get_or_create_context()

        def _make_action(_fn: Any = fn, _caps: tuple[str, ...] = captures) -> StepCallback:
            def action(vals: dict[str, Any], results: dict[str, Any]) -> None:
                _fn(vals, results, *_caps)

            return action

        ctx.actions.append(_make_action())
        return True
    return False


def handle_then_step(step_text: str) -> bool:
    """Process a Then step for property-based scenarios."""
    match = match_property_then(step_text)
    if match:
        if not _is_property_scenario:
            raise RuntimeError("property_then steps require @property-based tag")
        fn, captures = match
        ctx = _get_or_create_context()

        def _make_assertion(_fn: Any = fn, _caps: tuple[str, ...] = captures) -> StepCallback:
            def assertion(vals: dict[str, Any], results: dict[str, Any]) -> None:
                _fn(vals, results, *_caps)

            return assertion

        ctx.assertions.append(_make_assertion())
        return True
    return False


# ── pytest hooks ───────────────────────────────────────────────────────────


def _scenario_has_tag(item: pytest.Item, tag: str) -> bool:
    for marker in item.iter_markers():
        if marker.name == tag:
            return True
    return False


def _get_scenario_tags(item: pytest.Item) -> set[str]:
    return {marker.name for marker in item.iter_markers()}


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item: pytest.Item) -> None:
    """Before each test: detect if it's property-based and set up context."""
    global _is_property_scenario
    _reset_context()

    if _scenario_has_tag(item, "property-based"):
        _is_property_scenario = True
        ctx = _get_or_create_context()
        ctx.settings = _parse_settings_from_tags(_get_scenario_tags(item))


@pytest.hookimpl(trylast=True)
def pytest_runtest_call(item: pytest.Item) -> None:
    """After step execution: if property-based, run through Hypothesis."""
    if not _is_property_scenario:
        return

    ctx = _active_context
    if ctx is None or not ctx.strategies:
        return

    run_property_test(ctx)


@pytest.hookimpl(trylast=True)
def pytest_runtest_teardown(item: pytest.Item) -> None:
    """Clean up after each test."""
    _reset_context()
