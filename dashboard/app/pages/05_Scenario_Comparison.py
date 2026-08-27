from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard.components.charts import apply_chart_layout
from dashboard.components.layout import page_header, section_divider, section_header
from dashboard.components.metrics import metric_row

from src.data.loaders import load_scenario_support, load_simulation_donors
from src.simulation.donor_sampling import DonorSampler
from src.simulation.engine import SimulationEngine
from src.simulation.prediction import PredictionService
from src.simulation.scenario import Scenario
from src.simulation.support import SupportEvaluator
from src.utils.labels import (
    build_airport_labels,
    format_aircraft_class,
    format_engine_type,
    format_state,
)


PLOTLY_CONFIG = {"displaylogo": False, "responsive": True}


# =====================================================================
# Page header
# =====================================================================

page_header(
    "Scenario Comparison",
    (
        "Compare two historically supported wildlife-strike scenarios under "
        "the same Monte Carlo settings. For the clearest interpretation, "
        "change one comparison variable at a time."
    ),
)

st.info(
    "Controlled comparison: shared scenario context is held constant while "
    "one selected factor changes between Scenario A and Scenario B. Optional "
    "characteristics that are not being compared remain historically sampled."
)


# =====================================================================
# Helpers
# =====================================================================

def sorted_values(data, column):
    """Return sorted non-null unique string values."""
    if column not in data.columns:
        return []

    values = data[column].dropna().astype(str).str.strip()
    values = values[values != ""]
    return sorted(values.unique().tolist())


def sorted_numeric_values(data, column):
    """Return sorted unique numeric values, preserving integers when possible."""
    if column not in data.columns:
        return []

    values = pd.to_numeric(data[column], errors="coerce").dropna()
    if values.empty:
        return []

    unique_values = sorted(values.unique().tolist())
    if all(float(value).is_integer() for value in unique_values):
        return [int(value) for value in unique_values]
    return unique_values


def filter_equals(data, column, value):
    """Filter using the same normalized representation as the UI."""
    if column not in data.columns or value is None:
        return data.iloc[0:0].copy()

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        numeric = pd.to_numeric(data[column], errors="coerce")
        return data.loc[numeric.eq(float(value))].copy()

    normalized = data[column].astype("string").str.strip()
    return data.loc[normalized.eq(str(value).strip())].copy()


def require_options(options, message):
    """Stop cleanly if a cascading selection has no valid options."""
    if options:
        return
    st.warning(message)
    st.stop()


def relative_change(a, b):
    """Return relative change from A to B, or None when A is zero."""
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
    return component.replace("_damage", "").replace("_", " ").title()


def format_warned(value):
    """Human-readable display for wildlife-warning codes."""
    normalized = str(value).strip().upper()
    if normalized in {"Y", "YES", "TRUE", "1"}:
        return "Yes"
    if normalized in {"N", "NO", "FALSE", "0"}:
        return "No"
    return str(value)


def format_comparison_value(field_name, value):
    """Human-readable display for comparison values."""
    if field_name == "Engine type":
        return format_engine_type(value)
    if field_name == "Wildlife warning":
        return format_warned(value)
    return str(value)


def count_full_specified_support(data, scenario):
    """
    Count donor rows matching every scenario field explicitly specified.

    Required fields are always included. Optional fields are included when
    they are not None. This is an interpretability diagnostic only; required
    support remains the authoritative simulation gate.
    """
    field_map = {
        "airport_id": "AIRPORT_ID",
        "faa_region": "FAAREGION",
        "ac_class": "AC_CLASS",
        "ac_mass_group": "AC_MASS_GROUP",
        "season": "SEASON",
        "phase_of_flight": "PHASE_OF_FLIGHT",
        "wildlife_type": "WILDLIFE_TYPE",
        "size": "SIZE",
        "num_struck": "NUM_STRUCK",
        "type_eng": "TYPE_ENG",
        "num_engs": "NUM_ENGS",
        "warned": "WARNED",
        "height": "HEIGHT",
        "speed": "SPEED",
        "time_of_day": "TIME_OF_DAY",
        "sky": "SKY",
        "precipitation": "PRECIPITATION",
        "state": "STATE",
    }
    required_fields = {
        "airport_id",
        "faa_region",
        "ac_class",
        "ac_mass_group",
        "season",
        "phase_of_flight",
    }

    scenario_values = scenario.to_dict()
    working = data.copy()
    specified_optional_fields = []
    unavailable_fields = []

    for scenario_field, data_column in field_map.items():
        value = scenario_values.get(scenario_field)
        if value is None:
            continue
        if data_column not in working.columns:
            unavailable_fields.append(scenario_field)
            continue
        if scenario_field not in required_fields:
            specified_optional_fields.append(scenario_field)
        working = filter_equals(working, data_column, value)

    if unavailable_fields:
        return None, specified_optional_fields, unavailable_fields

    return len(working), specified_optional_fields, []


