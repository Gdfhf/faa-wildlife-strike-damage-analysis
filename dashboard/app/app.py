import streamlit as st

from src.data.loaders import (
    load_analytical_data,
    load_scenario_schema,
)
from src.models.loaders import (
    load_damage_model,
    load_severity_model,
)


st.set_page_config(
    page_title="FAA Wildlife Strike Dashboard",
    layout="wide",
)

st.title("FAA Wildlife Strike Damage Analysis")


try:
    df = load_analytical_data()

    st.success(
        f"Analytical dataset loaded successfully: "
        f"{len(df):,} records"
    )

except Exception as exc:
    st.error(f"Dataset loading failed: {exc}")


try:
    damage_model = load_damage_model()

    st.success(
        f"Damage model loaded successfully: "
        f"{type(damage_model).__name__}"
    )

except Exception as exc:
    st.error(f"Damage model loading failed: {exc}")


try:
    severity_model = load_severity_model()

    st.success(
        f"Severity model loaded successfully: "
        f"{type(severity_model).__name__}"
    )

except Exception as exc:
    st.error(f"Severity model loading failed: {exc}")


try:
    scenario_schema = load_scenario_schema()

    st.success(
        f"Simulation schema loaded successfully."
    )

    st.json(scenario_schema)

except Exception as exc:
    st.error(f"Scenario schema loading failed: {exc}")