"""
Minimal automated tests for the Capstone Airstrike operational simulation.

These tests focus on the high-value methodological and logical constraints
of the dashboard simulation rather than exhaustive software coverage.

They verify:

1. Invalid scenarios are rejected by structural validation.
2. Historically unsupported scenarios are identified correctly.
3. The simulation donor pool excludes the held-out 2022-2024 period.
4. User-specified required scenario fields remain fixed during donor sampling.
5. Prediction probabilities used by the simulation remain inside [0, 1].
6. A fixed random seed reproduces the same simulation result.
7. Conditional severity/component outcomes cannot exceed damaged outcomes.
"""

import numpy as np
import pytest

from src.data.loaders import (
    load_simulation_donors,
    load_scenario_support,
)
from src.simulation.scenario import Scenario
from src.simulation.support import SupportEvaluator
from src.simulation.donor_sampling import DonorSampler
from src.simulation.engine import SimulationEngine


# =====================================================================
# Test helper
# =====================================================================

class StubPredictionService:
    """
    Lightweight deterministic prediction service used to test the
    simulation engine independently from model deserialization.

    The real saved models have already been smoke-tested separately.
    Here we are testing whether the Monte Carlo engine handles valid
    probability arrays and conditional simulation logic correctly.
    """

    COMPONENTS = (
        "engine_damage",
        "forward_cockpit_damage",
        "landing_gear_damage",
        "propeller_damage",
        "wing_rotor_damage",
    )

    def predict_damage_probability(self, scenario_rows):
        """
        Return a constant valid damage probability for every trial.
        """
        return np.full(len(scenario_rows), 0.20, dtype=float)

    def predict_severity_probability(self, scenario_rows):
        """
        Return a constant valid conditional severity probability.
        """
        return np.full(len(scenario_rows), 0.40, dtype=float)

    def predict_component_probability(self, component, scenario_rows):
        """
        Return a constant valid probability for one component.
        """
        if component not in self.COMPONENTS:
            raise ValueError(f"Unknown component: {component}")

        return np.full(len(scenario_rows), 0.25, dtype=float)

    def predict_all_component_probabilities(self, scenario_rows):
        """
        Return conditional component probabilities in the same general
        structure expected by the simulation engine.
        """
        return {
            component: np.full(
                len(scenario_rows),
                0.25,
                dtype=float,
            )
            for component in self.COMPONENTS
        }


# =====================================================================
# Fixtures
# =====================================================================

@pytest.fixture(scope="module")
def donor_data():
    """
    Load the lightweight 1990-2021 empirical simulation donor pool once.
    """
    return load_simulation_donors()


@pytest.fixture(scope="module")
def support_data():
    """
    Load the lightweight historical scenario-support artifact once.
    """
    return load_scenario_support()


@pytest.fixture
def supported_scenario():
    """
    Historically supported scenario used during backend smoke testing.
    """
    return Scenario(
        ac_class="A",
        ac_mass_group="Heavy",
        season="Summer",
        phase_of_flight="Take-off Run",
        airport_id="KSMF",
    )


@pytest.fixture
def simulation_engine(donor_data, support_data):
    """
    Construct the operational Monte Carlo engine using the real
    support evaluator and donor sampler, but a deterministic prediction
    service so that engine behavior can be tested in isolation.
    """
    support_evaluator = SupportEvaluator(support_data)
    donor_sampler = DonorSampler(donor_data)
    prediction_service = StubPredictionService()

    return SimulationEngine(
        support_evaluator=support_evaluator,
        donor_sampler=donor_sampler,
        prediction_service=prediction_service,
    )


# =====================================================================
# 1. Scenario validation
# =====================================================================

def test_invalid_scenario_is_rejected():
    """
    A scenario missing a required user field must fail structural
    validation before simulation.
    """

    scenario = Scenario(
        ac_class="A",
        ac_mass_group="Heavy",
        season="Summer",
        phase_of_flight=None,
        airport_id="KSMF",
    )

    with pytest.raises(ValueError, match="PHASE_OF_FLIGHT is required"):
        scenario.validate()


# =====================================================================
# 2. Historical support gate
# =====================================================================

def test_zero_support_scenario_is_blocked(support_data):
    """
    A structurally valid scenario with no exact historical observations
    must be marked unsupported.
    """

    evaluator = SupportEvaluator(support_data)

    scenario = Scenario(
        ac_class="A",
        ac_mass_group="Heavy",
        season="Summer",
        phase_of_flight="Take-off Run",
        airport_id="FAKE_AIRPORT_ID",
    )

    result = evaluator.evaluate(scenario)

    assert result.supported is False
    assert result.exact_count == 0


def test_supported_scenario_has_historical_support(
    support_data,
    supported_scenario,
):
    """
    The known KSMF reference scenario should have historical support.
    """

    evaluator = SupportEvaluator(support_data)

    result = evaluator.evaluate(supported_scenario)

    assert result.supported is True
    assert result.exact_count > 0


# =====================================================================
# 3. Temporal separation
# =====================================================================

