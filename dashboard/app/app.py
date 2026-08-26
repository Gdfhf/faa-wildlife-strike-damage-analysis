import streamlit as st


st.set_page_config(
    page_title="FAA Wildlife Strike Dashboard",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="auto",
)


st.title("FAA Wildlife Strike Damage Analysis")

st.markdown(
    """
    This dashboard presents the results of the FAA wildlife strike
    damage analysis and provides an operational what-if simulation
    environment based on the models developed during the project.

    Use the pages in the sidebar to explore the historical data,
    examine damage risk, and run Monte Carlo scenarios.
    """
)

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Historical Analysis")
    st.markdown(
        """
        Explore reported FAA wildlife strike patterns across the
        1990–2024 analytical dataset, including temporal patterns,
        airports, wildlife, and observed aircraft damage.
        """
    )

with col2:
    st.subheader("Operational Simulation")
    st.markdown(
        """
        Construct supported what-if scenarios and estimate damage,
        severity, and component-level outcomes using the project's
        trained probability models and Monte Carlo simulation.
        """
    )

st.info(
    "The simulation uses historical reference data through 2021. "
    "The 2022–2024 period was kept separate from the simulation "
    "reference population to preserve the project's temporal "
    "evaluation design."
)