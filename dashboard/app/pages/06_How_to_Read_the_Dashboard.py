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
    "How to Read This Dashboard",
    (
        "A practical guide to what the dashboard numbers mean, what they "
        "do not mean, and how to interpret the simulation and comparison "
        "tools responsibly."
    ),
)

st.caption(
    "Detailed statistical methodology, model development, diagnostics, "
    "and formal limitations remain documented in the project notebooks "
    "and reports."
)


# =====================================================================
# Quick interpretation
# =====================================================================

section_divider()

section_header(
    "1. Start here",
    (
        "The dashboard contains three related but different kinds of "
        "information."
    ),
)

col1, col2, col3 = st.columns(
    3,
    gap="medium",
)

with col1:
    with st.container(border=True):
        st.markdown("### Historical")
        st.markdown(
            """
            **What happened in the reported dataset?**

            Historical pages summarize observed FAA wildlife-strike records.

            These are descriptive patterns, not predictions.
            """
        )

with col2:
    with st.container(border=True):
        st.markdown("### Model")
        st.markdown(
            """
            **What probability does the fitted model assign?**

            The damage model estimates the probability of aircraft damage
            for a reported strike scenario.
            """
        )

with col3:
    with st.container(border=True):
        st.markdown("### Simulation")
        st.markdown(
            """
            **What happens across repeated simulated outcomes?**

            Monte Carlo combines model probabilities with historically
            compatible donor context over many trials.
            """
        )

st.info(
    "Historical percentages, model probabilities, and Monte Carlo outcomes "
    "answer related but different questions."
)


# =====================================================================
# What the simulator predicts
# =====================================================================

section_divider()

section_header(
    "2. What does the simulator actually predict?",
    (
        "The simulator estimates consequences conditional on a reported "
        "wildlife-strike scenario."
    ),
)

st.success(
    "The primary modeled quantity is the probability of aircraft damage "
    "given a reported wildlife-strike scenario."
)

st.markdown(
    """
    A result such as **7.3% mean aircraft-damage probability** means:

    > Across simulated versions of the selected reported wildlife-strike
    > scenario, the fitted model assigns an average aircraft-damage
    > probability of about 7.3%.

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
        The FAA data describe **reported wildlife-strike events**. The
        project does not contain a complete denominator for all flights,
        all aircraft exposure, or all wildlife encounters.

        The dashboard therefore models outcomes **after a strike scenario
        has already been defined**, rather than the probability that a
        strike occurs in the first place.
        """
    )


# =====================================================================
# Historical support
# =====================================================================

section_divider()

section_header(
    "3. What does historical support mean?",
    (
        "Historical support describes data coverage. It is not the same "
        "thing as certainty or physical plausibility."
    ),
)

st.markdown(
    """
    The simulator uses a **required scenario context** consisting of:

    - geography: airport or FAA region;
    - aircraft class;
    - aircraft mass group;
    - season;
    - phase of flight.

    If that required combination has no exact support in the 1990–2021
    simulation reference population, the dashboard blocks the simulation
    instead of producing an apparently precise estimate from no historical
    precedent.
    """
)

support_col1, support_col2 = st.columns(
    2,
    gap="medium",
)

with support_col1:
    with st.container(border=True):
        st.markdown("#### Required-context support")
        st.markdown(
            """
            - Determines whether the simulation may run
            - Counts historical donor records matching the required context
            - Zero required support blocks the simulation
            """
        )

with support_col2:
    with st.container(border=True):
        st.markdown("#### Full specified-context support")
        st.markdown(
            """
            - Used when optional values are explicitly supplied
            - Checks whether the complete specified combination was observed
            - Helps distinguish observed combinations from counterfactual ones
            """
        )

st.warning(
    "A supported scenario is not automatically a high-confidence scenario. "
    "Sparse support should still be interpreted cautiously."
)

with st.expander(
    "What is a counterfactual override?",
    expanded=False,
):
    st.markdown(
        """
        Page 04 allows some optional characteristics to be explicitly
        overridden.

        If the **required context is supported** but the complete combination
        including an optional override was not historically observed, the
        dashboard may still run the simulation and identifies that override
        as **counterfactual**.

        Counterfactual does not automatically mean impossible. It means the
        estimate extends beyond an exactly observed historical combination
        and should be interpreted with greater caution.
        """
    )


# =====================================================================
# Historical sampling
# =====================================================================

section_divider()

section_header(
    "4. What does 'Historical sampling' mean?",
    (
        "Optional fields can remain unspecified so that historical donor "
        "rows provide their values."
    ),
)

st.markdown(
    """
    When an optional field is left as **Historical sampling**, the dashboard
    does not independently invent values for wildlife, engine, weather, and
    other optional characteristics.

    Instead, it samples complete compatible historical donor rows. This
    preserves combinations and relationships that actually occurred in the
    reference data.
    """
)

