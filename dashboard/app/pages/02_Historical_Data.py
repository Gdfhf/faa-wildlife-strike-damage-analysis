"""Interactive historical wildlife-strike explorer."""

from __future__ import annotations

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
from src.data.loaders import load_historical_data
from src.utils.labels import (
    build_airport_labels,
    format_aircraft_class
)


# =====================================================================
# Helpers
# =====================================================================

def clean_values(data: pd.DataFrame, column: str) -> list[str]:
    """Return sorted non-null, non-empty string values."""
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


def apply_multiselect_filter(
    data: pd.DataFrame,
    column: str,
    selected: list[str],
) -> pd.DataFrame:
    """Filter only when one or more values are explicitly selected."""
    if not selected or column not in data.columns:
        return data

    normalized = data[column].astype("string").str.strip()
    return data.loc[normalized.isin(selected)]


def safe_rate(numerator: float, denominator: float) -> float:
    """Return a valid proportion when the denominator is positive."""
    if denominator <= 0:
        return 0.0
    return numerator / denominator


def format_component_name(column: str) -> str:
    """Return presentation-friendly component labels."""
    labels = {
        "DAM_RAD": "Radome",
        "DAM_WINDSHLD": "Windshield",
        "DAM_NOSE": "Nose",
        "DAM_ENG1": "Engine 1",
        "DAM_ENG2": "Engine 2",
        "DAM_ENG3": "Engine 3",
        "DAM_ENG4": "Engine 4",
        "DAM_PROP": "Propeller",
        "DAM_WING_ROT": "Wing / Rotor",
        "DAM_FUSE": "Fuselage",
        "DAM_LG": "Landing Gear",
        "DAM_TAIL": "Tail",
        "DAM_LGHTS": "Lights",
        "DAM_OTHER": "Other",
    }
    return labels.get(column, column)


def style_figure(fig, *, hovermode: str = "closest"):
    """Apply the shared Plotly layout and chart-specific hover behavior."""
    fig = apply_chart_layout(fig)
    fig.update_layout(hovermode=hovermode)
    return fig


PLOTLY_CONFIG = {
    "displaylogo": False,
    "responsive": True,
}



# =====================================================================
# Page introduction
# =====================================================================

page_header(
    "Historical Wildlife Strike Explorer",
    (
        "Explore reported wildlife strikes from the project's 1990–2024 "
        "analytical dataset and examine how historical patterns change "
        "under different operational and wildlife filters."
    ),
)

st.caption(
    "All statistics on this page are historical observations among "
    "reported strikes. They are not model-generated probabilities or "
    "exposure-adjusted flight risk."
)


# =====================================================================
# Load historical artifact
# =====================================================================

try:
    historical_data = load_historical_data()

except Exception as exc:
    st.error(
        "Historical dashboard data could not be loaded. "
        f"Details: {exc}"
    )
    st.stop()


if historical_data.empty:
    st.warning("The historical explorer artifact contains no records.")
    st.stop()

airport_labels = build_airport_labels(historical_data)

# =====================================================================
# Filters
# =====================================================================

section_divider()

section_header(
    "Filter historical records",
    (
        "Start with time and operational context, then open the additional "
        "filters only when a more specific comparison is needed."
    ),
)

year_series = pd.to_numeric(
    historical_data["INCIDENT_YEAR"],
    errors="coerce",
)

min_year = int(year_series.min())
max_year = int(year_series.max())

year_range = st.slider(
    "Incident year",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year),
)

filter_col1, filter_col2 = st.columns(
    2,
    gap="medium",
)

with filter_col1:
    faa_regions = st.multiselect(
        "FAA region",
        options=clean_values(historical_data, "FAAREGION"),
    )

    seasons = st.multiselect(
        "Season",
        options=clean_values(historical_data, "SEASON"),
    )

with filter_col2:
    airports = st.multiselect(
        "Airport",
        options=clean_values(
            historical_data,
            "AIRPORT_ID",
        ),
        format_func=lambda airport_id: airport_labels.get(
            airport_id,
            airport_id,
        ),
    )

    phases = st.multiselect(
        "Phase of flight",
        options=clean_values(historical_data, "PHASE_OF_FLIGHT"),
    )

