"""Monte Carlo what-if simulation page."""

from __future__ import annotations

from dataclasses import asdict
import json
import os
from pathlib import Path
import shutil
import subprocess

import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard.components.charts import apply_chart_layout
from dashboard.components.layout import (
    page_header,
    section_divider,
    section_header,
)
from dashboard.components.metrics import metric_row
from src.data.loaders import (
    load_simulation_donors,
    load_scenario_support,
)
from src.simulation.donor_sampling import DonorSampler
from src.simulation.engine import SimulationEngine
from src.simulation.prediction import PredictionService
from src.simulation.scenario import Scenario
from src.simulation.support import SupportEvaluator
from src.utils.labels import (
    build_airport_labels,
    format_aircraft_class,
    format_engine_type,
    format_state
)


# =====================================================================
# Helpers
# =====================================================================

def sorted_values(data, column):
    """Return sorted non-null unique values from a dashboard artifact."""
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
    """Filter a dashboard artifact using normalized string comparison."""
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

def count_full_specified_support(data, scenario):
    """
    Count donor rows matching every scenario field that the user
    explicitly specified.

    Required fields are always included. Optional fields are included
    only when they are not None.

    This is an interpretability/support diagnostic only. It does not
    determine whether the simulation is allowed to run.
    """

    field_map = {
        "airport_id": "AIRPORT_ID",
        "faa_region": "FAAREGION",
        "ac_class": "AC_CLASS",
        "ac_mass_group": "AC_MASS_GROUP",
        "season": "SEASON",
        "phase_of_flight": "PHASE_OF_FLIGHT",

        # Optional scenario context
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

    scenario_values = scenario.to_dict()

    working = data.copy()
    specified_optional_fields = []

    required_fields = {
        "airport_id",
        "faa_region",
        "ac_class",
        "ac_mass_group",
        "season",
        "phase_of_flight",
    }

    for scenario_field, data_column in field_map.items():

        value = scenario_values.get(scenario_field)

        if value is None:
            continue

        if data_column not in working.columns:
            continue

        # Track explicit optional overrides separately so the UI knows
        # whether a counterfactual-support warning is relevant.
        if scenario_field not in required_fields:
            specified_optional_fields.append(scenario_field)

        # Numeric fields need numeric comparison so values such as
        # 2 and 2.0 are treated as equivalent.
        if scenario_field in {
            "num_engs",
            "height",
            "speed",
        }:
            numeric = pd.to_numeric(
                working[data_column],
                errors="coerce",
            )

            working = working.loc[
                numeric.eq(float(value))
            ].copy()

        else:
            normalized = (
                working[data_column]
                .astype("string")
                .str.strip()
            )

            working = working.loc[
                normalized.eq(str(value).strip())
            ].copy()

    return len(working), specified_optional_fields

def require_options(options, message):
    """Stop the page cleanly if no valid downstream choices remain."""
    if options:
        return

    st.warning(message)
    st.stop()


def optional_selectbox(label, values, key, format_func=None):
    """
    Select an optional categorical scenario value.

    'Historical sampling' is converted to None so that the donor sampler
    preserves the empirically sampled value from each historical donor row.
    """
    options = ["Historical sampling"] + values

    selected = st.selectbox(
        label,
        options=options,
        key=key,
        format_func=(
            lambda value: (
                value
                if value == "Historical sampling"
                else format_func(value)
            )
            if format_func is not None
            else value
        ),
    )

    if selected == "Historical sampling":
        return None

    return selected


def component_label(component):
    """Return a readable component label."""
    return (
        component
        .replace("_damage", "")
        .replace("_", " ")
        .title()
    )


def style_figure(fig, *, hovermode="closest"):
    """Apply shared dashboard Plotly styling."""
    fig = apply_chart_layout(fig)
    fig.update_layout(hovermode=hovermode)
    return fig


PLOTLY_CONFIG = {
    "displaylogo": False,
    "responsive": True,
}


# =====================================================================
# Local Godot visualization bridge
# =====================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]
GODOT_PROJECT_DIR = PROJECT_ROOT / "godot"
GODOT_TRIAL_PATH = GODOT_PROJECT_DIR / "data" / "latest_trial.json"


def simulation_run_signature(scenario, n_trials, seed):
    """Return the inputs that define the currently displayed simulation run."""
    return {
        "scenario": scenario.to_dict(),
        "n_trials": int(n_trials),
        "seed": int(seed),
    }


def export_visual_trial(result):
    """Write the retained random trial for the local Godot project."""
    if result.visual_trial is None:
        raise ValueError(
            "The simulation result does not contain a visual trial."
        )

    GODOT_TRIAL_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    payload = {
        "schema_version": "1.0",
        "simulation": {
            "n_trials": result.n_trials,
            "seed": result.seed,
        },
        "visual_trial": asdict(result.visual_trial),
    }

    with GODOT_TRIAL_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            payload,
            file,
            indent=2,
            ensure_ascii=False,
        )

    return GODOT_TRIAL_PATH