def make_scenario(
    *,
    airport_id,
    faa_region,
    ac_class,
    ac_mass_group,
    season,
    phase_of_flight,
    optional_override_field=None,
    optional_override_value=None,
):
    """Construct a Scenario while leaving non-compared optional fields sampled."""
    values = {
        "ac_class": ac_class,
        "ac_mass_group": ac_mass_group,
        "season": season,
        "phase_of_flight": phase_of_flight,
        "airport_id": airport_id,
        "faa_region": faa_region,
        "wildlife_type": None,
        "size": None,
        "num_struck": None,
        "type_eng": None,
        "num_engs": None,
        "warned": None,
        "height": None,
        "speed": None,
        "time_of_day": None,
        "sky": None,
        "precipitation": None,
        "state": None,
    }

    if optional_override_field is not None:
        values[optional_override_field] = optional_override_value

    return Scenario(**values)


def scenario_display_dict(scenario, airport_labels):
    """Return scenario details with display labels added for readability."""
    display = scenario.to_dict().copy()
    display["aircraft_class_label"] = format_aircraft_class(scenario.ac_class)

    if scenario.airport_id is not None:
        display["airport"] = airport_labels.get(scenario.airport_id, scenario.airport_id)
    if scenario.type_eng is not None:
        display["engine_type_label"] = format_engine_type(scenario.type_eng)
    if scenario.state is not None:
        display["state_label"] = format_state(scenario.state)

    return display


def style_figure(fig, height=None):
    """Apply the shared responsive dashboard chart layout."""
    fig = apply_chart_layout(fig, height=height)
    fig.update_layout(hovermode="closest")
    return fig


# =====================================================================
# Load simulation artifacts
# =====================================================================

try:
    donor_data = load_simulation_donors()
    support_data = load_scenario_support()
except Exception as exc:
    st.error("Simulation reference data could not be loaded. " f"Details: {exc}")
    st.stop()

airport_labels = build_airport_labels(donor_data)


# =====================================================================
# Cache simulation infrastructure
# =====================================================================

@st.cache_resource
def get_simulation_engine():
    prediction_service = PredictionService()
    support_evaluator = SupportEvaluator(support_data)
    donor_sampler = DonorSampler(donor_data)

    return SimulationEngine(
        support_evaluator=support_evaluator,
        donor_sampler=donor_sampler,
        prediction_service=prediction_service,
    )


# =====================================================================
# Shared scenario context
# =====================================================================

section_divider()
section_header(
    "1. Shared scenario context",
    (
        "Define the conditions that will remain fixed across both simulations. "
        "Selections cascade through the historical support artifact so that "
        "the required scenario context remains valid."
    ),
)

context_col1, context_col2 = st.columns([1, 1], gap="medium")

with context_col1:
    with st.container(border=True):
        st.markdown("#### Geography")

        geography_mode = st.radio(
            "Scenario geography",
            options=["Airport", "FAA Region"],
            horizontal=True,
            key="comparison_geography_mode",
        )

        shared_working = support_data.copy()
        airport_id = None
        faa_region = None

        if geography_mode == "Airport":
            geography_options = sorted_values(support_data, "AIRPORT_ID")
            require_options(
                geography_options,
                "No airports are available in the historical support artifact.",
            )

            airport_id = st.selectbox(
                "Airport",
                geography_options,
                format_func=lambda value: airport_labels.get(value, value),
                key="comparison_airport_id",
            )

            shared_working = filter_equals(shared_working, "AIRPORT_ID", airport_id)
        else:
            geography_options = sorted_values(support_data, "FAAREGION")
            require_options(
                geography_options,
                "No FAA regions are available in the historical support artifact.",
            )

            faa_region = st.selectbox(
                "FAA Region",
                geography_options,
                key="comparison_faa_region",
            )

            shared_working = filter_equals(shared_working, "FAAREGION", faa_region)

        st.caption(
            "Airport-level comparisons use a more specific donor population; "
            "FAA-region comparisons broaden the geographic support base."
        )

