from dataclasses import dataclass

import pandas as pd

from src.data.loaders import load_scenario_support
from src.simulation.scenario import Scenario


@dataclass(frozen=True)
class SupportResult:
    supported: bool
    exact_count: int
    geography_level: str
    filters_used: dict
    message: str


class SupportEvaluator:
    """
    Evaluate historical support for user-defined scenarios.

    The underlying support artifact contains only the
    1990-2021 development/reference period.
    """

    def __init__(self, support_data: pd.DataFrame | None = None):
        if support_data is None:
            support_data = load_scenario_support()

        self.support_data = support_data

    def evaluate(self, scenario: Scenario) -> SupportResult:
        """
        Count historical rows matching the required scenario context.

        Zero exact matches are blocked to remain consistent with
        Notebook 10.
        """
        scenario.validate()

        filters = {
            "AC_CLASS": scenario.ac_class,
            "AC_MASS_GROUP": scenario.ac_mass_group,
            "SEASON": scenario.season,
            "PHASE_OF_FLIGHT": scenario.phase_of_flight,
        }

        if scenario.airport_id:
            filters["AIRPORT_ID"] = scenario.airport_id
            geography_level = "airport"

        else:
            filters["FAAREGION"] = scenario.faa_region
            geography_level = "region"

        work = self.support_data

        mask = pd.Series(True, index=work.index)

        for column, value in filters.items():
            mask &= work[column].eq(value)

        exact_count = int(mask.sum())

        if exact_count == 0:
            return SupportResult(
                supported=False,
                exact_count=0,
                geography_level=geography_level,
                filters_used=filters,
                message=(
                    "No historical records were found for this exact "
                    "required scenario combination in the 1990-2021 "
                    "reference period. Simulation should be blocked."
                ),
            )

        return SupportResult(
            supported=True,
            exact_count=exact_count,
            geography_level=geography_level,
            filters_used=filters,
            message=(
                f"{exact_count:,} historical reference records support "
                "this required scenario combination."
            ),
        )