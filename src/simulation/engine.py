from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from src.simulation.scenario import Scenario
from src.simulation.support import SupportEvaluator
from src.simulation.donor_sampling import DonorSampler
from src.simulation.prediction import PredictionService


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

        rng = np.random.default_rng(seed)

        damage_outcomes = (
            rng.random(n_trials)
            < damage_probabilities
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
            )

        # -------------------------------------------------
        # Conditional damaged population
        # -------------------------------------------------

        damaged_rows = (
            rows.loc[damage_outcomes]
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

        for component, probabilities in (
            component_probabilities.items()
        ):
            outcomes = (
                rng.random(damage_count)
                < probabilities
            )

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
        )