with context_col2:
    with st.container(border=True):
        st.markdown("#### Aircraft context")

        ac_class_options = sorted_values(shared_working, "AC_CLASS")
        require_options(
            ac_class_options,
            "No aircraft classes are available for the selected geography.",
        )

        ac_class = st.selectbox(
            "Aircraft Class",
            ac_class_options,
            format_func=format_aircraft_class,
            key="comparison_ac_class",
        )

        shared_working = filter_equals(shared_working, "AC_CLASS", ac_class)

        mass_options = sorted_values(shared_working, "AC_MASS_GROUP")
        require_options(
            mass_options,
            "No aircraft mass groups are available for the selected context.",
        )

        ac_mass_group = st.selectbox(
            "Aircraft Mass Group",
            mass_options,
            key="comparison_mass_group",
        )

        shared_working = filter_equals(shared_working, "AC_MASS_GROUP", ac_mass_group)

        st.caption(
            "Aircraft class and mass group are held constant so the comparison "
            "does not mix changes in aircraft characteristics with the selected "
            "what-if factor."
        )


# =====================================================================
# Comparison variable
# =====================================================================

section_divider()
section_header(
    "2. Choose one comparison variable",
    (
        "Scenario A and Scenario B should differ in one factor whenever "
        "possible. Required support is enforced; optional overrides may be "
        "counterfactual and are audited separately."
    ),
)

COMPARISON_FIELDS = {
    "Season": {
        "scenario_field": "season",
        "data_column": "SEASON",
        "kind": "required",
    },
    "Phase of flight": {
        "scenario_field": "phase_of_flight",
        "data_column": "PHASE_OF_FLIGHT",
        "kind": "required",
    },
    "Wildlife type": {
        "scenario_field": "wildlife_type",
        "data_column": "WILDLIFE_TYPE",
        "kind": "optional",
    },
    "Wildlife size": {
        "scenario_field": "size",
        "data_column": "SIZE",
        "kind": "optional",
    },
    "Number struck": {
        "scenario_field": "num_struck",
        "data_column": "NUM_STRUCK",
        "kind": "optional",
    },
    "Engine type": {
        "scenario_field": "type_eng",
        "data_column": "TYPE_ENG",
        "kind": "optional",
    },
    "Number of engines": {
        "scenario_field": "num_engs",
        "data_column": "NUM_ENGS",
        "kind": "optional_numeric",
    },
    "Wildlife warning": {
        "scenario_field": "warned",
        "data_column": "WARNED",
        "kind": "optional",
    },
    "Time of day": {
        "scenario_field": "time_of_day",
        "data_column": "TIME_OF_DAY",
        "kind": "optional",
    },
}

comparison_variable = st.selectbox(
    "What do you want to compare?",
    options=list(COMPARISON_FIELDS),
    key="comparison_variable",
)

comparison_spec = COMPARISON_FIELDS[comparison_variable]
scenario_a_override = None
scenario_b_override = None
optional_override_field = None


# ---------------------------------------------------------------------
# Build required season / phase context around the selected comparison
# ---------------------------------------------------------------------

if comparison_variable == "Season":
    season_options = sorted_values(shared_working, "SEASON")
    require_options(
        season_options,
        "No seasons are available for the shared scenario context.",
    )

    comparison_col1, comparison_col2 = st.columns(2, gap="medium")

    with comparison_col1:
        scenario_a_override = st.selectbox(
            "Scenario A — Season",
            season_options,
            key="scenario_a_compare_value",
        )

    with comparison_col2:
        scenario_b_override = st.selectbox(
            "Scenario B — Season",
            season_options,
            index=1 if len(season_options) > 1 else 0,
            key="scenario_b_compare_value",
        )

    a_phase_source = filter_equals(shared_working, "SEASON", scenario_a_override)
    b_phase_source = filter_equals(shared_working, "SEASON", scenario_b_override)

    common_phase_options = sorted(
        set(sorted_values(a_phase_source, "PHASE_OF_FLIGHT"))
        & set(sorted_values(b_phase_source, "PHASE_OF_FLIGHT"))
    )

    require_options(
        common_phase_options,
        (
            "The selected seasons do not share a supported phase of flight "
            "under the current geography and aircraft context."
        ),
    )

    phase_of_flight = st.selectbox(
        "Shared Phase of Flight",
        common_phase_options,
        key="comparison_shared_phase",
    )

    season_a = scenario_a_override
    season_b = scenario_b_override