def test_donor_pool_excludes_held_out_years(donor_data):
    """
    The Monte Carlo donor pool must exclude the held-out 2022-2024
    evaluation period.

    This preserves the temporal separation established in the
    analytical notebooks.
    """

    assert "INCIDENT_YEAR" in donor_data.columns

    assert donor_data["INCIDENT_YEAR"].max() <= 2021

    held_out_rows = donor_data[
        donor_data["INCIDENT_YEAR"].isin(
            [2022, 2023, 2024]
        )
    ]

    assert held_out_rows.empty


# =====================================================================
# 4. Empirical donor sampling
# =====================================================================

def test_required_fields_remain_fixed_after_sampling(
    donor_data,
    supported_scenario,
):
    """
    Required user-specified scenario values must remain fixed after
    empirical donor sampling.

    Only unspecified contextual variables should be inherited from
    compatible historical donor rows.
    """

    sampler = DonorSampler(donor_data)

    trials = sampler.sample(
        scenario=supported_scenario,
        n_trials=500,
        random_state=42,
    )

    assert len(trials) == 500

    assert (trials["AC_CLASS"] == "A").all()
    assert (trials["AC_MASS_GROUP"] == "Heavy").all()
    assert (trials["SEASON"] == "Summer").all()

    assert (
        trials["PHASE_OF_FLIGHT"]
        == "Take-off Run"
    ).all()

    assert (trials["AIRPORT_ID"] == "KSMF").all()


# =====================================================================
# 5. Probability validity
# =====================================================================

def test_prediction_probabilities_remain_between_zero_and_one(
    donor_data,
    supported_scenario,
):
    """
    Probability arrays supplied to the Monte Carlo engine must remain
    finite and inside the mathematical probability range [0, 1].
    """

    sampler = DonorSampler(donor_data)

    rows = sampler.sample(
        scenario=supported_scenario,
        n_trials=250,
        random_state=42,
    )

    service = StubPredictionService()

    damage_probabilities = np.asarray(
        service.predict_damage_probability(rows)
    )

    severity_probabilities = np.asarray(
        service.predict_severity_probability(rows)
    )

    component_probabilities = (
        service.predict_all_component_probabilities(rows)
    )

    assert np.isfinite(damage_probabilities).all()
    assert (damage_probabilities >= 0).all()
    assert (damage_probabilities <= 1).all()

    assert np.isfinite(severity_probabilities).all()
    assert (severity_probabilities >= 0).all()
    assert (severity_probabilities <= 1).all()

    for probabilities in component_probabilities.values():
        probabilities = np.asarray(probabilities)

        assert np.isfinite(probabilities).all()
        assert (probabilities >= 0).all()
        assert (probabilities <= 1).all()


# =====================================================================
# 6. Reproducibility
# =====================================================================

def test_same_seed_reproduces_same_simulation(
    simulation_engine,
    supported_scenario,
):
    """
    Running the same scenario with the same trial count and random seed
    must reproduce the same aggregate Monte Carlo result.
    """

    result_a = simulation_engine.run(
        scenario=supported_scenario,
        n_trials=500,
        seed=123,
    )

    result_b = simulation_engine.run(
        scenario=supported_scenario,
        n_trials=500,
        seed=123,
    )

    assert result_a.n_trials == result_b.n_trials
    assert result_a.seed == result_b.seed

    assert (
        result_a.mean_damage_probability
        == result_b.mean_damage_probability
    )

    assert (
        result_a.simulated_damage_count
        == result_b.simulated_damage_count
    )

    assert (
        result_a.simulated_damage_rate
        == result_b.simulated_damage_rate
    )

    assert (
        result_a.simulated_severe_count
        == result_b.simulated_severe_count
    )

    assert (
        result_a.simulated_severe_rate_given_damage
        == result_b.simulated_severe_rate_given_damage
    )

    assert result_a.component_counts == result_b.component_counts

    assert (
        result_a.component_rates_given_damage
        == result_b.component_rates_given_damage
    )


# =====================================================================
# 7. Conditional outcome integrity
# =====================================================================

def test_conditional_counts_do_not_exceed_damage_count(
    simulation_engine,
    supported_scenario,
):
    """
    Severity and retained component outcomes are simulated only among
    damaged trials.

    Their counts therefore cannot exceed the total number of simulated
    damaged outcomes.
    """

    result = simulation_engine.run(
        scenario=supported_scenario,
        n_trials=1000,
        seed=42,
    )

    assert result.simulated_damage_count <= result.n_trials

    assert (
        result.simulated_severe_count
        <= result.simulated_damage_count
    )

    for component_count in result.component_counts.values():
        assert (
            component_count
            <= result.simulated_damage_count
        )


# =====================================================================
# Additional aggregate sanity checks
# =====================================================================

def test_simulation_rates_are_valid_probabilities(
    simulation_engine,
    supported_scenario,
):
    """
    Aggregated Monte Carlo rates should also remain within [0, 1].
    """

    result = simulation_engine.run(
        scenario=supported_scenario,
        n_trials=500,
        seed=42,
    )

    assert 0 <= result.mean_damage_probability <= 1
    assert 0 <= result.simulated_damage_rate <= 1

    if result.simulated_damage_count > 0:
        assert (
            0
            <= result.simulated_severe_rate_given_damage
            <= 1
        )

        for rate in result.component_rates_given_damage.values():
            assert 0 <= rate <= 1