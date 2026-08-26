import pandas as pd
import streamlit as st

from src.data.loaders import load_historical_data


# =====================================================================
# Page configuration
# =====================================================================

st.title("Historical Wildlife Strike Explorer")

st.markdown(
    """
    Explore reported wildlife strikes from the project's 1990–2024
    analytical dataset. All statistics on this page are **historical
    observations among reported strikes**; they are not modeled risk
    probabilities and should not be interpreted as exposure-adjusted
    airport or flight risk.
    """
)


# =====================================================================
# Helpers
# =====================================================================

def clean_values(data, column):
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


def apply_multiselect_filter(data, column, selected):
    """Filter only when one or more values are explicitly selected."""
    if not selected or column not in data.columns:
        return data

    normalized = data[column].astype("string").str.strip()
    return data.loc[normalized.isin(selected)]


def safe_rate(numerator, denominator):
    """Return a valid proportion when the denominator is positive."""
    if denominator <= 0:
        return 0.0
    return numerator / denominator


def format_component_name(column):
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


# =====================================================================
# Filters
# =====================================================================

st.subheader("1. Filter Historical Records")

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

with st.expander("Additional filters", expanded=True):

    col1, col2 = st.columns(2)

    with col1:
        faa_regions = st.multiselect(
            "FAA Region",
            options=clean_values(historical_data, "FAAREGION"),
        )

        airports = st.multiselect(
            "Airport ID",
            options=clean_values(historical_data, "AIRPORT_ID"),
        )

        aircraft_classes = st.multiselect(
            "Aircraft Class",
            options=clean_values(historical_data, "AC_CLASS"),
        )

        mass_groups = st.multiselect(
            "Aircraft Mass Group",
            options=clean_values(historical_data, "AC_MASS_GROUP"),
        )

    with col2:
        seasons = st.multiselect(
            "Season",
            options=clean_values(historical_data, "SEASON"),
        )

        phases = st.multiselect(
            "Phase of Flight",
            options=clean_values(historical_data, "PHASE_OF_FLIGHT"),
        )

        wildlife_types = st.multiselect(
            "Wildlife Type",
            options=clean_values(historical_data, "WILDLIFE_TYPE"),
        )

        wildlife_sizes = st.multiselect(
            "Wildlife Size",
            options=clean_values(historical_data, "SIZE"),
        )


filtered = historical_data.loc[
    year_series.between(year_range[0], year_range[1])
].copy()

filtered = apply_multiselect_filter(filtered, "FAAREGION", faa_regions)
filtered = apply_multiselect_filter(filtered, "AIRPORT_ID", airports)
filtered = apply_multiselect_filter(filtered, "AC_CLASS", aircraft_classes)
filtered = apply_multiselect_filter(filtered, "AC_MASS_GROUP", mass_groups)
filtered = apply_multiselect_filter(filtered, "SEASON", seasons)
filtered = apply_multiselect_filter(filtered, "PHASE_OF_FLIGHT", phases)
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

st.subheader("2. Filtered Historical Summary")

n_records = len(filtered)

damage = pd.to_numeric(
    filtered["INDICATED_DAMAGE"],
    errors="coerce",
).fillna(0)

n_damaged = int(damage.sum())
damage_rate = safe_rate(n_damaged, n_records)

n_airports = (
    filtered["AIRPORT_ID"]
    .dropna()
    .astype(str)
    .str.strip()
)
n_airports = int(n_airports[n_airports != ""].nunique())

n_species = (
    filtered["SPECIES"]
    .dropna()
    .astype(str)
    .str.strip()
)
n_species = int(n_species[n_species != ""].nunique())

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Reported Strikes", f"{n_records:,}")

with col2:
    st.metric("Damaged Strikes", f"{n_damaged:,}")

with col3:
    st.metric("Observed Damage Rate", f"{damage_rate:.2%}")

with col4:
    st.metric("Airports Represented", f"{n_airports:,}")

with col5:
    st.metric("Species Represented", f"{n_species:,}")


st.caption(
    "The damage rate is the proportion of filtered reported strikes "
    "with indicated aircraft damage. It is not a strike probability "
    "per flight because flight-exposure denominators are unavailable."
)


# =====================================================================
# Time trends
# =====================================================================

st.subheader("3. Historical Trends")

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
    trend["Damaged_Strikes"] / trend["Reported_Strikes"]
)

trend["INCIDENT_YEAR"] = trend["INCIDENT_YEAR"].astype(int)


col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Reported Strikes by Year")

    strike_chart = (
        trend[["INCIDENT_YEAR", "Reported_Strikes"]]
        .set_index("INCIDENT_YEAR")
    )

    st.line_chart(
        strike_chart,
        use_container_width=True,
    )

