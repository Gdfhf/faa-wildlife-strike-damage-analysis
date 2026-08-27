"""High-level landing page for the wildlife-strike dashboard."""

from __future__ import annotations

import streamlit as st
import plotly.express as px

from dashboard.components.layout import (
    page_header,
    section_divider,
    section_header,
)
from dashboard.components.metrics import metric_row
from src.data.loaders import (
    load_historical_data,
    load_overview_summary,
)

from dashboard.components.charts import apply_chart_layout

# ---------------------------------------------------------------------
# Page introduction
# ---------------------------------------------------------------------

page_header(
    "Wildlife Strike Risk Analysis",
    (
        "Explore historical FAA wildlife-strike patterns, predictive "
        "damage models, and supported operational what-if scenarios."
    ),
)


# ---------------------------------------------------------------------
# Load lightweight dashboard artifacts
# ---------------------------------------------------------------------

try:
    summary = load_overview_summary()
    df = load_historical_data()

except Exception as exc:
    st.error(
        "The dashboard overview data could not be loaded. "
        f"Details: {exc}"
    )
    st.stop()


# ---------------------------------------------------------------------
# Dataset summary
# ---------------------------------------------------------------------

section_header(
    "Dataset summary",
    (
        "A high-level snapshot of the analytical dataset used throughout "
        "the dashboard."
    ),
)

metric_row(
    [
        (
            "Reported strikes",
            f"{summary['n_records']:,}",
            "Wildlife-strike records included in the analytical dataset.",
        ),
        (
            "Damaging strikes",
            f"{summary['n_damaged']:,}",
            "Records reporting aircraft damage.",
        ),
        (
            "Airports represented",
            f"{summary['n_airports']:,}",
            "Distinct airports represented in the analytical dataset.",
        ),
        (
            "Study period",
            f"{summary['start_year']}–{summary['end_year']}",
            "Years covered by the analytical dataset.",
        ),
    ]
)

st.caption(
    f"Overall reported damage rate: {summary['damage_rate']:.2%} · "
    f"{summary['n_species']:,} wildlife species/categories represented."
)


# ---------------------------------------------------------------------
# Historical overview
# ---------------------------------------------------------------------

section_divider()

section_header(
    "Historical overview",
    (
        "Reported wildlife strikes provide the historical context for the "
        "predictive and simulation sections of the dashboard."
    ),
)

if "INCIDENT_YEAR" in df.columns:

    annual_strikes = (
        df.groupby("INCIDENT_YEAR")
        .size()
        .rename("Reported Strikes")
        .reset_index()
        .sort_values("INCIDENT_YEAR")
    )

    chart_col, interpretation_col = st.columns(
        [2, 1],
        gap="medium",
    )

    with chart_col:
        with st.container(border=True):
            st.markdown("#### Reported wildlife strikes over time")

            fig = px.line(
                annual_strikes,
                x="INCIDENT_YEAR",
                y="Reported Strikes",
                labels={
                    "INCIDENT_YEAR": "Year",
                    "Reported Strikes": "Reported strikes",
                },
            )

            fig = apply_chart_layout(fig)

            st.plotly_chart(
                fig,
                use_container_width=True,
            )

            st.caption(
                "Annual counts represent reported wildlife-strike records "
                "in the analytical dataset."
            )

    with interpretation_col:
        with st.container(border=True):
            st.markdown("#### Why this matters")

            st.write(
                "Reported strike counts change substantially across the "
                "study period. These trends provide historical exposure and "
                "reporting context, but they are not direct estimates of "
                "flight-level risk."
            )

            st.caption(
                "Changes over time can reflect both underlying wildlife-strike "
                "activity and changes in reporting. Use the Historical Data "
                "page for deeper filtering and descriptive analysis."
            )

else:
    st.warning(
        "INCIDENT_YEAR is not available in the historical dashboard artifact."
    )


# ---------------------------------------------------------------------
# Predictive model overview
# ---------------------------------------------------------------------

section_divider()