def find_godot_executable():
    """Resolve a local Godot executable without hard-coding one machine path."""
    configured = os.environ.get("GODOT_EXECUTABLE")

    if configured:
        configured_path = Path(configured).expanduser()
        if configured_path.is_file():
            return configured_path

    for command in ("godot", "godot4"):
        resolved = shutil.which(command)
        if resolved:
            return Path(resolved)

    return None


def launch_local_godot_project():
    """Launch the local Godot project so it reads the newly exported JSON."""
    godot_executable = find_godot_executable()

    if godot_executable is None:
        raise FileNotFoundError(
            "Godot could not be located. Set the GODOT_EXECUTABLE environment "
            "variable to the full path of godot.exe, or add Godot to PATH."
        )

    project_file = GODOT_PROJECT_DIR / "project.godot"

    if not project_file.is_file():
        raise FileNotFoundError(
            f"Godot project file was not found at: {project_file}"
        )

    subprocess.Popen(
        [
            str(godot_executable),
            "--path",
            str(GODOT_PROJECT_DIR),
        ],
        cwd=str(GODOT_PROJECT_DIR),
    )


# =====================================================================
# Page introduction
# =====================================================================

page_header(
    "Monte Carlo What-If Simulation",
    (
        "Construct a historically supported wildlife-strike scenario and "
        "estimate modeled damage, severity, and component outcomes through "
        "empirical Monte Carlo simulation."
    ),
)

st.caption(
    "Required scenario characteristics are fixed by the user. Optional "
    "characteristics can be specified manually or preserved through "
    "historical donor sampling."
)


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


airport_labels = build_airport_labels(donor_data)


# =====================================================================
# Cache model / simulation infrastructure
# =====================================================================

@st.cache_resource
def get_simulation_engine():
    """Construct and cache the reusable simulation service."""
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
# Required scenario definition
# =====================================================================

section_divider()

section_header(
    "Define the required scenario",
    (
        "These selections determine the historical support population used "
        "by the simulation. Downstream choices are restricted to combinations "
        "that remain historically supported."
    ),
)

scenario_col1, scenario_col2 = st.columns(
    2,
    gap="medium",
)

with scenario_col1:
    with st.container(border=True):
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

        st.caption(
            "Airport-level scenarios are more specific; FAA-region scenarios "
            "broaden the geographic donor population."
        )


with scenario_col2:
    with st.container(border=True):
        st.markdown("#### Required flight context")

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


# =====================================================================
# Optional scenario context
# =====================================================================

