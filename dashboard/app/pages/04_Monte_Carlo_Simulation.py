import pandas as pd
import streamlit as st

from src.data.loaders import (
    load_simulation_donors,
    load_scenario_support,
)
from src.simulation.scenario import Scenario
from src.simulation.support import SupportEvaluator
from src.simulation.donor_sampling import DonorSampler
from src.simulation.prediction import PredictionService
from src.simulation.engine import SimulationEngine

from src.utils.labels import (
    build_airport_labels,
    format_aircraft_class,
)


# =====================================================================
# Page configuration
# =====================================================================

st.title("Monte Carlo What-If Simulation")

st.markdown(
    """
    Construct a wildlife-strike scenario and estimate the probability
    of aircraft damage using the project's trained models and empirical
    Monte Carlo simulation.

    Required scenario characteristics are fixed by the user. Optional
    characteristics may either be specified manually or left to
    historical sampling from compatible strike records.
    """
)


# =====================================================================
# Helpers
# =====================================================================

def sorted_values(data, column):
    """
    Return sorted non-null unique values from a dashboard artifact.
    """
    if column not in data.columns:
        return []

    values = (
        data[column]
        .dropna()
        .astype(str)
        .str.strip()
    )

    values = values[values != ""]

    return sorted(values.unique().tolist())


def filter_equals(data, column, value):
    """
    Filter a dashboard artifact using normalized string comparison.

    This mirrors the string cleanup used to populate the selectboxes so
    that displayed choices and downstream filtering stay consistent.
    """
    if column not in data.columns or value is None:
        return data.iloc[0:0].copy()

    normalized = (
        data[column]
        .astype("string")
        .str.strip()
    )

    return data.loc[normalized == str(value).strip()].copy()


def require_options(options, message):
    """
    Stop the page cleanly if an upstream selection leaves no valid
    downstream choices.
    """
    if options:
        return

    st.warning(message)
    st.stop()


def optional_selectbox(label, values, key):
    """
    Select an optional categorical scenario value.

    'Historical sampling' is converted to None so that the donor
    sampler retains the empirically sampled historical value.
    """
    options = ["Historical sampling"] + values

    selected = st.selectbox(
        label,
        options=options,
        key=key,
    )

    if selected == "Historical sampling":
        return None

    return selected


# =====================================================================
# Load lightweight simulation artifacts
# =====================================================================

try:
    donor_data = load_simulation_donors()
    support_data = load_scenario_support()

except Exception as exc:
    st.error(
        "Simulation reference data could not be loaded. "
        f"Details: {exc}"
    )
    st.stop()

airport_labels = build_airport_labels(donor_data)

# =====================================================================
# Cache model / simulation infrastructure
# =====================================================================

@st.cache_resource
def get_simulation_engine():
    """
    Construct and cache the reusable simulation service.
    """

    prediction_service = PredictionService()

    support_evaluator = SupportEvaluator(
        support_data
    )

    donor_sampler = DonorSampler(
        donor_data
    )

    return SimulationEngine(
        support_evaluator=support_evaluator,
        donor_sampler=donor_sampler,
        prediction_service=prediction_service,
    )


# =====================================================================
# Scenario definition
# =====================================================================

st.subheader("1. Define Scenario")

st.caption(
    "Required fields determine the historical donor population used "
    "for the simulation."
)


# ---------------------------------------------------------------------
# Cascading required context
# ---------------------------------------------------------------------

st.markdown("#### Geography")

geography_mode = st.radio(
    "Scenario geography",
    options=[
        "Airport",
        "FAA Region",
    ],
    horizontal=True,
)

airport_id = None
faa_region = None

# The support artifact is the authoritative source for determining
# which required scenario combinations are historically supported.
# Each downstream selectbox is therefore restricted by the selections
# already made above it.
required_support = support_data.copy()