with st.expander("Aircraft and wildlife filters", expanded=False):
    aircraft_col, wildlife_col = st.columns(
        2,
        gap="medium",
    )

    with aircraft_col:
        aircraft_classes = st.multiselect(
            "Aircraft class",
            options=clean_values(
                historical_data,
                "AC_CLASS",
            ),
            format_func=format_aircraft_class,
        )

        mass_groups = st.multiselect(
            "Aircraft mass group",
            options=clean_values(historical_data, "AC_MASS_GROUP"),
        )

    with wildlife_col:
        wildlife_types = st.multiselect(
            "Wildlife type",
            options=clean_values(historical_data, "WILDLIFE_TYPE"),
        )

        wildlife_sizes = st.multiselect(
            "Wildlife size",
            options=clean_values(historical_data, "SIZE"),
        )


filtered = historical_data.loc[
    year_series.between(year_range[0], year_range[1])
].copy()

filtered = apply_multiselect_filter(filtered, "FAAREGION", faa_regions)
filtered = apply_multiselect_filter(filtered, "AIRPORT_ID", airports)
filtered = apply_multiselect_filter(filtered, "SEASON", seasons)
filtered = apply_multiselect_filter(filtered, "PHASE_OF_FLIGHT", phases)
filtered = apply_multiselect_filter(filtered, "AC_CLASS", aircraft_classes)
filtered = apply_multiselect_filter(filtered, "AC_MASS_GROUP", mass_groups)
filtered = apply_multiselect_filter(filtered, "WILDLIFE_TYPE", wildlife_types)
filtered = apply_multiselect_filter(filtered, "SIZE", wildlife_sizes)


if filtered.empty:
    st.warning(
        "No historical records match the current filters. "
        "Broaden one or more selections."
    )
    st.stop()


# =====================================================================
# Filtered KPI summary
# =====================================================================

section_divider()

section_header(
    "Filtered historical summary",
    "These metrics update with the selections above.",
)

n_records = len(filtered)

damage = pd.to_numeric(
    filtered["INDICATED_DAMAGE"],
    errors="coerce",
).fillna(0)

n_damaged = int(damage.sum())
damage_rate = safe_rate(n_damaged, n_records)

airport_values = (
    filtered["AIRPORT_ID"]
    .dropna()
    .astype(str)
    .str.strip()
)
n_airports = int(
    airport_values[airport_values != ""].nunique()
)

species_values = (
    filtered["SPECIES"]
    .dropna()
    .astype(str)
    .str.strip()
)
n_species = int(
    species_values[species_values != ""].nunique()
)

metric_row(
    [
        (
            "Reported strikes",
            f"{n_records:,}",
            "Reported wildlife-strike records matching the current filters.",
        ),
        (
            "Damaging strikes",
            f"{n_damaged:,}",
            "Filtered records with indicated aircraft damage.",
        ),
        (
            "Observed damage rate",
            f"{damage_rate:.2%}",
            (
                "Share of filtered reported strikes with indicated damage. "
                "This is not a probability per flight."
            ),
        ),
        (
            "Airports represented",
            f"{n_airports:,}",
            "Distinct airports represented by the current filtered records.",
        ),
    ]
)

st.caption(
    f"{n_species:,} species/categories are represented in the current "
    "selection. The observed damage rate is conditional on reported strikes; "
    "flight-exposure denominators are unavailable."
)


# =====================================================================
# Historical trends
# =====================================================================

section_divider()

section_header(
    "Historical trends",
    (
        "Compare reporting volume with the observed share of reported "
        "strikes associated with aircraft damage."
    ),
)

trend = (
    filtered.assign(
        INCIDENT_YEAR=pd.to_numeric(
            filtered["INCIDENT_YEAR"],
            errors="coerce",
        ),
        INDICATED_DAMAGE=pd.to_numeric(
            filtered["INDICATED_DAMAGE"],
            errors="coerce",
        ).fillna(0),
    )
    .dropna(subset=["INCIDENT_YEAR"])
    .groupby("INCIDENT_YEAR", as_index=False)
    .agg(
        Reported_Strikes=("INDICATED_DAMAGE", "size"),
        Damaged_Strikes=("INDICATED_DAMAGE", "sum"),
    )
)

trend["Observed_Damage_Rate"] = (
    trend["Damaged_Strikes"] / trend["Reported_Strikes"] * 100
)

trend["INCIDENT_YEAR"] = trend["INCIDENT_YEAR"].astype(int)

trend_col1, trend_col2 = st.columns(
    2,
    gap="medium",
)

