import streamlit as st


# =====================================================================
# Page configuration
# =====================================================================

st.title("How to Read This Dashboard")

st.markdown(
    """
    This page is a practical guide to interpreting the dashboard.
    It focuses on **what the numbers mean, what they do not mean, and
    how to use the simulation responsibly**.

    Detailed statistical methodology, model development, and formal
    limitations remain documented in the project notebooks and reports.
    """
)


# =====================================================================
# Quick interpretation
# =====================================================================

st.subheader("1. Start Here")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### Historical")
    st.markdown(
        """
        **What happened in the dataset?**

        Historical pages summarize reported FAA wildlife-strike records.

        These are observed patterns, not predictions.
        """
    )

with col2:
    st.markdown("### Model")
    st.markdown(
        """
        **What probability does the fitted model assign?**

        The damage model estimates the probability of aircraft damage
        for a reported strike scenario.
        """
    )

with col3:
    st.markdown("### Simulation")
    st.markdown(
        """
        **What happens when uncertainty is simulated repeatedly?**

        Monte Carlo combines model probabilities with historically
        compatible scenario context across many trials.
        """
    )


st.info(
    "The most important distinction: historical percentages, model "
    "probabilities, and Monte Carlo results answer related but different "
    "questions."
)


# =====================================================================
# What the simulator predicts
# =====================================================================

st.subheader("2. What Does the Simulator Actually Predict?")

st.success(
    "The simulator estimates consequences conditional on a reported "
    "wildlife-strike scenario."
)

st.markdown(
    """
    A result such as **7.3% aircraft-damage probability** means:

    > Among simulated versions of the selected reported wildlife-strike
    > scenario, the fitted model assigns an average damage probability of
    > about 7.3%.

    It does **not** mean that 7.3% of all flights will experience aircraft
    damage.
    """
)

with st.expander(
    "Why can't this dashboard estimate the chance of a strike occurring?",
    expanded=False,
):
    st.markdown(
        """
        The FAA strike records describe **reported strike events**.
        The project does not have a complete denominator representing all
        flights, all aircraft exposure, or all wildlife encounters.

        Because of that, the dashboard models outcomes **after a strike
        scenario has already been defined** rather than the probability
        that a strike occurs in the first place.
        """
    )


# =====================================================================
# Historical support
# =====================================================================

st.subheader("3. Why Are Some Scenario Combinations Unavailable?")

st.markdown(
    """
    The simulator is intentionally restricted to combinations with
    historical support.

    If an airport, aircraft class, aircraft mass group, season, and
    phase-of-flight combination never appears in the support data, the
    dashboard blocks that required combination instead of generating an
    apparently precise estimate from no historical precedent.
    """
)

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Supported scenario")
    st.markdown(
        """
        - Exists in the historical support population
        - Can provide compatible donor records
        - Can be simulated
        """
    )

with col2:
    st.markdown("#### Unsupported scenario")
    st.markdown(
        """
        - No exact required historical match
        - No suitable donor population
        - Simulation is blocked
        """
    )

st.warning(
    "A supported scenario is not automatically a high-confidence "
    "scenario. A combination based on only a small number of historical "
    "records should still be interpreted cautiously."
)


# =====================================================================
# Historical sampling
# =====================================================================

st.subheader("4. What Does 'Historical Sampling' Mean?")

st.markdown(
    """
    Required scenario inputs are fixed by the user. Optional variables
    can be left unspecified.

    When an optional field is left as **Historical sampling**, the
    dashboard does not randomly invent a value and does not sample each
    variable independently. Instead, it samples complete compatible
    historical donor rows and preserves the relationships already
    observed in those records.
    """
)

st.markdown(
    """
    **Example**

    Suppose the user specifies:

    - Airport: KSMF
    - Aircraft class: A
    - Mass group: Heavy
    - Season: Summer
    - Phase of flight: Take-off Run

    but leaves wildlife size, engine type, number struck, height, and
    weather unspecified.

    The simulation fills those optional characteristics from historically
    compatible strike records rather than assigning arbitrary values.
    """
)


# =====================================================================
# Monte Carlo intuition
# =====================================================================

st.subheader("5. Why Use 10,000 Monte Carlo Trials?")

st.markdown(
    """
    One model prediction provides a probability. Monte Carlo asks what
    repeated simulated outcomes look like when that probability and
    historically sampled context are used many times.

    The dashboard defaults to **10,000 trials** because it provides a
    stable operational estimate without making normal dashboard use
    unnecessarily slow.
    """
)

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### More trials help with")
    st.markdown(
        """
        - reducing random simulation noise;
        - stabilizing simulated rates;
        - making repeated runs more consistent.
        """
    )

with col2:
    st.markdown("#### More trials do NOT fix")
    st.markdown(
        """
        - limited historical support;
        - model error;
        - reporting bias;
        - future distribution changes.
        """
    )


# =====================================================================
# Probability hierarchy
# =====================================================================

st.subheader("6. How the Outcome Probabilities Relate")

st.markdown(
    """
    The project uses a layered outcome structure:
    """
)

st.markdown(
    """
    **1. Aircraft damage**

    The primary model estimates whether the reported strike results in
    aircraft damage.

    **2. Severity given damage**

    Severity is evaluated only after damage occurs.

    **3. Component damage given damage**

    Component models estimate which aircraft areas may be affected after
    damage has occurred.
    """
)

st.info(
    "Severity and component probabilities are conditional quantities. "
    "They should not be read as unconditional percentages across all "
    "reported strikes."
)

with st.expander(
    "Why don't the component probabilities add to 100%?",
    expanded=False,
):
    st.markdown(
        """
        Component outcomes are **not mutually exclusive**.

        A single damaging wildlife strike can affect more than one
        aircraft component, so engine, wing/rotor, forward cockpit,
        landing gear, and propeller probabilities do not form pieces of
        one 100% total.
        """
    )


