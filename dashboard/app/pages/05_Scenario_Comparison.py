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


# =====================================================================
# Page configuration
# =====================================================================

st.title("Scenario Comparison")

st.markdown(
    """
    Compare two historically supported wildlife-strike scenarios under
    the same Monte Carlo settings.

    The strongest interpretation is a **controlled comparison** in which
    Scenario A and Scenario B differ in only one scenario characteristic.
    Percentage-point differences are therefore emphasized over relative
    percentage changes.
    """
)


# =====================================================================
# Helpers
# =====================================================================

def sorted_values(data, column):
    """Return sorted non-null unique string values."""
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
    """Filter using the same normalized string representation as the UI."""
    if column not in data.columns or value is None:
        return data.iloc[0:0].copy()

    normalized = (
        data[column]
        .astype("string")
        .str.strip()
    )

    return data.loc[
        normalized == str(value).strip()
    ].copy()


def require_options(options, message):
    """Stop cleanly if a cascading selection has no valid options."""
    if options:
        return

    st.warning(message)
    st.stop()


def relative_change(a, b):
    """
    Return relative change from A to B.

    None is returned when Scenario A is zero because relative change
    would be undefined or misleading.
    """
    if a == 0:
        return None

    return (b - a) / a


def pp_difference(a, b):
    """Difference B - A in percentage points."""
    return (b - a) * 100.0


def format_relative(value):
    if value is None:
        return "Undefined"
    return f"{value:+.1%}"


def component_label(component):
    return (
        component
        .replace("_damage", "")
        .replace("_", " ")
        .title()
    )


def build_required_scenario(prefix, title, support_data):
    """
    Build one supported required scenario using cascading selections.

    Optional scenario variables are intentionally left as None in this
    first functional comparison page so that they continue to be filled
    by empirical historical donor sampling.
    """
    st.markdown(f"### {title}")

    geography_mode = st.radio(
        "Scenario geography",
        options=["Airport", "FAA Region"],
        horizontal=True,
        key=f"{prefix}_geography_mode",
    )

    working = support_data.copy()

    airport_id = None
    faa_region = None

    if geography_mode == "Airport":

        options = sorted_values(
            support_data,
            "AIRPORT_ID",
        )

        require_options(
            options,
            f"No airports are available for {title}.",
        )

        airport_id = st.selectbox(
            "Airport ID",
            options,
            key=f"{prefix}_airport_id",
        )

        working = filter_equals(
            working,
            "AIRPORT_ID",
            airport_id,
        )

    else:

        options = sorted_values(
            support_data,
            "FAAREGION",
        )

        require_options(
            options,
            f"No FAA regions are available for {title}.",
        )

        faa_region = st.selectbox(
            "FAA Region",
            options,
            key=f"{prefix}_faa_region",
        )

        working = filter_equals(
            working,
            "FAAREGION",
            faa_region,
        )

    ac_class_options = sorted_values(
        working,
        "AC_CLASS",
    )

    require_options(
        ac_class_options,
        f"No aircraft classes are supported for {title}.",
    )

    ac_class = st.selectbox(
        "Aircraft Class",
        ac_class_options,
        key=f"{prefix}_ac_class",
    )

    working = filter_equals(
        working,
        "AC_CLASS",
        ac_class,
    )

    mass_options = sorted_values(
        working,
        "AC_MASS_GROUP",
    )

    require_options(
        mass_options,
        f"No aircraft mass groups are supported for {title}.",
    )

    ac_mass_group = st.selectbox(
        "Aircraft Mass Group",
        mass_options,
        key=f"{prefix}_mass_group",
    )

    working = filter_equals(
        working,
        "AC_MASS_GROUP",
        ac_mass_group,
    )

    season_options = sorted_values(
        working,
        "SEASON",
    )

    require_options(
        season_options,
        f"No seasons are supported for {title}.",
    )

    season = st.selectbox(
        "Season",
        season_options,
        key=f"{prefix}_season",
    )

    working = filter_equals(
        working,
        "SEASON",
        season,
    )

    phase_options = sorted_values(
        working,
        "PHASE_OF_FLIGHT",
    )

    require_options(
        phase_options,
        f"No phases of flight are supported for {title}.",
    )

    phase_of_flight = st.selectbox(
        "Phase of Flight",
        phase_options,
        key=f"{prefix}_phase",
    )

    working = filter_equals(
        working,
        "PHASE_OF_FLIGHT",
        phase_of_flight,
    )

    st.caption(
        f"Historical support for required scenario: "
        f"{len(working):,} records"
    )

    scenario = Scenario(
        ac_class=ac_class,
        ac_mass_group=ac_mass_group,
        season=season,
        phase_of_flight=phase_of_flight,
        airport_id=airport_id,
        faa_region=faa_region,

        # Optional context remains empirically sampled.
        wildlife_type=None,
        size=None,
        num_struck=None,
        type_eng=None,
        num_engs=None,
        warned=None,
        height=None,
        speed=None,
        time_of_day=None,
        sky=None,
        precipitation=None,
        state=None,
    )

    return scenario


