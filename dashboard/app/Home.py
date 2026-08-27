import streamlit as st

from dashboard.components.layout import (
    page_header,
    section_divider,
    section_header,
)


# =====================================================================
# Page header
# =====================================================================

page_header(
    "FAA Wildlife Strike Damage Analysis",
    (
        "Explore reported FAA wildlife-strike patterns, review the fitted "
        "damage-risk system, and run historically grounded what-if simulations."
    ),
)

st.markdown(
    """
    This dashboard combines historical analysis, predictive modeling,
    explainability, and Monte Carlo simulation into one interactive workflow.

    If you are new to the project, start with the overview and historical
    pages before moving into the simulation tools.
    """
)


# =====================================================================
# Main navigation
# =====================================================================

section_divider()

section_header(
    "Choose a path",
    (
        "Use the analytical pages to understand the evidence, or go directly "
        "to the operational tools if you are already familiar with the project."
    ),
)

col1, col2 = st.columns(
    2,
    gap="large",
)


with col1:
    with st.container(border=True):

        st.markdown("### Historical analysis")

        st.markdown(
            """
            Explore reported FAA wildlife-strike patterns across the
            **1990–2024 analytical dataset**, including temporal patterns,
            airports, wildlife characteristics, and observed aircraft damage.
            """
        )

        st.page_link(
            "app/pages/01_Project_Overview.py",
            label="1. Project Overview →",
            icon="📋",
        )

        st.page_link(
            "app/pages/02_Historical_Data.py",
            label="2. Historical Data →",
            icon="📊",
        )

        st.page_link(
            "app/pages/03_Damage_Risk.py",
            label="3. Damage Risk & Model Insights →",
            icon="🧠",
        )


with col2:
    with st.container(border=True):

        st.markdown("### Operational simulation")

        st.markdown(
            """
            Construct supported what-if scenarios and estimate modeled
            aircraft damage, severity, and component-level outcomes using
            the project's trained probability systems and Monte Carlo
            simulation.
            """
        )

        st.page_link(
            "app/pages/04_Monte_Carlo_Simulation.py",
            label="4. Monte Carlo Simulation →",
            icon="🎲",
        )

        st.page_link(
            "app/pages/05_Scenario_Comparison.py",
            label="5. Scenario Comparison →",
            icon="⚖️",
        )


# =====================================================================
# Interpretation guide
# =====================================================================

section_divider()

section_header(
    "Need help interpreting the results?",
    (
        "The guide explains historical percentages, modeled probabilities, "
        "simulation outputs, support, counterfactual overrides, and common "
        "interpretation mistakes."
    ),
)

st.page_link(
    "app/pages/06_How_to_Read_the_Dashboard.py",
    label="6. How to Read the Dashboard →",
    icon="📖",
)


# =====================================================================
# Temporal design note
# =====================================================================

st.info(
    "The historical explorer covers 1990–2024. The Monte Carlo donor and "
    "support population uses 1990–2021 only, while 2022–2024 was preserved "
    "as the locked final-test period."
)


# =====================================================================
# Final scope reminder
# =====================================================================

with st.expander(
    "What this dashboard is — and is not",
    expanded=False,
):
    st.markdown(
        """
        This dashboard is a **scenario-analysis and decision-support
        prototype** based on historical FAA wildlife-strike reports.

        It can help users:

        - inspect reported historical patterns;
        - understand the fitted damage-risk system;
        - compare supported what-if scenarios;
        - explore modeled damage, severity, and component outcomes.

        It should **not** be interpreted as:

        - the probability that a flight will experience a wildlife strike;
        - a real-time collision predictor;
        - a causal safety model;
        - an operational aviation decision rule.
        """
    )