if geography_mode == "Airport":

    geography_options = sorted_values(
        support_data,
        "AIRPORT_ID",
    )

    require_options(
        geography_options,
        "No airports are available in the historical support artifact.",
    )

    airport_id = st.selectbox(
        "Airport",
        geography_options,
        format_func=lambda airport_id: airport_labels.get(
            airport_id,
            airport_id,
        ),
        key="required_airport_id",
    )

    required_support = filter_equals(
        required_support,
        "AIRPORT_ID",
        airport_id,
    )

else:

    geography_options = sorted_values(
        support_data,
        "FAAREGION",
    )

    require_options(
        geography_options,
        "No FAA regions are available in the historical support artifact.",
    )

    faa_region = st.selectbox(
        "FAA Region",
        geography_options,
        key="required_faa_region",
    )

    required_support = filter_equals(
        required_support,
        "FAAREGION",
        faa_region,
    )


st.markdown("#### Required Flight Context")

ac_class_options = sorted_values(
    required_support,
    "AC_CLASS",
)

require_options(
    ac_class_options,
    "The selected geography has no supported aircraft classes.",
)

ac_class = st.selectbox(
    "Aircraft Class",
    ac_class_options,
    format_func=format_aircraft_class,
    key="required_ac_class",
)

required_support = filter_equals(
    required_support,
    "AC_CLASS",
    ac_class,
)


ac_mass_group_options = sorted_values(
    required_support,
    "AC_MASS_GROUP",
)

require_options(
    ac_mass_group_options,
    "No aircraft mass groups are supported for the current selections.",
)

ac_mass_group = st.selectbox(
    "Aircraft Mass Group",
    ac_mass_group_options,
    key="required_ac_mass_group",
)

required_support = filter_equals(
    required_support,
    "AC_MASS_GROUP",
    ac_mass_group,
)


season_options = sorted_values(
    required_support,
    "SEASON",
)

require_options(
    season_options,
    "No seasons are supported for the current selections.",
)

season = st.selectbox(
    "Season",
    season_options,
    key="required_season",
)

required_support = filter_equals(
    required_support,
    "SEASON",
    season,
)


phase_options = sorted_values(
    required_support,
    "PHASE_OF_FLIGHT",
)

require_options(
    phase_options,
    "No phases of flight are supported for the current selections.",
)

phase_of_flight = st.selectbox(
    "Phase of Flight",
    phase_options,
    key="required_phase_of_flight",
)

required_support = filter_equals(
    required_support,
    "PHASE_OF_FLIGHT",
    phase_of_flight,
)


st.caption(
    f"Historical records matching the current required scenario: "
    f"{len(required_support):,}"
)

# =====================================================================
# Optional context
# =====================================================================