# =====================================================================
# Load simulation artifacts
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


# =====================================================================
# Cache simulation infrastructure
# =====================================================================

@st.cache_resource
def get_simulation_engine():
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
# Scenario definitions
# =====================================================================

st.subheader("1. Define Scenarios")

st.caption(
    "For the clearest what-if interpretation, keep most selections the "
    "same and change only the factor you want to investigate."
)

col_a, col_b = st.columns(2)

with col_a:
    scenario_a = build_required_scenario(
        "scenario_a",
        "Scenario A",
        support_data,
    )

with col_b:
    scenario_b = build_required_scenario(
        "scenario_b",
        "Scenario B",
        support_data,
    )


# =====================================================================
# Validate support
# =====================================================================

support_evaluator = SupportEvaluator(
    support_data
)

try:
    scenario_a.validate()
    scenario_b.validate()

except ValueError as exc:
    st.error(str(exc))
    st.stop()


support_a = support_evaluator.evaluate(
    scenario_a
)

support_b = support_evaluator.evaluate(
    scenario_b
)


if not support_a.supported:
    st.error(
        "Scenario A has no exact historical support and cannot be "
        "compared."
    )
    st.stop()

if not support_b.supported:
    st.error(
        "Scenario B has no exact historical support and cannot be "
        "compared."
    )
    st.stop()


# =====================================================================
# Comparison setup
# =====================================================================

st.subheader("2. Comparison Settings")

col1, col2 = st.columns(2)

with col1:
    n_trials = st.number_input(
        "Monte Carlo Trials",
        min_value=100,
        max_value=100_000,
        value=10_000,
        step=1_000,
        key="comparison_trials",
    )

with col2:
    seed = st.number_input(
        "Shared Random Seed",
        min_value=0,
        value=42,
        step=1,
        key="comparison_seed",
    )


st.caption(
    "Both scenarios use the same number of trials and random seed. "
    "This improves reproducibility and keeps the comparison settings "
    "consistent."
)


# =====================================================================
# Scenario difference summary
# =====================================================================

scenario_a_dict = scenario_a.to_dict()
scenario_b_dict = scenario_b.to_dict()

changed_fields = []

for field in scenario_a_dict:
    if scenario_a_dict.get(field) != scenario_b_dict.get(field):
        changed_fields.append(field)


if len(changed_fields) == 0:
    st.info(
        "Scenario A and Scenario B currently have the same required "
        "settings. Change at least one field to create a meaningful "
        "comparison."
    )

elif len(changed_fields) == 1:
    field = changed_fields[0]

    st.success(
        "Controlled one-variable comparison: "
        f"{field.replace('_', ' ').title()} changes from "
        f"{scenario_a_dict.get(field)} to "
        f"{scenario_b_dict.get(field)}."
    )

else:
    st.warning(
        f"The scenarios differ in {len(changed_fields)} fields: "
        + ", ".join(
            field.replace("_", " ").title()
            for field in changed_fields
        )
        + ". Differences in the results cannot be attributed to one "
          "factor alone."
    )


# =====================================================================
# Run comparison
# =====================================================================

st.subheader("3. Run Comparison")