elif comparison_variable == "Phase of flight":
    season_options = sorted_values(shared_working, "SEASON")
    require_options(
        season_options,
        "No seasons are available for the shared scenario context.",
    )

    season_a = st.selectbox(
        "Shared Season",
        season_options,
        key="comparison_shared_season",
    )
    season_b = season_a

    phase_source = filter_equals(shared_working, "SEASON", season_a)
    phase_options = sorted_values(phase_source, "PHASE_OF_FLIGHT")
    require_options(
        phase_options,
        "No phases of flight are available for the shared scenario context.",
    )

    comparison_col1, comparison_col2 = st.columns(2, gap="medium")

    with comparison_col1:
        scenario_a_override = st.selectbox(
            "Scenario A — Phase of Flight",
            phase_options,
            key="scenario_a_compare_value",
        )

    with comparison_col2:
        scenario_b_override = st.selectbox(
            "Scenario B — Phase of Flight",
            phase_options,
            index=1 if len(phase_options) > 1 else 0,
            key="scenario_b_compare_value",
        )

    phase_of_flight = None

else:
    season_options = sorted_values(shared_working, "SEASON")
    require_options(
        season_options,
        "No seasons are available for the shared scenario context.",
    )

    required_col1, required_col2 = st.columns(2, gap="medium")

    with required_col1:
        season_a = st.selectbox(
            "Shared Season",
            season_options,
            key="comparison_shared_season",
        )
    season_b = season_a

    phase_source = filter_equals(shared_working, "SEASON", season_a)
    phase_options = sorted_values(phase_source, "PHASE_OF_FLIGHT")
    require_options(
        phase_options,
        "No phases of flight are available for the shared scenario context.",
    )

    with required_col2:
        phase_of_flight = st.selectbox(
            "Shared Phase of Flight",
            phase_options,
            key="comparison_shared_phase",
        )

    optional_override_field = comparison_spec["scenario_field"]

    # Restrict optional comparison choices to donor rows that match the
    # shared required scenario context. This prevents the UI from offering
    # values that are only observed elsewhere in the historical donor pool.
    comparison_donor_context = donor_data.copy()

    if airport_id is not None:
        comparison_donor_context = filter_equals(
            comparison_donor_context,
            "AIRPORT_ID",
            airport_id,
        )

    if faa_region is not None:
        comparison_donor_context = filter_equals(
            comparison_donor_context,
            "FAAREGION",
            faa_region,
        )

    comparison_donor_context = filter_equals(
        comparison_donor_context,
        "AC_CLASS",
        ac_class,
    )

    comparison_donor_context = filter_equals(
        comparison_donor_context,
        "AC_MASS_GROUP",
        ac_mass_group,
    )

    comparison_donor_context = filter_equals(
        comparison_donor_context,
        "SEASON",
        season_a,
    )

    comparison_donor_context = filter_equals(
        comparison_donor_context,
        "PHASE_OF_FLIGHT",
        phase_of_flight,
    )

    if comparison_spec["kind"] == "optional_numeric":
        comparison_options = sorted_numeric_values(
            comparison_donor_context,
            comparison_spec["data_column"],
        )
    else:
        comparison_options = sorted_values(
            comparison_donor_context,
            comparison_spec["data_column"],
        )

    require_options(
        comparison_options,
        (
            f"No historically observed values are available for "
            f"{comparison_variable} under the current shared scenario context."
        ),
    )

    # If only one value occurs in the selected historical context, explain
    # why an A/B comparison cannot currently be formed instead of silently
    # showing the same value in both selectors.
    if len(comparison_options) < 2:
        only_value = format_comparison_value(
            comparison_variable,
            comparison_options[0],
        )

        st.info(
            f"Only one historically observed value is available for "
            f"{comparison_variable} under the current shared scenario context: "
            f"{only_value}."
        )

        st.warning(
            f"A comparison on {comparison_variable} requires at least two "
            "historically observed values under the selected geography, "
            "aircraft, season, and phase of flight. Change the shared context "
            "or choose another comparison variable."
        )

        st.stop()

    comparison_col1, comparison_col2 = st.columns(2, gap="medium")
    value_formatter = lambda value: format_comparison_value(
        comparison_variable,
        value,
    )

    with comparison_col1:
        scenario_a_override = st.selectbox(
            f"Scenario A — {comparison_variable}",
            comparison_options,
            format_func=value_formatter,
            key="scenario_a_compare_value",
        )

    with comparison_col2:
        scenario_b_override = st.selectbox(
            f"Scenario B — {comparison_variable}",
            comparison_options,
            index=1,
            format_func=value_formatter,
            key="scenario_b_compare_value",
        )

