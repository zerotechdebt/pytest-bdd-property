"""
pytest-bdd-property: Property-based testing for Gherkin scenarios.

Express universal invariants in standard Gherkin, executed by Hypothesis.

Usage:
    1. Tag scenarios with @property-based
    2. Use "Given any <type> <var>" to bind strategies
    3. Use property_when/property_then for When/Then steps
    4. Hypothesis runs 100+ generated inputs automatically

Example feature:
    @property-based
    Scenario: Wrong password never verifies
        Given any text <P>
        And any text <Q>
        And <P> is not equal to <Q>
        When <P> is hashed producing <H>
        Then <Q> does not verify against <H>
"""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _version

from pytest_bdd_property.assumptions import (
    parse_assumption,
    register_assumption,
)
from pytest_bdd_property.context import PropertyContext
from pytest_bdd_property.helpers import property_then, property_when
from pytest_bdd_property.registry import (
    list_strategies,
    register_strategy,
    resolve_strategy,
)
from pytest_bdd_property.runner import run_property_test

__all__ = [
    "register_strategy",
    "resolve_strategy",
    "list_strategies",
    "register_assumption",
    "parse_assumption",
    "PropertyContext",
    "property_when",
    "property_then",
    "run_property_test",
]

try:
    __version__ = _version("pytest-bdd-property")
except PackageNotFoundError:  # source tree that isn't installed
    __version__ = "0.0.0+unknown"