with trend_col1:
    with st.container(border=True):
        st.markdown("#### Reported strikes by year")

        strike_fig = px.line(
            trend,
            x="INCIDENT_YEAR",
            y="Reported_Strikes",
            labels={
                "INCIDENT_YEAR": "Year",
                "Reported_Strikes": "Reported strikes",
            },
        )
        strike_fig = style_figure(
            strike_fig,
            hovermode="x unified",
        )

        st.plotly_chart(
            strike_fig,
            use_container_width=True,
            config=PLOTLY_CONFIG,
        )

with trend_col2:
    with st.container(border=True):
        st.markdown("#### Observed damage rate by year")

        rate_fig = px.line(
            trend,
            x="INCIDENT_YEAR",
            y="Observed_Damage_Rate",
            labels={
                "INCIDENT_YEAR": "Year",
                "Observed_Damage_Rate": "Damage rate (%)",
            },
        )
        rate_fig.update_traces(
            hovertemplate="%{y:.2f}%<extra></extra>",
        )
        rate_fig = style_figure(
            rate_fig,
            hovermode="x unified",
        )

        st.plotly_chart(
            rate_fig,
            use_container_width=True,
            config=PLOTLY_CONFIG,
        )

st.caption(
    "Changes over time can reflect operational conditions, reporting "
    "practices, and data completeness. The two charts should therefore "
    "be interpreted together rather than as exposure-adjusted risk."
)


# =====================================================================
# Operational and wildlife patterns
# =====================================================================

section_divider()

section_header(
    "Operational and wildlife patterns",
    (
        "Compare where reported strikes occur in the flight profile and "
        "how observed damage differs across wildlife-size categories."
    ),
)

pattern_col1, pattern_col2 = st.columns(
    2,
    gap="medium",
)

with pattern_col1:
    with st.container(border=True):
        st.markdown("#### Phase of flight")

        phase_summary = (
            filtered.assign(
                INDICATED_DAMAGE=pd.to_numeric(
                    filtered["INDICATED_DAMAGE"],
                    errors="coerce",
                ).fillna(0)
            )
            .dropna(subset=["PHASE_OF_FLIGHT"])
            .groupby("PHASE_OF_FLIGHT", as_index=False)
            .agg(
                Reported_Strikes=("INDICATED_DAMAGE", "size"),
                Damaged_Strikes=("INDICATED_DAMAGE", "sum"),
            )
        )

        phase_display = (
            phase_summary
            .sort_values("Reported_Strikes", ascending=True)
            .tail(12)
        )

        phase_fig = px.bar(
            phase_display,
            x="Reported_Strikes",
            y="PHASE_OF_FLIGHT",
            orientation="h",
            labels={
                "Reported_Strikes": "Reported strikes",
                "PHASE_OF_FLIGHT": "Phase of flight",
            },
        )
        phase_fig = style_figure(phase_fig)

        st.plotly_chart(
            phase_fig,
            use_container_width=True,
            config=PLOTLY_CONFIG,
        )

with pattern_col2:
    with st.container(border=True):
        st.markdown("#### Wildlife size")

        size_summary = (
            filtered.assign(
                INDICATED_DAMAGE=pd.to_numeric(
                    filtered["INDICATED_DAMAGE"],
                    errors="coerce",
                ).fillna(0)
            )
            .dropna(subset=["SIZE"])
            .groupby("SIZE", as_index=False)
            .agg(
                Reported_Strikes=("INDICATED_DAMAGE", "size"),
                Damaged_Strikes=("INDICATED_DAMAGE", "sum"),
            )
        )

        size_summary["Observed_Damage_Rate"] = (
            size_summary["Damaged_Strikes"]
            / size_summary["Reported_Strikes"]
            * 100
        )

        size_summary = size_summary.sort_values(
            "Observed_Damage_Rate",
            ascending=False,
        )

        size_fig = px.bar(
            size_summary,
            x="SIZE",
            y="Observed_Damage_Rate",
            labels={
                "SIZE": "Wildlife size",
                "Observed_Damage_Rate": "Observed damage rate (%)",
            },
        )
        size_fig.update_traces(
            hovertemplate="%{x}<br>%{y:.2f}%<extra></extra>",
        )
        size_fig = style_figure(size_fig)

        st.plotly_chart(
            size_fig,
            use_container_width=True,
            config=PLOTLY_CONFIG,
        )


# =====================================================================
# Most frequently reported wildlife and airports
# =====================================================================

