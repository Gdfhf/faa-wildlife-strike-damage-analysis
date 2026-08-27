from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd

from src.simulation.scenario import Scenario
from src.simulation.support import SupportEvaluator
from src.simulation.donor_sampling import DonorSampler
from src.simulation.prediction import PredictionService


# Scenario-eligible fields retained for the illustrative Godot trial.
VISUAL_CONTEXT_FIELDS = [
    "AIRPORT_ID",
    "FAAREGION",
    "AC_CLASS",
    "AC_MASS_GROUP",
    "SEASON",
    "PHASE_OF_FLIGHT",
    "WILDLIFE_TYPE",
    "SIZE",
    "NUM_STRUCK",
    "TYPE_ENG",
    "NUM_ENGS",
    "WARNED",
    "HEIGHT",
    "SPEED",
    "TIME_OF_DAY",
    "SKY",
    "PRECIPITATION",
    "STATE",
]


def _to_python_value(value: Any) -> Any:
    """
    Convert NumPy/pandas scalar values into ordinary Python values
    suitable for later JSON serialization.
    """
    if isinstance(value, np.generic):
        value = value.item()

    if pd.isna(value):
        return None

    return value


def _extract_visual_context(row: pd.Series) -> dict[str, Any]:
    """
    Extract scenario-eligible values from one fully realized sampled
    donor row after user overrides have been applied.
    """
    return {
        column: _to_python_value(row[column])
        for column in VISUAL_CONTEXT_FIELDS
        if column in row.index
    }


@dataclass
class VisualTrial:
    """
    One already-realized Monte Carlo trial retained for illustrative use.

    This object performs no prediction or simulation. It only preserves
    values that were already produced by the validated simulation engine.
    """

    trial_index: int

    # Scenario explicitly supplied by the user.
    scenario: dict[str, Any]

    # Full trial context after donor sampling + user overrides.
    sampled_context: dict[str, Any]

    # Primary damage result.
    damage_probability: float
    damaged: bool

    # Conditional severity result.
    severity_probability: float | None = None
    severe: bool | None = None

    # Conditional component results.
    component_probabilities: dict[str, float] = field(
        default_factory=dict
    )
    component_outcomes: dict[str, bool] = field(
        default_factory=dict
    )


@dataclass
class SimulationResult:
    n_trials: int
    seed: int | None

    support_count: int
    geography_level: str

    mean_damage_probability: float
    simulated_damage_count: int
    simulated_damage_rate: float

    severity_probability_mean_damaged: float | None
    simulated_severe_count: int
    simulated_severe_rate_given_damage: float | None

    component_probability_means_damaged: dict[str, float] = field(
        default_factory=dict
    )

    component_counts: dict[str, int] = field(
        default_factory=dict
    )

    component_rates_given_damage: dict[str, float] = field(
        default_factory=dict
    )

    # One randomly selected realized trial for optional visualization.
    visual_trial: VisualTrial | None = None


