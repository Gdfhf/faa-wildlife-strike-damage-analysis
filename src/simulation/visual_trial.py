from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class VisualTrial:
    """
    One realized Monte Carlo trial retained for illustrative use.

    This object does not perform simulation or prediction. It only
    preserves the context, probabilities, and stochastic outcomes
    already produced by SimulationEngine.
    """

    trial_index: int

    # Scenario explicitly supplied by the user.
    scenario: dict[str, Any]

    # Full realized context after donor sampling + user overrides.
    sampled_context: dict[str, Any]

    # Primary damage outcome.
    damage_probability: float
    damaged: bool

    # Conditional severity outcome.
    severity_probability: float | None = None
    severe: bool | None = None

    # Conditional component outcomes.
    component_probabilities: dict[str, float] = field(
        default_factory=dict
    )

    component_outcomes: dict[str, bool] = field(
        default_factory=dict
    )