with st.expander(
    "Optional scenario context",
    expanded=False,
):

    st.caption(
        "Leave a variable as Historical sampling to retain the value from "
        "each sampled donor record instead of forcing a fixed value."
    )

    optional_col1, optional_col2 = st.columns(
        2,
        gap="medium",
    )

    with optional_col1:

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
            format_func=format_engine_type,
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

    with optional_col2:

        precipitation = optional_selectbox(
            "Precipitation",
            sorted_values(
                donor_data,
                "PRECIPITATION",
            ),
            key="precipitation",
        )

        if geography_mode == "FAA Region":
            state = optional_selectbox(
                "State / location",
                sorted_values(
                    donor_data,
                    "STATE",
                ),
                key="state",
                format_func=format_state,
            )

        else:
            state = None

            st.caption(
                "State/location is determined by the selected airport "
                "and is not independently overridden."
            )

        specify_num_struck = st.checkbox(
            "Specify number struck"
        )

        num_struck = None

        if specify_num_struck:
            num_struck_options = sorted_values(
                donor_data,
                "NUM_STRUCK",
            )

            num_struck = st.selectbox(
                "Number Struck",
                num_struck_options,
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
# Construct and validate scenario
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

full_support_count, specified_optional_fields = (
    count_full_specified_support(
        donor_data,
        scenario,
    )
)

# =====================================================================
# Historical support
# =====================================================================

section_divider()

section_header(
    "Historical support",
    (
        "Support measures how many 1990–2021 historical donor records match "
        "the required scenario context. It describes data coverage, not "
        "physical certainty."
    ),
)

support_col1, support_col2 = st.columns(
    [2, 1],
    gap="medium",
)

with support_col1:
    if support.supported:
        st.success(
            f"Required scenario context is supported by "
            f"{support.exact_count:,} compatible historical records."
        )

        if specified_optional_fields:

            readable_fields = [
                field.replace("_", " ").title()
                for field in specified_optional_fields
            ]

            if full_support_count > 0:

                st.info(
                    f"The complete specified scenario, including the optional "
                    f"override(s) {', '.join(readable_fields)}, appears in "
                    f"{full_support_count:,} historical donor record"
                    f"{'s' if full_support_count != 1 else ''}."
                )

            else:

                st.warning(
                    "The required scenario is historically supported, but the "
                    "complete combination including the selected optional "
                    "override(s) was not observed in the historical donor data. "
                    "The simulation will therefore treat these optional values "
                    "as a counterfactual override."
                )

                st.caption(
                    "Optional override(s): "
                    + ", ".join(readable_fields)
                    + ". The simulation is allowed to continue because required "
                    "scenario support is present, but the resulting estimate "
                    "should be interpreted with greater caution."
                )

    else:
        st.error(
            "This required scenario combination has no exact historical "
            "support in the 1990–2021 simulation reference population."
        )

        st.info(
            "Change one or more required scenario characteristics before "
            "running the simulation. The dashboard does not generate a "
            "numerical estimate for completely unsupported combinations."
        )

with support_col2:
    with st.container(border=True):
        st.metric(
            "Required-context support",
            f"{support.exact_count:,}",
            help=(
                "Historical donor records matching the required scenario fields: "
                "geography, aircraft class, aircraft mass group, season, "
                "and phase of flight."
            ),

        )

        st.caption(
            f"Geography level: {support.geography_level}"
        )


if not support.supported:
    st.stop()


# =====================================================================
# Simulation configuration
# =====================================================================

section_divider()

section_header(
    "Simulation settings",
    (
        "The default run uses 10,000 trials. The random seed allows the "
        "simulation to be reproduced."
    ),
)

settings_col1, settings_col2 = st.columns(
    2,
    gap="medium",
)

with settings_col1:
    n_trials = st.number_input(
        "Monte Carlo Trials",
        min_value=100,
        max_value=100_000,
        value=10_000,
        step=1_000,
    )

with settings_col2:
    seed = st.number_input(
        "Random Seed",
        min_value=0,
        value=42,
        step=1,
    )


with st.expander(
    "Review scenario before running",
    expanded=False,
):
    scenario_display = scenario.to_dict().copy()

    scenario_display["aircraft_class_label"] = (
        format_aircraft_class(scenario.ac_class)
    )

    if scenario.type_eng is not None:
        scenario_display["engine_type_label"] = (
            format_engine_type(scenario.type_eng)
        )

    if scenario.state is not None:
        scenario_display["state_label"] = (
            format_state(scenario.state)
        )

    if scenario.airport_id is not None:
        scenario_display["airport"] = airport_labels.get(
            scenario.airport_id,
            scenario.airport_id,
        )
        
    st.json(scenario_display)


# =====================================================================
# Run simulation
# =====================================================================

section_divider()

section_header(
    "Run simulation",
    "Run the current supported scenario using the settings above.",
)

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

    st.session_state["latest_monte_carlo_result"] = result
    st.session_state["latest_monte_carlo_signature"] = (
        simulation_run_signature(
            scenario,
            n_trials,
            seed,
        )
    )


current_run_signature = simulation_run_signature(
    scenario,
    n_trials,
    seed,
)

result = st.session_state.get(
    "latest_monte_carlo_result"
)

stored_run_signature = st.session_state.get(
    "latest_monte_carlo_signature"
)


if (
    result is not None
    and stored_run_signature == current_run_signature
):

    # =================================================================
    # Main damage results
    # =================================================================

    section_divider()

    section_header(
        "Simulation results",
        (
            "Modeled probabilities summarize the model outputs across "
            "simulated donor rows. Realized rates reflect the stochastic "
            "Monte Carlo outcomes from this specific run."
        ),
    )

    st.markdown("### Aircraft damage")

    metric_row(
        [
            (
                "Mean damage probability",
                f"{result.mean_damage_probability:.2%}",
                (
                    "Average calibrated model probability across the "
                    "simulated scenario rows."
                ),
            ),
            (
                "Simulated damage rate",
                f"{result.simulated_damage_rate:.2%}",
                (
                    "Realized proportion of Monte Carlo trials sampled "
                    "as aircraft-damage outcomes."
                ),
            ),
            (
                "Damaged trials",
                (
                    f"{result.simulated_damage_count:,} "
                    f"/ {result.n_trials:,}"
                ),
                "Number of realized damaged outcomes in this simulation run.",
            ),
        ]
    )

    st.caption(
        "The mean modeled probability is the primary probability summary. "
        "The simulated damage rate contains Monte Carlo noise and will vary "
        "slightly across random seeds."
    )


    # =================================================================
    # Severity results
    # =================================================================

    st.markdown("### Severity conditional on damage")

    if result.simulated_damage_count > 0:

        metric_row(
            [
                (
                    "Mean severity probability",
                    f"{result.severity_probability_mean_damaged:.2%}",
                    (
                        "Average severity-model probability among simulated "
                        "trials that resulted in aircraft damage."
                    ),
                ),
                (
                    "Simulated severe rate",
                    f"{result.simulated_severe_rate_given_damage:.2%}",
                    (
                        "Realized severe-outcome rate among damaged trials."
                    ),
                ),
                (
                    "Severe outcomes",
                    (
                        f"{result.simulated_severe_count:,} "
                        f"/ {result.simulated_damage_count:,}"
                    ),
                    "Realized severe outcomes among damaged trials.",
                ),
            ]
        )

        st.caption(
            "Severity is conditional on a simulated strike already resulting "
            "in aircraft damage. It is not an unconditional probability across "
            "all strike trials."
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
            "### Component damage conditional on damage"
        )

        component_rows = []

        for component, count in result.component_counts.items():

            rate = result.component_rates_given_damage.get(
                component,
                0.0,
            )

            component_rows.append(
                {
                    "Component": component_label(component),
                    "Simulated Count": count,
                    "Rate Given Damage": rate * 100,
                }
            )

        component_df = pd.DataFrame(
            component_rows
        ).sort_values(
            "Rate Given Damage",
            ascending=True,
        )

        component_fig = px.bar(
            component_df,
            x="Rate Given Damage",
            y="Component",
            orientation="h",
            custom_data=["Simulated Count"],
            labels={
                "Rate Given Damage": "Rate given damage (%)",
                "Component": "Component",
            },
        )

        component_fig.update_traces(
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Rate given damage: %{x:.2f}%<br>"
                "Simulated count: %{customdata[0]:,}"
                "<extra></extra>"
            ),
        )

        component_fig = style_figure(
            component_fig
        )

        st.plotly_chart(
            component_fig,
            use_container_width=True,
            config=PLOTLY_CONFIG,
        )

        with st.expander(
            "View component result table",
            expanded=False,
        ):
            display_component_df = (
                component_df
                .sort_values(
                    "Rate Given Damage",
                    ascending=False,
                )
                .copy()
            )

            display_component_df[
                "Rate Given Damage"
            ] = (
                display_component_df[
                    "Rate Given Damage"
                ]
                .map(lambda value: f"{value:.2f}%")
            )

            st.dataframe(
                display_component_df,
                use_container_width=True,
                hide_index=True,
            )

        st.caption(
            "Component outcomes are conditional on aircraft damage. "
            "The retained component systems are not mutually exclusive, "
            "so one damaged trial can contribute to multiple components."
        )


    # =================================================================
    # Run information
    # =================================================================

    with st.expander(
        "Simulation details",
        expanded=False,
    ):

        detail_col1, detail_col2 = st.columns(
            2,
            gap="medium",
        )

        with detail_col1:
            st.write(
                f"Trials: {result.n_trials:,}"
            )

            st.write(
                f"Random seed: {result.seed}"
            )

        with detail_col2:
            st.write(
                f"Required-context historical support: "
                f"{result.support_count:,} records"
            )
            
            if specified_optional_fields:
                st.write(
                    f"Full specified-context historical support: "
                    f"{full_support_count:,} records"
                )

            st.write(
                f"Geography level: "
                f"{result.geography_level}"
            )

        st.markdown(
            "**Scenario supplied to the simulation:**"
        )

        scenario_display = scenario.to_dict().copy()

        if scenario_display.get("airport_id") is not None:
            scenario_display["airport"] = airport_labels.get(
                scenario_display["airport_id"],
                scenario_display["airport_id"],
            )

        st.json(
            scenario_display
        )

    # =================================================================
    # Optional Godot single-trial visualization
    # =================================================================

    section_divider()

    section_header(
        "Single-Trial Visualization",
        (
            "Open an illustrative 2D visualization of the one random "
            "Monte Carlo realization retained from this simulation run."
        ),
    )

    with st.container(border=True):
        st.caption(
            "The Godot scene consumes the already-realized Python trial. "
            "It does not rerun the model, resample the outcome, or simulate "
            "physical collision dynamics."
        )

        if result.visual_trial is None:
            st.info(
                "No visual trial is available for this simulation result."
            )

        else:
            if st.button(
                "Visualize Random Trial",
                key="launch_godot_visual_trial",
            ):
                try:
                    exported_path = export_visual_trial(
                        result
                    )

                    launch_local_godot_project()

                    st.success(
                        "Godot visualizer launched using the retained random trial."
                    )

                    st.caption(
                        f"Trial payload: {exported_path}"
                    )

                except Exception as exc:
                    st.error(
                        "The Godot visualizer could not be launched."
                    )
                    st.exception(exc)

        st.caption(
            "Illustrative only — this is a schematic visualization of one "
            "stochastic realization, not a physical wildlife-strike simulation."
        )


elif result is not None:
    st.info(
        "The scenario or simulation settings have changed since the last run. "
        "Run the Monte Carlo simulation again to refresh the results and "
        "single-trial visualization."
    )

