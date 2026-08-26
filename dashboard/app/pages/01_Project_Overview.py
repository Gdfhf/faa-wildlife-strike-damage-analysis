import pandas as pd
import streamlit as st

from src.data.loaders import (
    load_historical_data,
    load_overview_summary,
)


st.title("Project Overview")

st.markdown(
    """
    This page provides a high-level view of the FAA wildlife strike
    dataset used in the project. It summarizes the scale of the data,
    historical reporting patterns, and observed aircraft damage before
    moving into the predictive and simulation sections of the dashboard.
    """
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
# KPI cards
# ---------------------------------------------------------------------

st.subheader("Dataset Summary")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Reported Strikes",
        f"{summary['n_records']:,}",
    )

with col2:
    st.metric(
        "Historical Period",
        f"{summary['start_year']}–{summary['end_year']}",
    )

with col3:
    st.metric(
        "Airports",
        f"{summary['n_airports']:,}",
    )

with col4:
    st.metric(
        "Wildlife Species",
        f"{summary['n_species']:,}",
    )


col5, col6 = st.columns(2)

with col5:
    st.metric(
        "Records with Damage",
        f"{summary['n_damaged']:,}",
    )

with col6:
    st.metric(
        "Historical Damage Rate",
        f"{summary['damage_rate']:.2%}",
    )


st.divider()


# ---------------------------------------------------------------------
# Annual strike volume
# ---------------------------------------------------------------------

st.subheader("Reported Wildlife Strikes Over Time")

if "INCIDENT_YEAR" in df.columns:

    annual_strikes = (
        df.groupby("INCIDENT_YEAR")
        .size()
        .rename("Reported Strikes")
        .reset_index()
        .sort_values("INCIDENT_YEAR")
    )

    st.line_chart(
        annual_strikes,
        x="INCIDENT_YEAR",
        y="Reported Strikes",
        use_container_width=True,
    )

    st.caption(
        "Annual counts represent reported wildlife strike records in "
        "the 1990–2024 analytical dataset. Changes over time can reflect "
        "both underlying strike activity and changes in reporting."
    )

else:
    st.warning(
        "INCIDENT_YEAR is not available in the historical dashboard artifact."
    )


# ---------------------------------------------------------------------
# Historical damage rate
# ---------------------------------------------------------------------

st.subheader("Observed Damage Rate Over Time")

if (
    "INCIDENT_YEAR" in df.columns
    and "INDICATED_DAMAGE" in df.columns
):

    damage = df[
        ["INCIDENT_YEAR", "INDICATED_DAMAGE"]
    ].copy()

    # Make the calculation tolerant of either numeric/bool or
    # common string representations.
    if pd.api.types.is_numeric_dtype(
        damage["INDICATED_DAMAGE"]
    ):
        damage["damage_flag"] = (
            damage["INDICATED_DAMAGE"]
            .fillna(0)
            .astype(float)
        )

    elif pd.api.types.is_bool_dtype(
        damage["INDICATED_DAMAGE"]
    ):
        damage["damage_flag"] = (
            damage["INDICATED_DAMAGE"]
            .fillna(False)
            .astype(int)
        )

    else:
        damage["damage_flag"] = (
            damage["INDICATED_DAMAGE"]
            .astype(str)
            .str.strip()
            .str.upper()
            .isin(
                [
                    "1",
                    "TRUE",
                    "T",
                    "YES",
                    "Y",
                    "DAMAGE",
                    "DAMAGED",
                ]
            )
            .astype(int)
        )

    annual_damage = (
        damage.groupby("INCIDENT_YEAR")["damage_flag"]
        .mean()
        .mul(100)
        .rename("Damage Rate (%)")
        .reset_index()
        .sort_values("INCIDENT_YEAR")
    )

    st.line_chart(
        annual_damage,
        x="INCIDENT_YEAR",
        y="Damage Rate (%)",
        use_container_width=True,
    )

    st.caption(
        "Damage rate is the percentage of reported wildlife strikes "
        "associated with indicated aircraft damage in each year."
    )

else:
    st.warning(
        "The fields required for the historical damage-rate chart "
        "are not available."
    )


st.divider()


# ---------------------------------------------------------------------
# Top wildlife and airports
# ---------------------------------------------------------------------

left, right = st.columns(2)


with left:
    st.subheader("Most Frequently Reported Wildlife")

    wildlife_column = None

    if "SPECIES" in df.columns:
        wildlife_column = "SPECIES"

    elif "WILDLIFE_TYPE" in df.columns:
        wildlife_column = "WILDLIFE_TYPE"

    if wildlife_column is not None:

        top_wildlife = (
            df[wildlife_column]
            .dropna()
            .astype(str)
            .value_counts()
            .head(10)
            .rename("Reported Strikes")
            .reset_index()
        )

        top_wildlife.columns = [
            "Wildlife",
            "Reported Strikes",
        ]

        st.bar_chart(
            top_wildlife,
            x="Wildlife",
            y="Reported Strikes",
            use_container_width=True,
        )

    else:
        st.warning(
            "No wildlife field is available in the historical artifact."
        )


with right:
    st.subheader("Airports with the Most Reported Strikes")

    airport_column = None

    if "AIRPORT" in df.columns:
        airport_column = "AIRPORT"

    elif "AIRPORT_ID" in df.columns:
        airport_column = "AIRPORT_ID"

    if airport_column is not None:

        top_airports = (
            df[airport_column]
            .dropna()
            .astype(str)
            .value_counts()
            .head(10)
            .rename("Reported Strikes")
            .reset_index()
        )

        top_airports.columns = [
            "Airport",
            "Reported Strikes",
        ]

        st.bar_chart(
            top_airports,
            x="Airport",
            y="Reported Strikes",
            use_container_width=True,
        )

    else:
        st.warning(
            "No airport field is available in the historical artifact."
        )


st.divider()


# ---------------------------------------------------------------------
# Methodology context
# ---------------------------------------------------------------------

st.subheader("How to Interpret This Dashboard")

st.markdown(
    """
    **Historical exploration:** The descriptive sections use the complete
    analytical period from **1990 through 2024**.

    **Operational simulation:** Simulation scenarios use historical donor
    and support information from **1990 through 2021**. The 2022–2024
    period is intentionally excluded from that reference population to
    preserve the temporal evaluation design used during model development.

    **Observed versus predicted risk:** Historical damage rates shown on
    this page describe what was reported in the dataset. They are not the
    same as the model-generated probabilities presented in the damage-risk
    and simulation pages.

    **Reporting context:** FAA wildlife strike records represent reported
    events. Trends should therefore be interpreted as trends in the
    recorded dataset rather than as a direct measurement of every wildlife
    strike that occurred in the United States.
    """
)