section_divider()

section_header(
    "Most frequently reported wildlife and airports",
    (
        "These rankings describe report volume only. They do not account "
        "for differences in traffic or other exposure."
    ),
)

ranking_col1, ranking_col2 = st.columns(
    2,
    gap="medium",
)

with ranking_col1:
    with st.container(border=True):
        st.markdown("#### Top species")

        species_counts = (
            filtered["SPECIES"]
            .dropna()
            .astype(str)
            .str.strip()
        )
        species_counts = species_counts[
            species_counts != ""
        ]

        species_counts = (
            species_counts
            .value_counts()
            .head(15)
            .rename_axis("Species")
            .reset_index(name="Reported_Strikes")
            .sort_values("Reported_Strikes", ascending=True)
        )

        species_fig = px.bar(
            species_counts,
            x="Reported_Strikes",
            y="Species",
            orientation="h",
            labels={
                "Reported_Strikes": "Reported strikes",
                "Species": "Species",
            },
        )
        species_fig = style_figure(species_fig)

        st.plotly_chart(
            species_fig,
            use_container_width=True,
            config=PLOTLY_CONFIG,
        )

with ranking_col2:
    with st.container(border=True):
        st.markdown("#### Top airports by reports")

        # Keep the chart axis compact by using only AIRPORT_ID.
        # The full airport name is retained for the hover tooltip.
        airport_rank = filtered[
            ["AIRPORT_ID", "AIRPORT"]
        ].copy()

        airport_rank["AIRPORT_ID"] = (
            airport_rank["AIRPORT_ID"]
            .astype("string")
            .fillna("")
            .str.strip()
        )

        airport_rank["AIRPORT"] = (
            airport_rank["AIRPORT"]
            .astype("string")
            .fillna("")
            .str.strip()
        )

        airport_rank = airport_rank[
            airport_rank["AIRPORT_ID"] != ""
        ]

        # Determine a representative airport name for each airport ID.
        airport_names = (
            airport_rank[
                airport_rank["AIRPORT"] != ""
            ]
            .groupby("AIRPORT_ID")["AIRPORT"]
            .agg(
                lambda values: (
                    values.mode().iloc[0]
                    if not values.mode().empty
                    else values.iloc[0]
                )
            )
        )

        # Count reports by airport ID.
        airport_counts = (
            airport_rank["AIRPORT_ID"]
            .value_counts()
            .head(15)
            .rename_axis("Airport ID")
            .reset_index(name="Reported_Strikes")
        )

        # Attach the readable name only for hover information.
        airport_counts["Airport Name"] = (
            airport_counts["Airport ID"]
            .map(airport_names)
            .fillna("Name unavailable")
        )

        # Ascending order makes the largest horizontal bar appear at top.
        airport_counts = airport_counts.sort_values(
            "Reported_Strikes",
            ascending=True,
        )

        airport_fig = px.bar(
            airport_counts,
            x="Reported_Strikes",
            y="Airport ID",
            orientation="h",
            custom_data=["Airport Name"],
            labels={
                "Reported_Strikes": "Reported strikes",
                "Airport ID": "Airport",
            },
        )

        airport_fig.update_traces(
            hovertemplate=(
                "<b>%{y}</b><br>"
                "%{customdata[0]}<br>"
                "Reported strikes: %{x:,}"
                "<extra></extra>"
            ),
        )

        airport_fig = style_figure(
            airport_fig
        )

        st.plotly_chart(
            airport_fig,
            use_container_width=True,
            config=PLOTLY_CONFIG,
        )

st.caption(
    "High report counts do not necessarily indicate higher underlying "
    "strike risk because airport and flight-exposure denominators are "
    "not available in this analytical dataset."
)


# =====================================================================
# Damage severity
# =====================================================================

section_divider()

section_header(
    "Damage severity among damaged strikes",
    (
        "This section is conditional on aircraft damage having already "
        "been indicated in the historical record."
    ),
)

damaged_records = filtered.loc[
    pd.to_numeric(
        filtered["INDICATED_DAMAGE"],
        errors="coerce",
    ).fillna(0).eq(1)
].copy()

if damaged_records.empty:
    st.info(
        "No damaged strikes are present under the current filters, "
        "so severity and component summaries are unavailable."
    )