st.markdown(
    """
    **Example**

    Suppose the user specifies:

    - Airport: KSMF
    - Aircraft class: A — Airplane
    - Mass group: Heavy
    - Season: Summer
    - Phase of flight: Take-off Run

    but leaves wildlife size, engine type, number struck, height, and weather
    unspecified.

    Those optional characteristics are then filled from compatible historical
    donor records rather than selected independently.
    """
)

st.caption(
    "Some coded fields are displayed with human-readable labels in the UI. "
    "The underlying model and simulation values remain unchanged."
)


# =====================================================================
# Monte Carlo intuition
# =====================================================================

section_divider()

section_header(
    "5. Why use 10,000 Monte Carlo trials?",
    (
        "The default balances stable simulation behavior with practical "
        "dashboard response time."
    ),
)

st.markdown(
    """
    The fitted model produces probabilities. Monte Carlo repeatedly samples
    historically compatible context and generates simulated outcomes from
    those probabilities.

    The dashboard defaults to **10,000 trials** because this generally
    provides stable operational summaries without making normal interactive
    use unnecessarily slow.
    """
)

col1, col2 = st.columns(
    2,
    gap="medium",
)

with col1:
    with st.container(border=True):
        st.markdown("#### More trials help with")
        st.markdown(
            """
            - reducing random simulation noise;
            - stabilizing realized simulated rates;
            - improving run-to-run consistency.
            """
        )

with col2:
    with st.container(border=True):
        st.markdown("#### More trials do NOT fix")
        st.markdown(
            """
            - limited historical support;
            - model error;
            - reporting bias;
            - distribution shift;
            - unrealistic user assumptions.
            """
        )

st.info(
    "Mean modeled probabilities are the primary analytical outputs. "
    "Realized Monte Carlo rates are secondary simulated outcomes and "
    "contain random simulation noise."
)


# =====================================================================
# Probability hierarchy
# =====================================================================

section_divider()

section_header(
    "6. How do the outcome probabilities relate?",
    (
        "The project uses a layered damage → severity/component structure."
    ),
)

st.markdown(
    """
    **1. Aircraft damage**

    The primary model estimates whether a reported strike results in
    aircraft damage.

    **2. Severity given damage**

    Severity is evaluated after aircraft damage occurs.

    **3. Component damage given damage**

    Component models estimate which aircraft areas may be affected after
    damage occurs.
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

        One damaging strike can affect more than one aircraft component,
        so engine, wing/rotor, forward cockpit, landing gear, and propeller
        probabilities are not pieces of a single 100% total.
        """
    )


# =====================================================================
# Number struck
# =====================================================================

section_divider()

section_header(
    "7. How should 'Number struck' be interpreted?",
    (
        "The analytical dataset treats this field as an ordered category, "
        "not as an arbitrary exact integer."
    ),
)

st.markdown(
    """
    The available categories are based on the historical analytical data,
    for example:

    - **1**
    - **2–10**
    - **11–100**
    - **More than 100**

    The dashboard therefore presents historical categories rather than
    allowing an arbitrary value such as 7 or 42 to be entered as though the
    model had been trained on exact counts.
    """
)


# =====================================================================
# Model threshold
# =====================================================================

section_divider()

section_header(
    "8. Probability is not the same as a classification threshold",
    (
        "The Monte Carlo simulator uses continuous probabilities rather "
        "than the locked evaluation threshold."
    ),
)

st.markdown(
    """
    During model evaluation, a classification threshold was selected so
    that confusion matrices, precision, recall, and F1 could be examined.

    That threshold is useful for evaluating classification behavior, but it
    does **not** drive the Monte Carlo simulator.
    """
)

st.warning(
    "The locked classification threshold is an analytical reference. "
    "It is not an aviation safety rule or recommended operational decision "
    "boundary."
)


# =====================================================================
# Train / validation / test timeline
# =====================================================================

section_divider()

section_header(
    "9. How was the model evaluated over time?",
    (
        "Chronological separation was used to preserve a genuine future "
        "holdout period."
    ),
)

col1, col2, col3 = st.columns(
    3,
    gap="medium",
)

with col1:
    with st.container(border=True):
        st.markdown("### 1990–2018")
        st.markdown(
            """
            **Model development**

            Historical records used for fitting the main predictive models.
            """
        )

with col2:
    with st.container(border=True):
        st.markdown("### 2019–2021")
        st.markdown(
            """
            **Validation / calibration**

            Used for calibration and analytical decision settings.
            """
        )

with col3:
    with st.container(border=True):
        st.markdown("### 2022–2024")
        st.markdown(
            """
            **Locked final test**

            Held out until final evaluation of the selected system.
            """
        )

st.caption(
    "The Monte Carlo donor/support population is restricted to 1990–2021, "
    "so the 2022–2024 final-test period does not leak into the simulation "
    "reference population."
)