with st.expander(
    "Why are some Page 04 optional fields not comparison controls?",
    expanded=False,
):
    st.markdown(
        """
        The comparison page intentionally exposes a smaller set of controls
        than the single-scenario simulator.

        - **State / location** is not independently varied because it is tied
          to the selected airport geography.
        - **Height and speed** are continuous and strongly related to flight
          phase; forcing exact values can create very sparse or operationally
          inconsistent combinations.
        - **Sky and precipitation** remain historically sampled in this
          comparison workflow to avoid over-conditioning the scenario.

        These fields can still influence donor sampling. They are omitted as
        direct comparison controls so that the main A/B interpretation remains
        easier to defend.
        """
    )


# =====================================================================
# Construct Scenario A and B
# =====================================================================

if comparison_variable == "Season":
    scenario_a = make_scenario(
        airport_id=airport_id,
        faa_region=faa_region,
        ac_class=ac_class,
        ac_mass_group=ac_mass_group,
        season=season_a,
        phase_of_flight=phase_of_flight,
    )
    scenario_b = make_scenario(
        airport_id=airport_id,
        faa_region=faa_region,
        ac_class=ac_class,
        ac_mass_group=ac_mass_group,
        season=season_b,
        phase_of_flight=phase_of_flight,
    )
elif comparison_variable == "Phase of flight":
    scenario_a = make_scenario(
        airport_id=airport_id,
        faa_region=faa_region,
        ac_class=ac_class,
        ac_mass_group=ac_mass_group,
        season=season_a,
        phase_of_flight=scenario_a_override,
    )
    scenario_b = make_scenario(
        airport_id=airport_id,
        faa_region=faa_region,
        ac_class=ac_class,
        ac_mass_group=ac_mass_group,
        season=season_b,
        phase_of_flight=scenario_b_override,
    )
else:
    scenario_a = make_scenario(
        airport_id=airport_id,
        faa_region=faa_region,
        ac_class=ac_class,
        ac_mass_group=ac_mass_group,
        season=season_a,
        phase_of_flight=phase_of_flight,
        optional_override_field=optional_override_field,
        optional_override_value=scenario_a_override,
    )
    scenario_b = make_scenario(
        airport_id=airport_id,
        faa_region=faa_region,
        ac_class=ac_class,
        ac_mass_group=ac_mass_group,
        season=season_b,
        phase_of_flight=phase_of_flight,
        optional_override_field=optional_override_field,
        optional_override_value=scenario_b_override,
    )


# =====================================================================
# Validate and audit support
# =====================================================================

try:
    scenario_a.validate()
    scenario_b.validate()
except ValueError as exc:
    st.error(str(exc))
    st.stop()

support_evaluator = SupportEvaluator(support_data)
support_a = support_evaluator.evaluate(scenario_a)
support_b = support_evaluator.evaluate(scenario_b)

full_support_a, optional_fields_a, unavailable_a = count_full_specified_support(
    donor_data,
    scenario_a,
)
full_support_b, optional_fields_b, unavailable_b = count_full_specified_support(
    donor_data,
    scenario_b,
)

section_divider()
section_header(
    "3. Historical support",
    (
        "Required-context support determines whether each simulation may run. "
        "When an optional comparison value is explicitly imposed, full "
        "specified-context support is shown separately."
    ),
)

support_col1, support_col2 = st.columns(2, gap="medium")


def render_support_panel(
    title,
    support,
    full_support_count,
    optional_fields,
    unavailable_fields,
):
    with st.container(border=True):
        st.markdown(f"#### {title}")

        if support.supported:
            st.success(
                f"Required scenario context is supported by "
                f"{support.exact_count:,} historical records."
            )
        else:
            st.error("This required scenario context has no exact historical support.")

        st.metric(
            "Required support records",
            f"{support.exact_count:,}",
            help=(
                "Historical donor records matching geography, aircraft class, "
                "aircraft mass group, season, and phase of flight."
            ),
        )

        if optional_fields:
            if unavailable_fields:
                st.warning(
                    "Full specified-context support could not be evaluated "
                    "because one or more donor columns are unavailable."
                )
            elif full_support_count is not None and full_support_count > 0:
                st.info(
                    f"Full specified-context support: "
                    f"{full_support_count:,} historical record"
                    f"{'s' if full_support_count != 1 else ''}."
                )
            else:
                st.warning(
                    "The required context is supported, but this complete "
                    "optional override combination was not observed in the "
                    "historical donor data. Treat this as a counterfactual estimate."
                )