class SimulationEngine:
    """
    Execute the operational Monte Carlo simulation using the
    validated Notebook 10 workflow.
    """

    def __init__(
        self,
        support_evaluator: SupportEvaluator | None = None,
        donor_sampler: DonorSampler | None = None,
        prediction_service: PredictionService | None = None,
    ):
        self.support_evaluator = (
            support_evaluator or SupportEvaluator()
        )

        self.donor_sampler = (
            donor_sampler or DonorSampler()
        )

        self.prediction_service = (
            prediction_service or PredictionService()
        )

    def run(
        self,
        scenario: Scenario,
        n_trials: int = 10_000,
        seed: int | None = 42,
    ) -> SimulationResult:
        """
        Run one Monte Carlo scenario.

        The returned SimulationResult also retains one independently
        selected realized trial for optional illustrative visualization.
        Selecting that trial uses its own RNG stream and therefore does
        not alter the existing Monte Carlo outcome sequence.
        """
        if n_trials <= 0:
            raise ValueError(
                "n_trials must be greater than zero."
            )

        scenario.validate()

        # -------------------------------------------------
        # Historical support gate
        # -------------------------------------------------

        support = self.support_evaluator.evaluate(
            scenario
        )

        if not support.supported:
            raise ValueError(
                support.message
            )

        # -------------------------------------------------
        # Generate empirical scenario trials
        # -------------------------------------------------

        rows = self.donor_sampler.sample(
            scenario=scenario,
            n_trials=n_trials,
            random_state=seed,
        )

        # -------------------------------------------------
        # Damage probability
        # -------------------------------------------------

        damage_probabilities = (
            self.prediction_service
            .predict_damage_probability(rows)
        )

        # Existing scientific outcome RNG.
        rng = np.random.default_rng(seed)

        damage_outcomes = (
            rng.random(n_trials)
            < damage_probabilities
        )

        # -------------------------------------------------
        # Select one trial for optional visualization
        # -------------------------------------------------
        #
        # This is deliberately a separate RNG stream so adding the
        # visualization feature cannot shift severity/component draws
        # or otherwise change the existing simulation results.

        if seed is None:
            visual_rng = np.random.default_rng()
        else:
            visual_rng = np.random.default_rng(
                np.random.SeedSequence(
                    [int(seed), 1]
                )
            )

        visual_index = int(
            visual_rng.integers(
                low=0,
                high=n_trials,
            )
        )

        visual_context = _extract_visual_context(
            rows.iloc[visual_index]
        )

        damage_count = int(
            damage_outcomes.sum()
        )

        damage_rate = (
            damage_count / n_trials
        )

        mean_damage_probability = float(
            damage_probabilities.mean()
        )

        # -------------------------------------------------
        # No damaged trials
        # -------------------------------------------------

        if damage_count == 0:
            visual_trial = VisualTrial(
                trial_index=visual_index,
                scenario=scenario.to_dict(),
                sampled_context=visual_context,
                damage_probability=float(
                    damage_probabilities[
                        visual_index
                    ]
                ),
                damaged=False,
                severity_probability=None,
                severe=None,
                component_probabilities={},
                component_outcomes={},
            )

            return SimulationResult(
                n_trials=n_trials,
                seed=seed,
                support_count=support.exact_count,
                geography_level=support.geography_level,
                mean_damage_probability=mean_damage_probability,
                simulated_damage_count=0,
                simulated_damage_rate=0.0,
                severity_probability_mean_damaged=None,
                simulated_severe_count=0,
                simulated_severe_rate_given_damage=None,
                component_probability_means_damaged={},
                component_counts={},
                component_rates_given_damage={},
                visual_trial=visual_trial,
            )

        # -------------------------------------------------
        # Conditional damaged population
        # -------------------------------------------------

        damaged_indices = np.flatnonzero(
            damage_outcomes
        )

        damaged_rows = (
            rows.iloc[damaged_indices]
            .reset_index(drop=True)
        )

        # -------------------------------------------------
        # Severity
        # -------------------------------------------------

        severity_probabilities = (
            self.prediction_service
            .predict_severity_probability(
                damaged_rows
            )
        )

        severity_outcomes = (
            rng.random(damage_count)
            < severity_probabilities
        )

        severe_count = int(
            severity_outcomes.sum()
        )

        severe_rate_given_damage = (
            severe_count / damage_count
        )

        severity_probability_mean = float(
            severity_probabilities.mean()
        )

        # -------------------------------------------------
        # Components
        # -------------------------------------------------

        component_probabilities = (
            self.prediction_service
            .predict_all_component_probabilities(
                damaged_rows
            )
        )

        component_probability_means = {}
        component_counts = {}
        component_rates = {}

        # Preserve the realized per-damaged-trial component arrays only
        # long enough to build the single retained visualization trial.
        component_outcome_arrays = {}

        for component, probabilities in (
            component_probabilities.items()
        ):
            outcomes = (
                rng.random(damage_count)
                < probabilities
            )

            component_outcome_arrays[
                component
            ] = outcomes

            count = int(
                outcomes.sum()
            )

            component_probability_means[
                component
            ] = float(
                probabilities.mean()
            )

            component_counts[
                component
            ] = count

            component_rates[
                component
            ] = (
                count / damage_count
            )

        # -------------------------------------------------
        # Build retained visual trial
        # -------------------------------------------------

        visual_damaged = bool(
            damage_outcomes[
                visual_index
            ]
        )

        visual_severity_probability = None
        visual_severe = None

        visual_component_probabilities = {}
        visual_component_outcomes = {}

        if visual_damaged:
            # `damaged_indices` is ordered, so searchsorted maps the
            # original trial index into the compressed damaged-only
            # severity/component population.
            damaged_position = int(
                np.searchsorted(
                    damaged_indices,
                    visual_index,
                )
            )

            visual_severity_probability = float(
                severity_probabilities[
                    damaged_position
                ]
            )

            visual_severe = bool(
                severity_outcomes[
                    damaged_position
                ]
            )

            for component, probabilities in (
                component_probabilities.items()
            ):
                visual_component_probabilities[
                    component
                ] = float(
                    probabilities[
                        damaged_position
                    ]
                )

                visual_component_outcomes[
                    component
                ] = bool(
                    component_outcome_arrays[
                        component
                    ][damaged_position]
                )

        visual_trial = VisualTrial(
            trial_index=visual_index,
            scenario=scenario.to_dict(),
            sampled_context=visual_context,
            damage_probability=float(
                damage_probabilities[
                    visual_index
                ]
            ),
            damaged=visual_damaged,
            severity_probability=
                visual_severity_probability,
            severe=visual_severe,
            component_probabilities=
                visual_component_probabilities,
            component_outcomes=
                visual_component_outcomes,
        )

        # -------------------------------------------------
        # Result
        # -------------------------------------------------

        return SimulationResult(
            n_trials=n_trials,
            seed=seed,

            support_count=support.exact_count,
            geography_level=support.geography_level,

            mean_damage_probability=
                mean_damage_probability,

            simulated_damage_count=
                damage_count,

            simulated_damage_rate=
                damage_rate,

            severity_probability_mean_damaged=
                severity_probability_mean,

            simulated_severe_count=
                severe_count,

            simulated_severe_rate_given_damage=
                severe_rate_given_damage,

            component_probability_means_damaged=
                component_probability_means,

            component_counts=
                component_counts,

            component_rates_given_damage=
                component_rates,

            visual_trial=
                visual_trial,
        )
