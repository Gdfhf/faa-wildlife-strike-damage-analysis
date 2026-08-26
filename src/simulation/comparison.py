from __future__ import annotations

from dataclasses import dataclass, field

from src.simulation.engine import (
    SimulationEngine,
    SimulationResult,
)
from src.simulation.scenario import Scenario


@dataclass
class MetricDifference:
    scenario_a: float | None
    scenario_b: float | None
    absolute_difference: float | None
    relative_change: float | None


@dataclass
class ComparisonResult:
    scenario_a_result: SimulationResult
    scenario_b_result: SimulationResult

    damage_probability: MetricDifference

    severity_probability: MetricDifference

    component_probabilities: dict[
        str,
        MetricDifference
    ] = field(default_factory=dict)


def _compare_metric(
    value_a: float | None,
    value_b: float | None,
) -> MetricDifference:
    """
    Compare two numeric simulation metrics.

    Absolute difference is B - A.

    Relative change is also measured from A to B:
        (B - A) / A

    Relative change is unavailable when A is zero or either
    value is missing.
    """
    if value_a is None or value_b is None:
        return MetricDifference(
            scenario_a=value_a,
            scenario_b=value_b,
            absolute_difference=None,
            relative_change=None,
        )

    difference = value_b - value_a

    if value_a == 0:
        relative_change = None
    else:
        relative_change = difference / value_a

    return MetricDifference(
        scenario_a=value_a,
        scenario_b=value_b,
        absolute_difference=difference,
        relative_change=relative_change,
    )


class ScenarioComparator:
    """
    Compare two operational Monte Carlo scenarios.

    Both simulations use the same number of trials and random seed
    so differences are driven as consistently as possible by the
    requested scenario changes rather than arbitrary run settings.
    """

    def __init__(
        self,
        engine: SimulationEngine | None = None,
    ):
        self.engine = engine or SimulationEngine()

    def compare(
        self,
        scenario_a: Scenario,
        scenario_b: Scenario,
        n_trials: int = 10_000,
        seed: int | None = 42,
    ) -> ComparisonResult:

        result_a = self.engine.run(
            scenario=scenario_a,
            n_trials=n_trials,
            seed=seed,
        )

        result_b = self.engine.run(
            scenario=scenario_b,
            n_trials=n_trials,
            seed=seed,
        )

        damage_difference = _compare_metric(
            result_a.mean_damage_probability,
            result_b.mean_damage_probability,
        )

        severity_difference = _compare_metric(
            result_a.severity_probability_mean_damaged,
            result_b.severity_probability_mean_damaged,
        )

        components = set(
            result_a.component_probability_means_damaged
        ) | set(
            result_b.component_probability_means_damaged
        )

        component_differences = {}

        for component in sorted(components):
            value_a = (
                result_a
                .component_probability_means_damaged
                .get(component)
            )

            value_b = (
                result_b
                .component_probability_means_damaged
                .get(component)
            )

            component_differences[component] = (
                _compare_metric(
                    value_a,
                    value_b,
                )
            )

        return ComparisonResult(
            scenario_a_result=result_a,
            scenario_b_result=result_b,
            damage_probability=damage_difference,
            severity_probability=severity_difference,
            component_probabilities=component_differences,
        )