# =====================================================================
# Uncertainty
# =====================================================================

section_divider()

section_header(
    "10. Three different sources of uncertainty",
    (
        "Increasing Monte Carlo trials addresses only one of these."
    ),
)

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

        Comes from learning relationships from finite historical data and
        applying them to future or different scenarios.

        More Monte Carlo trials do not remove model uncertainty.
        """
    )

with tab3:
    st.markdown(
        """
        ### Historical-support uncertainty

        Comes from having few or no compatible historical examples.

        More simulation trials cannot create additional historical evidence.
        """
    )


# =====================================================================
# Scenario comparison
# =====================================================================

section_divider()

section_header(
    "11. How to use Scenario Comparison",
    (
        "The comparison page is designed around controlled one-variable "
        "what-if comparisons."
    ),
)

st.markdown(
    """
    Page 05 first defines a **shared scenario context** and then asks which
    factor should differ between Scenario A and Scenario B.

    Example:

    **Shared context**
    - KDEN — Denver International Airport
    - A — Airplane
    - Heavy
    - Autumn
    - Descent

    **Comparison variable**
    - Number struck

    **Scenario A:** 1  
    **Scenario B:** 2–10

    This is much easier to interpret than changing several unrelated
    conditions at once.
    """
)

st.markdown(
    """
    The comparison page therefore emphasizes:

    - **percentage-point difference** as the primary result;
    - relative percentage change as secondary context;
    - common Monte Carlo settings for both scenarios;
    - historical support for both scenarios;
    - one changed field whenever possible.
    """
)

with st.expander(
    "Why are some Page 04 optional fields not comparison controls?",
    expanded=False,
):
    st.markdown(
        """
        Page 05 intentionally exposes a smaller set of comparison controls.

        State/location is tied to geography, while height and speed are
        strongly related to operational context such as phase of flight.
        Sky and precipitation are also left historically sampled in the
        controlled comparison workflow.

        This keeps A/B comparisons easier to interpret and reduces the chance
        of creating internally contradictory or extremely sparse scenarios.
        """
    )


# =====================================================================
# Common interpretation mistakes
# =====================================================================

section_divider()

section_header(
    "12. Common misinterpretations",
    (
        "These are the most important conclusions the dashboard should not "
        "be used to make."
    ),
)

with st.expander(
    "“This airport has more reported strikes, so it must be more dangerous.”",
    expanded=False,
):
    st.markdown(
        """
        Not necessarily.

        Airports differ in traffic volume, reporting practices, wildlife
        exposure, geography, and operations. The project does not have a
        complete flight-exposure denominator, so report counts should not be
        treated as airport risk rankings.
        """
    )

with st.expander(
    "“A feature is important in SHAP, so it causes aircraft damage.”",
    expanded=False,
):
    st.markdown(
        """
        No.

        SHAP and permutation importance describe how the fitted model uses
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

        More trials reduce Monte Carlo sampling noise. They do not fix sparse
        historical data, model limitations, reporting bias, or future
        distribution shift.
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

with st.expander(
    "“A counterfactual optional override is the same as an observed scenario.”",
    expanded=False,
):
    st.markdown(
        """
        No.

        If the required context is supported but the complete combination
        including an optional override was not observed, the dashboard labels
        that situation as counterfactual. The estimate may still be useful for
        what-if analysis, but it deserves greater caution.
        """
    )


# =====================================================================
# Practical dashboard guide
# =====================================================================

section_divider()

section_header(
    "13. Which page should I use?",
    (
        "Each dashboard page answers a different part of the project "
        "question."
    ),
)

page_guide = {
    "Overview": (
        "Use this first for headline dataset patterns and the overall "
        "project story."
    ),
    "Historical Explorer": (
        "Use this to filter FAA records and inspect observed historical "
        "patterns."
    ),
    "Damage Risk & Model Insights": (
        "Use this to examine model performance, generalization, and "
        "explainability."
    ),
    "What-If Simulation": (
        "Use this to simulate one supported reported wildlife-strike "
        "scenario and optionally test specific what-if overrides."
    ),
    "Scenario Comparison": (
        "Use this for a controlled A/B comparison in which one factor "
        "changes while the shared context remains fixed."
    ),
}

for page, description in page_guide.items():
    st.markdown(
        f"**{page}** — {description}"
    )


# =====================================================================
# Final interpretation reminder
# =====================================================================

section_divider()

st.markdown("### Bottom line")

st.markdown(
    """
    This dashboard is best treated as a **scenario-analysis and
    decision-support prototype** built from historical FAA wildlife-strike
    reports.

    It helps users explore reported historical patterns, understand the
    predictive models, and test how modeled consequences change across
    historically grounded reported-strike scenarios.

    It should not be interpreted as a real-time collision predictor, causal
    safety model, or substitute for operational aviation judgment.
    """
)