with st.expander(
    "Optional scenario context",
    expanded=False,
):

    st.caption(
        "Leave an optional variable as Historical sampling to preserve "
        "the value observed in each sampled historical donor row."
    )

    col1, col2 = st.columns(2)

    with col1:

        wildlife_type = optional_selectbox(
            "Wildlife Type",
            sorted_values(
                donor_data,
                "WILDLIFE_TYPE",
            ),
            key="wildlife_type",
        )

        size = optional_selectbox(
            "Wildlife Size",
            sorted_values(
                donor_data,
                "SIZE",
            ),
            key="wildlife_size",
        )

        type_eng = optional_selectbox(
            "Engine Type",
            sorted_values(
                donor_data,
                "TYPE_ENG",
            ),
            key="engine_type",
        )

        warned = optional_selectbox(
            "Wildlife Warning",
            sorted_values(
                donor_data,
                "WARNED",
            ),
            key="warned",
        )

        time_of_day = optional_selectbox(
            "Time of Day",
            sorted_values(
                donor_data,
                "TIME_OF_DAY",
            ),
            key="time_of_day",
        )

        sky = optional_selectbox(
            "Sky Condition",
            sorted_values(
                donor_data,
                "SKY",
            ),
            key="sky",
        )

    with col2:

        precipitation = optional_selectbox(
            "Precipitation",
            sorted_values(
                donor_data,
                "PRECIPITATION",
            ),
            key="precipitation",
        )

        state = optional_selectbox(
            "State",
            sorted_values(
                donor_data,
                "STATE",
            ),
            key="state",
        )

        specify_num_struck = st.checkbox(
            "Specify number struck"
        )

        num_struck = None

        if specify_num_struck:
            num_struck = st.number_input(
                "Number Struck",
                min_value=0,
                step=1,
                value=1,
            )

        specify_num_engs = st.checkbox(
            "Specify number of engines"
        )

        num_engs = None

        if specify_num_engs:
            num_engs = st.number_input(
                "Number of Engines",
                min_value=0.0,
                step=1.0,
                value=2.0,
            )

        specify_height = st.checkbox(
            "Specify height"
        )

        height = None

        if specify_height:
            height = st.number_input(
                "Height",
                min_value=0.0,
                step=100.0,
                value=1000.0,
            )

        specify_speed = st.checkbox(
            "Specify speed"
        )

        speed = None

        if specify_speed:
            speed = st.number_input(
                "Speed",
                min_value=0.0,
                step=10.0,
                value=100.0,
            )


# =====================================================================
# Simulation configuration
# =====================================================================

st.subheader("2. Simulation Settings")

col1, col2 = st.columns(2)

with col1:
    n_trials = st.number_input(
        "Monte Carlo Trials",
        min_value=100,
        max_value=100_000,
        value=10_000,
        step=1_000,
    )

with col2:
    seed = st.number_input(
        "Random Seed",
        min_value=0,
        value=42,
        step=1,
    )


st.caption(
    "10,000 trials is the default operational setting used for the "
    "dashboard. The random seed allows the simulation to be reproduced."
)


# =====================================================================
# Construct scenario
# =====================================================================

scenario = Scenario(
    ac_class=ac_class,
    ac_mass_group=ac_mass_group,
    season=season,
    phase_of_flight=phase_of_flight,
    airport_id=airport_id,
    faa_region=faa_region,
    wildlife_type=wildlife_type,
    size=size,
    num_struck=num_struck,
    type_eng=type_eng,
    num_engs=num_engs,
    warned=warned,
    height=height,
    speed=speed,
    time_of_day=time_of_day,
    sky=sky,
    precipitation=precipitation,
    state=state,
)


# =====================================================================
# Historical support
# =====================================================================

st.subheader("3. Historical Support")

try:
    scenario.validate()

except ValueError as exc:
    st.error(str(exc))
    st.stop()


support_evaluator = SupportEvaluator(
    support_data
)

support = support_evaluator.evaluate(
    scenario
)


if support.supported:

    st.success(
        f"Scenario supported by "
        f"{support.exact_count:,} compatible historical records."
    )

    st.caption(
        f"Geographic support level: "
        f"{support.geography_level}"
    )

else:

    st.error(
        "This required scenario combination has no exact historical "
        "support in the 1990–2021 simulation reference population."
    )

    st.info(
        "Change one or more required scenario characteristics before "
        "running the simulation. The dashboard does not generate a "
        "numerical estimate for completely unsupported required "
        "scenario combinations."
    )

    st.stop()


# =====================================================================
# Run simulation
# =====================================================================

st.subheader("4. Run Simulation")

run_clicked = st.button(
    "Run Monte Carlo Simulation",
    type="primary",
)