section_header(
    "What the predictive models estimate",
    (
        "The modelling workflow separates damage occurrence, damage severity, "
        "and affected aircraft components into related but distinct questions."
    ),
)

damage_col, severity_col, component_col = st.columns(
    3,
    gap="medium",
)

with damage_col:
    with st.container(border=True):
        st.markdown("#### Damage risk")
        st.write(
            "Estimates the probability that a reported wildlife strike "
            "results in aircraft damage."
        )
        st.caption("Primary binary prediction task.")

with severity_col:
    with st.container(border=True):
        st.markdown("#### Damage severity")
        st.write(
            "Estimates the probability of the more severe damage outcome "
            "within the severity model's defined conditional scope."
        )
        st.caption("Conditional severity modelling.")

with component_col:
    with st.container(border=True):
        st.markdown("#### Affected components")
        st.write(
            "Estimates probabilities of damage to specific aircraft "
            "areas or components."
        )
        st.caption("Component-level damage modelling.")


# ---------------------------------------------------------------------
# Operational simulation overview
# ---------------------------------------------------------------------

section_divider()

section_header(
    "Operational what-if simulation",
    (
        "The simulation layer combines supported scenario inputs with "
        "historical donor records and the trained predictive models."
    ),
)

with st.container(border=True):
    simulation_col, trial_col = st.columns(
        [3, 1],
        gap="medium",
    )

    with simulation_col:
        st.markdown("#### From scenario to simulated outcomes")

        st.write(
            "Users define operational conditions such as aircraft class, "
            "aircraft mass group, season, phase of flight, and airport. "
            "Optional wildlife and aircraft details may be supplied when "
            "appropriate or sampled from historically supported records."
        )

        st.write(
            "The Monte Carlo engine repeatedly evaluates compatible "
            "conditions to summarize damage, severity, and component-risk "
            "outputs while preserving the scenario's historical support."
        )

    with trial_col:
        st.metric(
            "Default simulation",
            "10,000 trials",
            help=(
                "Default number of Monte Carlo trials used by the "
                "operational simulation."
            ),
        )


# ---------------------------------------------------------------------
# Analytical workflow
# ---------------------------------------------------------------------

section_divider()

section_header(
    "Analytical workflow",
    (
        "The dashboard is the presentation layer of the modelling workflow "
        "developed across the project notebooks."
    ),
)

workflow = [
    (
        "1. Historical data",
        "FAA wildlife-strike records are cleaned, structured, and explored.",
    ),
    (
        "2. Predictive modelling",
        "Damage, severity, and component models are trained.",
    ),
    (
        "3. Validation",
        "Performance, thresholds, and probability calibration are assessed.",
    ),
    (
        "4. Explainability",
        "Model behaviour and major predictors are investigated.",
    ),
    (
        "5. Simulation",
        "Supported scenarios are evaluated through Monte Carlo trials.",
    ),
]

workflow_cols = st.columns(
    len(workflow),
    gap="small",
)

for column, (title, text) in zip(workflow_cols, workflow):
    with column:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.caption(text)


# ---------------------------------------------------------------------
# Interpretation and scope
# ---------------------------------------------------------------------

section_divider()

section_header(
    "How to interpret this dashboard",
    "Key scope distinctions that apply across the dashboard.",
)

with st.expander("Methodology and interpretation notes"):
    st.markdown(
        """
        **Historical exploration:** Descriptive sections use the complete
        analytical period from **1990 through 2024**.

        **Operational simulation:** Simulation scenarios use historical donor
        and support information from **1990 through 2021**. The 2022–2024
        period is intentionally excluded from that reference population to
        preserve the temporal evaluation design used during model development.

        **Observed versus predicted risk:** Historical damage rates describe
        what was reported in the dataset. They are not the same as the
        model-generated probabilities presented in the damage-risk and
        simulation pages.

        **Reporting context:** FAA wildlife-strike records represent reported
        events. Trends should therefore be interpreted as trends in the
        recorded dataset rather than as a direct measurement of every wildlife
        strike that occurred in the United States.
        """
    )
