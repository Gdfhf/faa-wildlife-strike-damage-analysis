from __future__ import annotations

import pandas as pd
import numpy as np

from src.data.loaders import load_simulation_donors
from src.simulation.scenario import Scenario


class DonorSampler:
    """
    Build Monte Carlo scenario rows using historically compatible
    donor records from the 1990-2021 reference population.
    """

    def __init__(self, donor_data: pd.DataFrame | None = None):
        if donor_data is None:
            donor_data = load_simulation_donors()

        self.donor_data = donor_data

    def _required_filters(self, scenario: Scenario) -> dict:
        """
        Return the fields that define the required historical
        compatibility pool.
        """
        filters = {
            "AC_CLASS": scenario.ac_class,
            "AC_MASS_GROUP": scenario.ac_mass_group,
            "SEASON": scenario.season,
            "PHASE_OF_FLIGHT": scenario.phase_of_flight,
        }

        if scenario.airport_id:
            filters["AIRPORT_ID"] = scenario.airport_id
        else:
            filters["FAAREGION"] = scenario.faa_region

        return filters

    def get_compatible_donors(
        self,
        scenario: Scenario,
    ) -> pd.DataFrame:
        """
        Return donor rows matching the required scenario context.
        """
        scenario.validate()

        filters = self._required_filters(scenario)

        work = self.donor_data
        mask = pd.Series(True, index=work.index)

        for column, value in filters.items():
            mask &= work[column].eq(value)

        return work.loc[mask].copy()

    def sample(
        self,
        scenario: Scenario,
        n_trials: int = 10_000,
        random_state: int | None = None,
    ) -> pd.DataFrame:
        """
        Generate Monte Carlo scenario rows.

        Whole historically compatible donor rows are sampled with
        replacement. User-provided fields then overwrite donor values.

        Unspecified fields retain their sampled historical values.
        """
        if n_trials <= 0:
            raise ValueError("n_trials must be greater than zero.")

        donors = self.get_compatible_donors(scenario)

        if donors.empty:
            raise ValueError(
                "No historically compatible donor rows were found. "
                "Simulation cannot proceed."
            )

        rng = np.random.default_rng(random_state)

        sampled_positions = rng.integers(
            low=0,
            high=len(donors),
            size=n_trials,
        )

        sampled = (
            donors.iloc[sampled_positions]
            .copy()
            .reset_index(drop=True)
        )

        overrides = scenario.to_model_overrides()

        for column, value in overrides.items():
            if column in sampled.columns:
                sampled[column] = value

        return sampled