if run_clicked:

    try:

        with st.spinner(
            f"Running {int(n_trials):,} Monte Carlo trials..."
        ):

            engine = get_simulation_engine()

            result = engine.run(
                scenario=scenario,
                n_trials=int(n_trials),
                seed=int(seed),
            )

    except Exception as exc:

        st.error(
            "The simulation could not be completed."
        )

        st.exception(exc)

        st.stop()


    # =================================================================
    # Main damage results
    # =================================================================

    st.divider()

    st.subheader("Simulation Results")

    st.markdown("### Aircraft Damage")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Mean Modeled Damage Probability",
            f"{result.mean_damage_probability:.2%}",
        )

    with col2:
        st.metric(
            "Simulated Damage Rate",
            f"{result.simulated_damage_rate:.2%}",
        )

    with col3:
        st.metric(
            "Damaged Trials",
            (
                f"{result.simulated_damage_count:,} "
                f"/ {result.n_trials:,}"
            ),
        )


    st.caption(
        "The mean modeled probability summarizes the probabilities "
        "assigned to the simulated scenario rows. The simulated damage "
        "rate is the realized proportion of Bernoulli damage outcomes "
        "across the Monte Carlo trials."
    )


    # =================================================================
    # Severity results
    # =================================================================

    st.markdown("### Severity Conditional on Damage")

    if result.simulated_damage_count > 0:

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Mean Severity Probability",
                (
                    f"{result.severity_probability_mean_damaged:.2%}"
                ),
            )

        with col2:
            st.metric(
                "Simulated Severe Rate",
                (
                    f"{result.simulated_severe_rate_given_damage:.2%}"
                ),
            )

        with col3:
            st.metric(
                "Severe Outcomes",
                (
                    f"{result.simulated_severe_count:,} "
                    f"/ {result.simulated_damage_count:,} damaged"
                ),
            )

        st.caption(
            "Severity is conditional on a simulated strike already "
            "resulting in aircraft damage. It should not be interpreted "
            "as an unconditional probability across all strike trials."
        )

    else:

        st.info(
            "No damaged outcomes occurred in this simulation run, so "
            "conditional severity and component outcomes are unavailable."
        )


    # =================================================================
    # Component results
    # =================================================================

    if (
        result.simulated_damage_count > 0
        and result.component_counts
    ):

        st.markdown(
            "### Component Damage Conditional on Damage"
        )

        component_rows = []

        for component, count in result.component_counts.items():

            rate = result.component_rates_given_damage.get(
                component,
                0.0,
            )

            component_rows.append(
                {
                    "Component": (
                        component
                        .replace("_damage", "")
                        .replace("_", " ")
                        .title()
                    ),
                    "Simulated Count": count,
                    "Rate Given Damage": rate,
                }
            )

        component_df = pd.DataFrame(
            component_rows
        )

        component_df = component_df.sort_values(
            "Rate Given Damage",
            ascending=False,
        )

        display_component_df = (
            component_df.copy()
        )

        display_component_df[
            "Rate Given Damage"
        ] = (
            display_component_df[
                "Rate Given Damage"
            ]
            .map(lambda value: f"{value:.2%}")
        )

        st.dataframe(
            display_component_df,
            use_container_width=True,
            hide_index=True,
        )

        chart_data = (
            component_df[
                [
                    "Component",
                    "Rate Given Damage",
                ]
            ]
            .set_index("Component")
            .mul(100)
        )

        st.bar_chart(
            chart_data,
            use_container_width=True,
        )

        st.caption(
            "Component probabilities and outcomes are conditional on "
            "aircraft damage. The retained component systems are not "
            "mutually exclusive, so more than one component may be "
            "affected within the same simulated damaged strike."
        )


    # =================================================================
    # Run information
    # =================================================================

    with st.expander(
        "Simulation details",
        expanded=False,
    ):

        st.write(
            f"Trials: {result.n_trials:,}"
        )

        st.write(
            f"Random seed: {result.seed}"
        )

        st.write(
            f"Historical support: "
            f"{result.support_count:,} records"
        )

        st.write(
            f"Geography level: "
            f"{result.geography_level}"
        )

        st.markdown(
            "**Scenario supplied to the simulation:**"
        )

        st.json(
            scenario.to_dict()
        )