with col2:
    st.markdown("#### Observed Damage Rate by Year")

    rate_chart = (
        trend[["INCIDENT_YEAR", "Observed_Damage_Rate"]]
        .set_index("INCIDENT_YEAR")
        .mul(100)
    )

    st.line_chart(
        rate_chart,
        use_container_width=True,
    )

st.caption(
    "Changes over time may reflect both operational conditions and "
    "changes in wildlife-strike reporting practices or data completeness."
)


# =====================================================================
# Operational and wildlife patterns
# =====================================================================

st.subheader("4. Operational and Wildlife Patterns")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Phase of Flight")

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

    phase_summary["Observed Damage Rate"] = (
        phase_summary["Damaged_Strikes"]
        / phase_summary["Reported_Strikes"]
    )

    phase_display = (
        phase_summary
        .sort_values("Reported_Strikes", ascending=False)
        .head(12)
        .set_index("PHASE_OF_FLIGHT")[["Reported_Strikes"]]
    )

    st.bar_chart(
        phase_display,
        use_container_width=True,
    )

with col2:
    st.markdown("#### Wildlife Size")

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

    size_summary["Observed Damage Rate"] = (
        size_summary["Damaged_Strikes"]
        / size_summary["Reported_Strikes"]
    )

    size_chart = (
        size_summary
        .sort_values("Observed Damage Rate", ascending=False)
        .set_index("SIZE")[["Observed Damage Rate"]]
        .mul(100)
    )

    st.bar_chart(
        size_chart,
        use_container_width=True,
    )


# =====================================================================
# Top wildlife and airports
# =====================================================================

st.subheader("5. Most Frequently Reported Wildlife and Airports")

col1, col2 = st.columns(2)

with col1:
    species_counts = (
        filtered["SPECIES"]
        .dropna()
        .astype(str)
        .str.strip()
    )
    species_counts = species_counts[species_counts != ""]
    species_counts = (
        species_counts
        .value_counts()
        .head(15)
        .rename("Reported Strikes")
        .to_frame()
    )

    st.markdown("#### Top Species")
    st.bar_chart(
        species_counts,
        use_container_width=True,
    )

with col2:
    airport_labels = filtered.copy()

    airport_labels["Airport Label"] = (
        airport_labels["AIRPORT_ID"]
        .astype("string")
        .fillna("")
        .str.strip()
    )

    if "AIRPORT" in airport_labels.columns:
        airport_name = (
            airport_labels["AIRPORT"]
            .astype("string")
            .fillna("")
            .str.strip()
        )

        airport_labels["Airport Label"] = airport_labels[
            "Airport Label"
        ].where(
            airport_name.eq(""),
            airport_labels["Airport Label"]
            + " — "
            + airport_name,
        )

    airport_counts = (
        airport_labels["Airport Label"]
        .replace("", pd.NA)
        .dropna()
        .value_counts()
        .head(15)
        .rename("Reported Strikes")
        .to_frame()
    )

    st.markdown("#### Top Airports by Reports")
    st.bar_chart(
        airport_counts,
        use_container_width=True,
    )

st.caption(
    "High report counts do not necessarily mean an airport or species "
    "has higher underlying strike risk. Exposure volume is not available "
    "in this dataset."
)


# =====================================================================
# Damage severity
# =====================================================================

st.subheader("6. Damage Severity Among Damaged Strikes")

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
            .rename("Damaged Strikes")
            .to_frame()
        )

        st.bar_chart(
            severity_counts,
            use_container_width=True,
        )

        st.caption(
            "Severity is shown only among records where aircraft damage "
            "was indicated. It is therefore conditional on damage."
        )


# =====================================================================
# Component damage
# =====================================================================

st.subheader("7. Reported Component Damage")

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
                "Rate Among Damaged Strikes": safe_rate(
                    count,
                    len(damaged_records),
                ),
            }
        )

    component_df = (
        pd.DataFrame(component_rows)
        .sort_values(
            "Damaged Records",
            ascending=False,
        )
    )

    component_chart = (
        component_df[
            ["Component", "Rate Among Damaged Strikes"]
        ]
        .set_index("Component")
        .mul(100)
    )

    st.bar_chart(
        component_chart,
        use_container_width=True,
    )

    component_display = component_df.copy()
    component_display["Rate Among Damaged Strikes"] = (
        component_display["Rate Among Damaged Strikes"]
        .map(lambda value: f"{value:.2%}")
    )

    st.dataframe(
        component_display,
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