with support_col1:
    render_support_panel(
        "Scenario A",
        support_a,
        full_support_a,
        optional_fields_a,
        unavailable_a,
    )

with support_col2:
    render_support_panel(
        "Scenario B",
        support_b,
        full_support_b,
        optional_fields_b,
        unavailable_b,
    )

if not support_a.supported or not support_b.supported:
    st.error(
        "Both scenarios require exact required-context support before the "
        "comparison can run. Adjust the comparison values or shared context."
    )
    st.stop()


# =====================================================================
# Difference check
# =====================================================================

scenario_a_dict = scenario_a.to_dict()
scenario_b_dict = scenario_b.to_dict()

changed_fields = [
    field
    for field in scenario_a_dict
    if scenario_a_dict.get(field) != scenario_b_dict.get(field)
]

if len(changed_fields) == 0:
    st.info(
        "Scenario A and Scenario B are currently identical. Select different "
        "values to create a meaningful comparison."
    )
elif len(changed_fields) == 1:
    field = changed_fields[0]
    st.success(
        "Controlled one-variable comparison: "
        f"{field.replace('_', ' ').title()} changes from "
        f"{scenario_a_dict.get(field)} to {scenario_b_dict.get(field)}."
    )
else:
    st.warning(
        f"The scenarios differ in {len(changed_fields)} fields: "
        + ", ".join(field.replace("_", " ").title() for field in changed_fields)
        + ". Differences in the results cannot be attributed to one factor alone."
    )


# =====================================================================
# Comparison settings and review
# =====================================================================

section_divider()
section_header(
    "4. Comparison settings",
    (
        "Both simulations use the same trial count and random seed so the "
        "Monte Carlo settings remain directly comparable."
    ),
)

settings_col1, settings_col2 = st.columns(2, gap="medium")

with settings_col1:
    n_trials = st.number_input(
        "Monte Carlo Trials",
        min_value=100,
        max_value=100_000,
        value=10_000,
        step=1_000,
        key="comparison_trials",
    )

with settings_col2:
    seed = st.number_input(
        "Shared Random Seed",
        min_value=0,
        value=42,
        step=1,
        key="comparison_seed",
    )

with st.expander("Review scenarios before running", expanded=False):
    review_col1, review_col2 = st.columns(2, gap="medium")

    with review_col1:
        st.markdown("#### Scenario A")
        st.json(scenario_display_dict(scenario_a, airport_labels))

    with review_col2:
        st.markdown("#### Scenario B")
        st.json(scenario_display_dict(scenario_b, airport_labels))


# =====================================================================
# Run comparison
# =====================================================================

section_divider()
section_header(
    "5. Run comparison",
    (
        "Modeled probability differences are the primary comparison outputs. "
        "Realized Monte Carlo rates are retained as secondary diagnostics."
    ),
)

run_clicked = st.button("Run Scenario Comparison", type="primary")