# =====================================================================
# Model threshold
# =====================================================================

st.subheader("7. Probability Is Not the Same as a Classification Threshold")

st.markdown(
    """
    The damage model outputs a continuous probability.

    During model evaluation, a threshold was also selected so that
    confusion matrices, precision, recall, and F1 could be examined.
    That threshold is useful for understanding classification behavior,
    but it is **not** what drives the Monte Carlo simulator.
    """
)

st.warning(
    "The locked classification threshold is an analytical reference. "
    "It is not an aviation safety rule or recommended operational "
    "decision boundary."
)


# =====================================================================
# Train / validation / test timeline
# =====================================================================

st.subheader("8. How Was the Model Evaluated Over Time?")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 1990–2018")
    st.markdown(
        """
        **Model development**

        Historical data used for fitting the main predictive models.
        """
    )

with col2:
    st.markdown("### 2019–2021")
    st.markdown(
        """
        **Validation / calibration**

        Used to choose calibration and analytical decision settings.
        """
    )

with col3:
    st.markdown("### 2022–2024")
    st.markdown(
        """
        **Locked final test**

        Held out until the final evaluation of the selected system.
        """
    )


st.caption(
    "The Monte Carlo donor/support population is restricted to the "
    "pre-final-test historical period so that 2022–2024 does not leak "
    "into the simulation reference population."
)


# =====================================================================
# Uncertainty
# =====================================================================

st.subheader("9. Three Different Sources of Uncertainty")

tab1, tab2, tab3 = st.tabs(
    [
        "Monte Carlo",
        "Model",
        "Historical Support",
    ]
)

with tab1:
    st.markdown(
        """
        ### Monte Carlo uncertainty

        Comes from random simulation draws.

        Running more trials can reduce this type of variation.
        """
    )

with tab2:
    st.markdown(
        """
        ### Model uncertainty

        Comes from learning relationships from finite historical data
        and applying them to future or different scenarios.

        More Monte Carlo trials do not remove model uncertainty.
        """
    )

with tab3:
    st.markdown(
        """
        ### Historical-support uncertainty

        Comes from having few or no compatible historical examples.

        More simulation trials cannot create additional historical
        evidence.
        """
    )


# =====================================================================
# Scenario comparison
# =====================================================================

st.subheader("10. How to Use Scenario Comparison")

st.markdown(
    """
    Scenario comparison is most useful when **one factor changes and the
    others stay the same**.

    For example:

    **Scenario A:** KSMF, Heavy, Summer, Take-off Run  
    **Scenario B:** KSMF, Heavy, Winter, Take-off Run

    This provides a much clearer what-if interpretation than changing
    airport, season, aircraft class, and phase of flight simultaneously.
    """
)

st.markdown(
    """
    The comparison page therefore emphasizes:

    - **percentage-point difference** as the main result;
    - relative percentage change as secondary context;
    - historical support for both scenarios.
    """
)


# =====================================================================
# Common interpretation mistakes
# =====================================================================

st.subheader("11. Common Misinterpretations")

with st.expander(
    "“This airport has more reported strikes, so it must be more dangerous.”",
    expanded=False,
):
    st.markdown(
        """
        Not necessarily.

        Airports differ greatly in traffic volume, reporting practices,
        wildlife exposure, geography, and operations. The project does
        not have a full flight-exposure denominator, so report counts
        should not be treated as airport risk rankings.
        """
    )


with st.expander(
    "“A feature is important in SHAP, so it causes aircraft damage.”",
    expanded=False,
):
    st.markdown(
        """
        No.

        SHAP and permutation importance explain how the fitted model uses
        information. They do not establish physical or causal mechanisms.
        """
    )


with st.expander(
    "“If I run 100,000 trials, the result becomes certain.”",
    expanded=False,
):
    st.markdown(
        """
        No.

        More trials reduce Monte Carlo sampling noise. They do not fix
        sparse historical data, model limitations, reporting bias, or
        future distribution shift.
        """
    )


with st.expander(
    "“A supported scenario means the estimate is equally reliable everywhere.”",
    expanded=False,
):
    st.markdown(
        """
        No.

        Support only confirms that compatible historical examples exist.
        Some combinations are represented much more strongly than others.
        """
    )


# =====================================================================
# Practical dashboard guide
# =====================================================================

st.subheader("12. Which Page Should I Use?")

page_guide = {
    "Overview": (
        "Use this first for headline dataset patterns and the overall "
        "project story."
    ),
    "Historical Explorer": (
        "Use this to filter the FAA records and inspect observed "
        "historical patterns."
    ),
    "Damage Risk & Model Insights": (
        "Use this to examine model performance, generalization, and "
        "explainability."
    ),
    "What-If Simulation": (
        "Use this to simulate one historically supported reported "
        "wildlife-strike scenario."
    ),
    "Scenario Comparison": (
        "Use this to compare two supported scenarios under the same "
        "Monte Carlo settings."
    ),
}

for page, description in page_guide.items():
    st.markdown(f"**{page}** — {description}")


# =====================================================================
# Final interpretation reminder
# =====================================================================

st.divider()

st.markdown("### Bottom Line")

st.markdown(
    """
    This dashboard is best treated as a **scenario-analysis and decision-
    support prototype** built from historical FAA wildlife-strike reports.

    It helps users explore historical patterns, understand the predictive
    model, and test how modeled consequences change across supported
    reported-strike scenarios.

    It should not be interpreted as a real-time collision predictor,
    causal safety model, or substitute for operational aviation judgment.
    """
)
