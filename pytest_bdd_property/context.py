"""PropertyContext: accumulated state for a @property-based scenario."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from hypothesis import strategies as st

from .types import AssumptionFn, StepCallback


@dataclass
class PropertyContext:
    """Accumulated state for a single @property-based scenario.

    Built up during Phase 1 (registration), consumed during Phase 2 (execution).
    """

    strategies: dict[str, st.SearchStrategy[Any]] = field(default_factory=dict)
    assumptions: list[AssumptionFn] = field(default_factory=list)
    actions: list[StepCallback] = field(default_factory=list)
    assertions: list[StepCallback] = field(default_factory=list)
    settings: dict[str, Any] = field(default_factory=dict)