run_clicked = st.button(
    "Run Scenario Comparison",
    type="primary",
)


if run_clicked:

    try:

        with st.spinner(
            f"Running two {int(n_trials):,}-trial simulations..."
        ):

            engine = get_simulation_engine()

            result_a = engine.run(
                scenario=scenario_a,
                n_trials=int(n_trials),
                seed=int(seed),
            )

            result_b = engine.run(
                scenario=scenario_b,
                n_trials=int(n_trials),
                seed=int(seed),
            )

    except Exception as exc:

        st.error(
            "The scenario comparison could not be completed."
        )

        st.exception(exc)
        st.stop()


    # =================================================================
    # Main damage comparison
    # =================================================================

    st.divider()
    st.subheader("Comparison Results")

    st.markdown("### Aircraft Damage Probability")

    a_damage = result_a.mean_damage_probability
    b_damage = result_b.mean_damage_probability

    damage_pp = pp_difference(
        a_damage,
        b_damage,
    )

    damage_relative = relative_change(
        a_damage,
        b_damage,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Scenario A",
            f"{a_damage:.2%}",
        )

    with col2:
        st.metric(
            "Scenario B",
            f"{b_damage:.2%}",
        )

    with col3:
        st.metric(
            "Difference (B − A)",
            f"{damage_pp:+.2f} pp",
            delta=format_relative(
                damage_relative
            ),
            delta_color="normal",
        )


    damage_chart = pd.DataFrame(
        {
            "Scenario": [
                "Scenario A",
                "Scenario B",
            ],
            "Mean Modeled Damage Probability": [
                a_damage * 100,
                b_damage * 100,
            ],
        }
    ).set_index("Scenario")

    st.bar_chart(
        damage_chart,
        use_container_width=True,
    )

    st.caption(
        "The percentage-point difference is the primary comparison. "
        "The smaller delta annotation shows relative change from "
        "Scenario A to Scenario B."
    )


    # =================================================================
    # Severity comparison
    # =================================================================

    st.markdown("### Severity Probability Conditional on Damage")

    a_severity = (
        result_a.severity_probability_mean_damaged
    )

    b_severity = (
        result_b.severity_probability_mean_damaged
    )

    if a_severity is not None and b_severity is not None:

        severity_pp = pp_difference(
            a_severity,
            b_severity,
        )

        severity_relative = relative_change(
            a_severity,
            b_severity,
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Scenario A",
                f"{a_severity:.2%}",
            )

        with col2:
            st.metric(
                "Scenario B",
                f"{b_severity:.2%}",
            )

        with col3:
            st.metric(
                "Difference (B − A)",
                f"{severity_pp:+.2f} pp",
                delta=format_relative(
                    severity_relative
                ),
            )

        severity_chart = pd.DataFrame(
            {
                "Scenario": [
                    "Scenario A",
                    "Scenario B",
                ],
                "Mean Severity Probability": [
                    a_severity * 100,
                    b_severity * 100,
                ],
            }
        ).set_index("Scenario")

        st.bar_chart(
            severity_chart,
            use_container_width=True,
        )

        st.caption(
            "Severity remains conditional on a simulated strike already "
            "resulting in aircraft damage."
        )

    else:

        st.info(
            "A severity comparison is unavailable because at least one "
            "scenario produced no damaged trials."
        )


    # =================================================================
    # Component probability comparison
    # =================================================================

    st.markdown(
        "### Component Probabilities Conditional on Damage"
    )

    components = sorted(
        set(
            result_a.component_probability_means_damaged.keys()
        )
        | set(
            result_b.component_probability_means_damaged.keys()
        )
    )

    component_rows = []

    for component in components:

        a_value = (
            result_a
            .component_probability_means_damaged
            .get(component)
        )

        b_value = (
            result_b
            .component_probability_means_damaged
            .get(component)
        )

        if a_value is None or b_value is None:
            continue

        component_rows.append(
            {
                "Component": component_label(
                    component
                ),
                "Scenario A": a_value,
                "Scenario B": b_value,
                "Difference (pp)": pp_difference(
                    a_value,
                    b_value,
                ),
                "Relative Change": relative_change(
                    a_value,
                    b_value,
                ),
            }
        )


    if component_rows:

        component_df = pd.DataFrame(
            component_rows
        )

        component_df = component_df.sort_values(
            "Difference (pp)",
            key=lambda series: series.abs(),
            ascending=False,
        )

        display_df = component_df.copy()

        display_df["Scenario A"] = (
            display_df["Scenario A"]
            .map(lambda value: f"{value:.2%}")
        )

        display_df["Scenario B"] = (
            display_df["Scenario B"]
            .map(lambda value: f"{value:.2%}")
        )

        display_df["Difference (pp)"] = (
            display_df["Difference (pp)"]
            .map(lambda value: f"{value:+.2f}")
        )

        display_df["Relative Change"] = (
            display_df["Relative Change"]
            .map(format_relative)
        )

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
        )


        component_chart = (
            component_df[
                [
                    "Component",
                    "Scenario A",
                    "Scenario B",
                ]
            ]
            .set_index("Component")
            .mul(100)
        )

        st.bar_chart(
            component_chart,
            use_container_width=True,
        )

        st.caption(
            "Component probabilities are conditional on aircraft "
            "damage. Components are modeled separately and are not "
            "mutually exclusive."
        )

    else:

        st.info(
            "Component probability comparison is unavailable because "
            "at least one scenario produced no damaged trials."
        )


    # =================================================================
    # Realized Monte Carlo outcomes
    # =================================================================

    with st.expander(
        "Realized Monte Carlo outcomes",
        expanded=False,
    ):

        realized_rows = [
            {
                "Metric": "Simulated damage rate",
                "Scenario A": result_a.simulated_damage_rate,
                "Scenario B": result_b.simulated_damage_rate,
            },
            {
                "Metric": "Severe rate given damage",
                "Scenario A": (
                    result_a.simulated_severe_rate_given_damage
                ),
                "Scenario B": (
                    result_b.simulated_severe_rate_given_damage
                ),
            },
        ]

        realized_df = pd.DataFrame(
            realized_rows
        )

        realized_df["Difference (pp)"] = (
            (
                realized_df["Scenario B"]
                - realized_df["Scenario A"]
            )
            * 100
        )

        display_realized = realized_df.copy()

        for column in [
            "Scenario A",
            "Scenario B",
        ]:
            display_realized[column] = (
                display_realized[column]
                .map(
                    lambda value: (
                        f"{value:.2%}"
                        if pd.notna(value)
                        else "Unavailable"
                    )
                )
            )

        display_realized["Difference (pp)"] = (
            display_realized["Difference (pp)"]
            .map(
                lambda value: (
                    f"{value:+.2f}"
                    if pd.notna(value)
                    else "Unavailable"
                )
            )
        )

        st.dataframe(
            display_realized,
            use_container_width=True,
            hide_index=True,
        )

        st.caption(
            "These are realized Monte Carlo rates and therefore contain "
            "simulation noise. The modeled probability comparisons "
            "above are the primary comparison quantities."
        )


    # =================================================================
    # Support and scenario details
    # =================================================================

    st.markdown("### Historical Support")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Scenario A Support",
            f"{result_a.support_count:,} records",
        )

    with col2:
        st.metric(
            "Scenario B Support",
            f"{result_b.support_count:,} records",
        )


    st.caption(
        "Support counts describe how many historical donor records match "
        "the required scenario context. More Monte Carlo trials reduce "
        "simulation noise but do not create new historical support."
    )


    with st.expander(
        "Scenario definitions and run details",
        expanded=False,
    ):

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Scenario A")
            st.json(
                scenario_a.to_dict()
            )

            st.write(
                f"Historical support: "
                f"{result_a.support_count:,}"
            )

        with col2:
            st.markdown("#### Scenario B")
            st.json(
                scenario_b.to_dict()
            )

            st.write(
                f"Historical support: "
                f"{result_b.support_count:,}"
            )

        st.write(
            f"Trials per scenario: {result_a.n_trials:,}"
        )

        st.write(
            f"Shared random seed: {result_a.seed}"
        )