if run_clicked:
    try:
        with st.spinner(f"Running two {int(n_trials):,}-trial simulations..."):
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
        st.error("The scenario comparison could not be completed.")
        st.exception(exc)
        st.stop()

    # =================================================================
    # Main damage comparison
    # =================================================================

    section_divider()
    section_header(
        "Comparison results",
        (
            "Percentage-point differences are emphasized because they show "
            "the absolute modeled change directly. Relative change is secondary "
            "and can appear large when Scenario A is small."
        ),
    )

    st.markdown("### Aircraft damage probability")

    a_damage = result_a.mean_damage_probability
    b_damage = result_b.mean_damage_probability
    damage_pp = pp_difference(a_damage, b_damage)
    damage_relative = relative_change(a_damage, b_damage)

    metric_row(
        [
            (
                "Scenario A",
                f"{a_damage:.2%}",
                "Mean modeled aircraft-damage probability for Scenario A.",
            ),
            (
                "Scenario B",
                f"{b_damage:.2%}",
                "Mean modeled aircraft-damage probability for Scenario B.",
            ),
            (
                "Difference (B − A)",
                f"{damage_pp:+.2f} pp",
                (
                    "Absolute percentage-point difference. "
                    f"Relative change: {format_relative(damage_relative)}."
                ),
            ),
        ]
    )

    damage_chart = pd.DataFrame(
        {
            "Scenario": ["Scenario A", "Scenario B"],
            "Probability (%)": [a_damage * 100, b_damage * 100],
        }
    )

    damage_fig = px.bar(
        damage_chart,
        x="Scenario",
        y="Probability (%)",
        text="Probability (%)",
        labels={"Probability (%)": "Modeled damage probability (%)"},
    )
    damage_fig.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside",
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Modeled damage probability: %{y:.2f}%"
            "<extra></extra>"
        ),
    )
    damage_fig = style_figure(damage_fig, height=360)

    st.plotly_chart(
        damage_fig,
        use_container_width=True,
        config=PLOTLY_CONFIG,
    )

    st.caption(
        f"Relative change from Scenario A to Scenario B: "
        f"{format_relative(damage_relative)}. "
        "Use the percentage-point difference as the primary interpretation."
    )

    # =================================================================
    # Severity comparison
    # =================================================================

    st.markdown("### Severity probability conditional on damage")

    a_severity = result_a.severity_probability_mean_damaged
    b_severity = result_b.severity_probability_mean_damaged

    if a_severity is not None and b_severity is not None:
        severity_pp = pp_difference(a_severity, b_severity)
        severity_relative = relative_change(a_severity, b_severity)

        metric_row(
            [
                (
                    "Scenario A",
                    f"{a_severity:.2%}",
                    "Mean severity probability among damaged trials.",
                ),
                (
                    "Scenario B",
                    f"{b_severity:.2%}",
                    "Mean severity probability among damaged trials.",
                ),
                (
                    "Difference (B − A)",
                    f"{severity_pp:+.2f} pp",
                    (
                        "Absolute percentage-point difference. "
                        f"Relative change: {format_relative(severity_relative)}."
                    ),
                ),
            ]
        )

        severity_chart = pd.DataFrame(
            {
                "Scenario": ["Scenario A", "Scenario B"],
                "Probability (%)": [a_severity * 100, b_severity * 100],
            }
        )

        severity_fig = px.bar(
            severity_chart,
            x="Scenario",
            y="Probability (%)",
            text="Probability (%)",
            labels={"Probability (%)": "Severity probability (%)"},
        )
        severity_fig.update_traces(
            texttemplate="%{text:.2f}%",
            textposition="outside",
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Severity probability: %{y:.2f}%"
                "<extra></extra>"
            ),
        )
        severity_fig = style_figure(severity_fig, height=360)

        st.plotly_chart(
            severity_fig,
            use_container_width=True,
            config=PLOTLY_CONFIG,
        )

        st.caption(
            "Severity is conditional on a simulated strike already resulting "
            "in aircraft damage."
        )
    else:
        st.info(
            "A severity comparison is unavailable because at least one "
            "scenario produced no damaged trials."
        )

    # =================================================================
    # Component probability comparison
    # =================================================================

    st.markdown("### Component probabilities conditional on damage")

    components = sorted(
        set(result_a.component_probability_means_damaged.keys())
        | set(result_b.component_probability_means_damaged.keys())
    )

    component_rows = []

    for component in components:
        a_value = result_a.component_probability_means_damaged.get(component)
        b_value = result_b.component_probability_means_damaged.get(component)

        if a_value is None or b_value is None:
            continue

        component_rows.append(
            {
                "Component": component_label(component),
                "Scenario A": a_value,
                "Scenario B": b_value,
                "Difference (pp)": pp_difference(a_value, b_value),
                "Relative Change": relative_change(a_value, b_value),
            }
        )

    if component_rows:
        component_df = pd.DataFrame(component_rows)
        component_df = component_df.sort_values(
            "Difference (pp)",
            key=lambda series: series.abs(),
            ascending=False,
        )

        component_long = component_df[
            ["Component", "Scenario A", "Scenario B"]
        ].melt(
            id_vars="Component",
            var_name="Scenario",
            value_name="Probability",
        )
        component_long["Probability (%)"] = component_long["Probability"] * 100

        component_fig = px.bar(
            component_long,
            x="Probability (%)",
            y="Component",
            color="Scenario",
            orientation="h",
            barmode="group",
            labels={"Probability (%)": "Probability (%)"},
        )
        component_fig.update_traces(
            hovertemplate=(
                "<b>%{y}</b><br>"
                "%{fullData.name}: %{x:.2f}%"
                "<extra></extra>"
            )
        )
        component_fig.update_yaxes(
            categoryorder="array",
            categoryarray=component_df["Component"].tolist()[::-1],
        )
        component_fig = style_figure(
            component_fig,
            height=max(360, 55 * len(component_df)),
        )

        st.plotly_chart(
            component_fig,
            use_container_width=True,
            config=PLOTLY_CONFIG,
        )

        display_df = component_df.copy()
        display_df["Scenario A"] = display_df["Scenario A"].map(
            lambda value: f"{value:.2%}"
        )
        display_df["Scenario B"] = display_df["Scenario B"].map(
            lambda value: f"{value:.2%}"
        )
        display_df["Difference (pp)"] = display_df["Difference (pp)"].map(
            lambda value: f"{value:+.2f}"
        )
        display_df["Relative Change"] = display_df["Relative Change"].map(
            format_relative
        )

        with st.expander("Component comparison table", expanded=False):
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
            )

        st.caption(
            "Component probabilities are conditional on aircraft damage. "
            "Components are modeled separately and are not mutually exclusive."
        )
    else:
        st.info(
            "Component probability comparison is unavailable because at least "
            "one scenario produced no damaged trials."
        )

    # =================================================================
    # Realized Monte Carlo outcomes
    # =================================================================

    with st.expander("Realized Monte Carlo outcomes", expanded=False):
        realized_rows = [
            {
                "Metric": "Simulated damage rate",
                "Scenario A": result_a.simulated_damage_rate,
                "Scenario B": result_b.simulated_damage_rate,
            },
            {
                "Metric": "Severe rate given damage",
                "Scenario A": result_a.simulated_severe_rate_given_damage,
                "Scenario B": result_b.simulated_severe_rate_given_damage,
            },
        ]

        realized_df = pd.DataFrame(realized_rows)
        realized_df["Difference (pp)"] = (
            realized_df["Scenario B"] - realized_df["Scenario A"]
        ) * 100

        display_realized = realized_df.copy()

        for column in ["Scenario A", "Scenario B"]:
            display_realized[column] = display_realized[column].map(
                lambda value: f"{value:.2%}" if pd.notna(value) else "Unavailable"
            )

        display_realized["Difference (pp)"] = display_realized[
            "Difference (pp)"
        ].map(
            lambda value: f"{value:+.2f}" if pd.notna(value) else "Unavailable"
        )

        st.dataframe(
            display_realized,
            use_container_width=True,
            hide_index=True,
        )

        st.caption(
            "These are realized Monte Carlo rates and therefore contain "
            "simulation noise. The modeled probability comparisons above are "
            "the primary comparison quantities."
        )

    # =================================================================
    # Support and run details
    # =================================================================

    section_divider()
    section_header(
        "Support and run details",
        (
            "Support counts describe historical coverage. Increasing the "
            "number of Monte Carlo trials reduces simulation noise but does "
            "not create additional historical support."
        ),
    )

    metric_row(
        [
            (
                "Scenario A required support",
                f"{result_a.support_count:,}",
                "Historical records matching Scenario A required context.",
            ),
            (
                "Scenario B required support",
                f"{result_b.support_count:,}",
                "Historical records matching Scenario B required context.",
            ),
        ]
    )

    with st.expander("Scenario definitions and run metadata", expanded=False):
        detail_col1, detail_col2 = st.columns(2, gap="medium")

        with detail_col1:
            st.markdown("#### Scenario A")
            st.json(scenario_display_dict(scenario_a, airport_labels))
            st.write(
                f"Required-context historical support: "
                f"{result_a.support_count:,} records"
            )
            if optional_fields_a:
                if full_support_a is None:
                    st.write("Full specified-context historical support: unavailable")
                else:
                    st.write(
                        "Full specified-context historical support: "
                        f"{full_support_a:,} records"
                    )

        with detail_col2:
            st.markdown("#### Scenario B")
            st.json(scenario_display_dict(scenario_b, airport_labels))
            st.write(
                f"Required-context historical support: "
                f"{result_b.support_count:,} records"
            )
            if optional_fields_b:
                if full_support_b is None:
                    st.write("Full specified-context historical support: unavailable")
                else:
                    st.write(
                        "Full specified-context historical support: "
                        f"{full_support_b:,} records"
                    )

        st.write(f"Trials per scenario: {result_a.n_trials:,}")
        st.write(f"Shared random seed: {result_a.seed}")
        st.write(f"Comparison variable: {comparison_variable}")