else:
    severity = (
        damaged_records["DAMAGE_LEVEL"]
        .dropna()
        .astype(str)
        .str.strip()
    )
    severity = severity[severity != ""]

    if severity.empty:
        st.info(
            "Damage occurred in the filtered records, but no usable "
            "damage-level values are available."
        )

    else:
        severity_counts = (
            severity
            .value_counts()
            .rename_axis("Damage level")
            .reset_index(name="Damaged_Strikes")
        )

        severity_fig = px.bar(
            severity_counts,
            x="Damage level",
            y="Damaged_Strikes",
            labels={
                "Damage level": "Damage level",
                "Damaged_Strikes": "Damaged strikes",
            },
        )
        severity_fig = style_figure(severity_fig)

        st.plotly_chart(
            severity_fig,
            use_container_width=True,
            config=PLOTLY_CONFIG,
        )

        st.caption(
            "Severity is shown only among records where aircraft damage "
            "was indicated and is therefore conditional on damage."
        )


# =====================================================================
# Component damage
# =====================================================================

section_divider()

section_header(
    "Reported component damage",
    (
        "Component indicators describe which aircraft areas were reported "
        "as damaged among the filtered damaged-strike records."
    ),
)

component_columns = [
    "DAM_RAD",
    "DAM_WINDSHLD",
    "DAM_NOSE",
    "DAM_ENG1",
    "DAM_ENG2",
    "DAM_ENG3",
    "DAM_ENG4",
    "DAM_PROP",
    "DAM_WING_ROT",
    "DAM_FUSE",
    "DAM_LG",
    "DAM_TAIL",
    "DAM_LGHTS",
    "DAM_OTHER",
]

available_components = [
    column
    for column in component_columns
    if column in damaged_records.columns
]

if damaged_records.empty or not available_components:
    st.info(
        "Component-damage information is unavailable under the current "
        "filters."
    )

else:
    component_rows = []

    for column in available_components:
        count = int(
            pd.to_numeric(
                damaged_records[column],
                errors="coerce",
            )
            .fillna(0)
            .sum()
        )

        component_rows.append(
            {
                "Component": format_component_name(column),
                "Damaged Records": count,
                "Rate Among Damaged Strikes": (
                    safe_rate(
                        count,
                        len(damaged_records),
                    )
                    * 100
                ),
            }
        )

    component_df = (
        pd.DataFrame(component_rows)
        .sort_values(
            "Rate Among Damaged Strikes",
            ascending=True,
        )
    )

    component_fig = px.bar(
        component_df,
        x="Rate Among Damaged Strikes",
        y="Component",
        orientation="h",
        labels={
            "Rate Among Damaged Strikes": "Rate among damaged strikes (%)",
            "Component": "Component",
        },
    )
    component_fig.update_traces(
        hovertemplate="%{y}<br>%{x:.2f}%<extra></extra>",
    )
    component_fig = style_figure(component_fig)

    st.plotly_chart(
        component_fig,
        use_container_width=True,
        config=PLOTLY_CONFIG,
    )

    with st.expander("View component summary table", expanded=False):
        component_display = component_df.copy()

        component_display["Rate Among Damaged Strikes"] = (
            component_display["Rate Among Damaged Strikes"]
            .map(lambda value: f"{value:.2f}%")
        )

        st.dataframe(
            component_display.sort_values(
                "Damaged Records",
                ascending=False,
            ),
            use_container_width=True,
            hide_index=True,
        )

    st.caption(
        "Component indicators are not mutually exclusive. A single "
        "damaged strike can therefore contribute to more than one "
        "component category."
    )


# =====================================================================
# Optional record preview
# =====================================================================

section_divider()

with st.expander("Preview filtered records", expanded=False):

    preview_columns = [
        "INCIDENT_DATE",
        "INCIDENT_YEAR",
        "AIRPORT_ID",
        "AIRPORT",
        "FAAREGION",
        "AC_CLASS",
        "AC_MASS_GROUP",
        "PHASE_OF_FLIGHT",
        "SPECIES",
        "WILDLIFE_TYPE",
        "SIZE",
        "INDICATED_DAMAGE",
        "DAMAGE_LEVEL",
    ]

    preview_columns = [
        column
        for column in preview_columns
        if column in filtered.columns
    ]

    st.dataframe(
        filtered[preview_columns].head(500),
        use_container_width=True,
        hide_index=True,
    )

    if len(filtered) > 500:
        st.caption(
            f"Showing the first 500 of {len(filtered):,} filtered records."
        )
