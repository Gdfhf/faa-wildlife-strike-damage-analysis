import streamlit as st


st.set_page_config(
    page_title="FAA Wildlife Strike Damage Analysis",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="auto",
)


pages = [
    st.Page(
        "app/Home.py",
        title="Home",
        icon="🏠",
        default=True,
    ),
    st.Page(
        "app/pages/01_Project_Overview.py",
        title="1. Project Overview",
        icon="📋",
    ),
    st.Page(
        "app/pages/02_Historical_Data.py",
        title="2. Historical Data",
        icon="📊",
    ),
    st.Page(
        "app/pages/03_Damage_Risk.py",
        title="3. Damage Risk & Model Insights",
        icon="🧠",
    ),
    st.Page(
        "app/pages/04_Monte_Carlo_Simulation.py",
        title="4. Monte Carlo Simulation",
        icon="🎲",
    ),
    st.Page(
        "app/pages/05_Scenario_Comparison.py",
        title="5. Scenario Comparison",
        icon="⚖️",
    ),
    st.Page(
        "app/pages/06_How_to_Read_the_Dashboard.py",
        title="6. How to Read the Dashboard",
        icon="📖",
    ),
]


navigation = st.navigation(pages)

navigation.run()