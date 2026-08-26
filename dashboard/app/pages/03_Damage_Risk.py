from pathlib import Path
import json

import pandas as pd
import streamlit as st


# =====================================================================
# Page configuration
# =====================================================================

st.title("Damage Risk & Model Insights")

st.markdown(
    """
    Review the evidence behind the project's canonical aircraft-damage
    probability system. This page presents saved validation and
    explainability artifacts from Notebooks 06 and 09; it does **not**
    retrain models or recompute SHAP values during dashboard use.

    The primary model estimates **reported aircraft-damage probability
    conditional on a reported wildlife strike**. Classification
    thresholds shown here are analytical reference points, not
    operational safety rules.
    """
)


# =====================================================================
# Portable project paths
# =====================================================================

def find_project_root():
    """
    Find the repository root from the current working directory or from
    this page's location.
    """
    candidates = []

    try:
        candidates.extend([Path.cwd(), *Path.cwd().parents])
    except Exception:
        pass

    try:
        page_path = Path(__file__).resolve()
        candidates.extend([page_path.parent, *page_path.parents])
    except Exception:
        pass

    seen = set()

    for candidate in candidates:
        candidate = candidate.resolve()

        if candidate in seen:
            continue

        seen.add(candidate)

        if (
            (candidate / "outputs").exists()
            and (candidate / "models").exists()
        ):
            return candidate

    # Fallback consistent with the dashboard/app/pages layout:
    # dashboard/app/pages/03_...py -> repository root is three parents up.
    try:
        return Path(__file__).resolve().parents[3]
    except Exception:
        return Path.cwd()


ROOT = find_project_root()

NB06_DIR = ROOT / "outputs" / "06_calibration_validation"
NB09_DIR = ROOT / "outputs" / "09_explainability"


# =====================================================================
# Artifact helpers
# =====================================================================

@st.cache_data
def load_csv(path_string):
    path = Path(path_string)
    if not path.exists():
        return None
    return pd.read_csv(path)


@st.cache_data
def load_json(path_string):
    path = Path(path_string)
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def existing_image(directory, filename):
    path = directory / filename
    return path if path.exists() else None


def find_column(data, candidates):
    """Return the first matching column name, case-insensitively."""
    if data is None or data.empty:
        return None

    lookup = {
        str(column).lower(): column
        for column in data.columns
    }

    for candidate in candidates:
        match = lookup.get(candidate.lower())
        if match is not None:
            return match

    return None


def display_artifact_warning(name):
    st.info(
        f"{name} was not found in the expected output directory. "
        "The rest of the page can still load from the available "
        "Notebook 06/09 artifacts."
    )


def format_feature_name(value):
    return (
        str(value)
        .replace("_", " ")
        .title()
    )


# =====================================================================
# Load core metadata
# =====================================================================

manifest = load_csv(
    str(NB06_DIR / "final_model_manifest.csv")
)

metadata = load_json(
    str(NB06_DIR / "validation_metadata.json")
)

probability_metrics = load_csv(
    str(NB06_DIR / "final_test_probability_metrics.csv")
)

threshold_metrics = load_csv(
    str(NB06_DIR / "final_test_locked_threshold_metrics.csv")
)

year_metrics = load_csv(
    str(NB06_DIR / "final_test_metrics_by_year.csv")
)

unseen_metrics = load_csv(
    str(NB06_DIR / "final_test_unseen_airport_metrics.csv")
)

support_metrics = load_csv(
    str(NB06_DIR / "final_test_performance_by_support_tier.csv")
)

trust_evidence = load_csv(
    str(NB06_DIR / "monte_carlo_trust_decision_evidence.csv")
)

grouped_shap = load_csv(
    str(
        NB09_DIR
        / "09_shap_grouped_original_feature_importance.csv"
    )
)

permutation = load_csv(
    str(
        NB09_DIR
        / "09_permutation_importance_original_features.csv"
    )
)

airport_dependence = load_csv(
    str(NB09_DIR / "09_airport_dependence_summary.csv")
)

secondary_status = load_csv(
    str(NB09_DIR / "09_secondary_model_status.csv")
)


# =====================================================================
# 1. Canonical model
# =====================================================================

st.subheader("1. Canonical Damage Probability Model")

if manifest is not None and not manifest.empty:

    row = manifest.iloc[0]

    model_name = row.get(
        "selected_base_candidate",
        "Canonical damage model",
    )

    calibration = row.get(
        "selected_calibration_method",
        "Not available",
    )

    feature_set = row.get(
        "feature_set",
        "Not available",
    )

    n_features = row.get(
        "n_input_features",
        "Not available",
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Base Candidate",
            str(model_name),
        )

    with col2:
        st.metric(
            "Calibration",
            str(calibration).title(),
        )

    with col3:
        st.metric(
            "Feature Set",
            str(feature_set).replace("_", " ").title(),
        )

    with col4:
        st.metric(
            "Input Features",
            str(n_features),
        )

    base_period = row.get(
        "base_fit_period",
        "1990–2018",
    )

    calibration_period = row.get(
        "calibration_fit_period",
        "2019–2021",
    )

    final_period = row.get(
        "final_test_period",
        "2022–2024",
    )

    st.caption(
        f"Base-model fitting period: {base_period} | "
        f"Calibration/selection period: {calibration_period} | "
        f"Locked final-test period: {final_period}"
    )

else:
    display_artifact_warning("Final model manifest")

    st.markdown(
        """
        The approved primary system is the final calibrated
        aircraft-damage probability pipeline exported by Notebook 06.
        """
    )


if metadata is not None:

    with st.expander(
        "Validation design and locked decisions",
        expanded=False,
    ):
        st.json(metadata)


st.info(
    "The model produces a continuous damage probability. The Monte "
    "Carlo simulator uses that continuous probability directly; it does "
    "not convert each scenario to damage/no-damage using the "
    "classification threshold shown later on this page."
)


# =====================================================================
# 2. Final-test probability performance
# =====================================================================

st.subheader("2. Locked Final-Test Probability Performance")

st.caption(
    "These are out-of-time results for 2022–2024 after model, "
    "calibration, and threshold decisions had already been locked."
)

if probability_metrics is not None and not probability_metrics.empty:

    st.dataframe(
        probability_metrics,
        use_container_width=True,
        hide_index=True,
    )

    system_col = find_column(
        probability_metrics,
        ["probability_system", "system", "model"],
    )

    pr_col = find_column(
        probability_metrics,
        ["pr_auc", "average_precision", "average_precision_score"],
    )

    brier_col = find_column(
        probability_metrics,
        ["brier_score", "brier"],
    )

    logloss_col = find_column(
        probability_metrics,
        ["log_loss", "logloss"],
    )

    if system_col is not None:
        final_rows = probability_metrics.loc[
            probability_metrics[system_col]
            .astype(str)
            .str.lower()
            .str.contains("final")
        ]

        if final_rows.empty:
            final_row = probability_metrics.iloc[-1]
        else:
            final_row = final_rows.iloc[-1]

        metric_columns = st.columns(3)

        with metric_columns[0]:
            if pr_col is not None:
                st.metric(
                    "Final PR-AUC",
                    f"{float(final_row[pr_col]):.3f}",
                )
            else:
                st.metric("Final PR-AUC", "See table")

        with metric_columns[1]:
            if brier_col is not None:
                st.metric(
                    "Final Brier Score",
                    f"{float(final_row[brier_col]):.4f}",
                )
            else:
                st.metric("Final Brier Score", "See table")

        with metric_columns[2]:
            if logloss_col is not None:
                st.metric(
                    "Final Log Loss",
                    f"{float(final_row[logloss_col]):.4f}",
                )
            else:
                st.metric("Final Log Loss", "See table")

else:
    display_artifact_warning(
        "Final-test probability metrics"
    )


st.caption(
    "PR-AUC summarizes discrimination for the relatively uncommon "
    "damage outcome. Brier score and log loss evaluate probability "
    "quality; lower values indicate better probabilistic predictions."
)


# =====================================================================
# 3. Classification reference
# =====================================================================

st.subheader("3. Classification Reference at the Locked Threshold")

st.warning(
    "The classification threshold is included for interpretability and "
    "error analysis only. It is not a recommended aviation decision "
    "threshold and is not what drives the Monte Carlo simulation."
)

confusion_path = existing_image(
    NB09_DIR,
    "09_locked_threshold_confusion_matrix.png",
)

col1, col2 = st.columns([1.1, 1])

with col1:

    if confusion_path is not None:
        st.image(
            str(confusion_path),
            caption=(
                "Final-test confusion matrix at the locked "
                "validation-derived threshold."
            ),
            use_container_width=True,
        )

    else:
        st.markdown("#### Confusion Matrix")
        st.write(
            "TN = 55,651 | FP = 1,322 | "
            "FN = 1,314 | TP = 932"
        )

with col2:

    if threshold_metrics is not None and not threshold_metrics.empty:

        st.markdown("#### Locked Threshold Metrics")

        st.dataframe(
            threshold_metrics,
            use_container_width=True,
            hide_index=True,
        )

    else:
        st.markdown("#### Known F1-threshold result")

        st.metric("Locked F1 Threshold", "0.20")
        st.metric("Precision", "≈ 41.35%")
        st.metric("Recall", "≈ 41.50%")


st.caption(
    "At threshold 0.20, the final test contained 55,651 true "
    "negatives, 1,322 false positives, 1,314 false negatives, and "
    "932 true positives. The similar FP and FN counts reflect the "
    "validation-derived F1 trade-off rather than an accuracy-maximizing "
    "or safety-cost-based policy."
)


# =====================================================================
# 4. Temporal and geographic generalization
# =====================================================================

st.subheader("4. Generalization Evidence")

col1, col2 = st.columns(2)

with col1:

    st.markdown("#### Performance by Future Year")

    if year_metrics is not None and not year_metrics.empty:

        year_col = find_column(
            year_metrics,
            ["INCIDENT_YEAR", "year"],
        )

        pr_col = find_column(
            year_metrics,
            ["pr_auc", "average_precision"],
        )

        if year_col is not None and pr_col is not None:

            chart = (
                year_metrics[[year_col, pr_col]]
                .dropna()
                .set_index(year_col)
            )

            st.line_chart(
                chart,
                use_container_width=True,
            )

        st.dataframe(
            year_metrics,
            use_container_width=True,
            hide_index=True,
        )

    else:
        display_artifact_warning(
            "Final-test metrics by year"
        )


with col2:

    st.markdown("#### Unseen-Airport Evaluation")

    if unseen_metrics is not None and not unseen_metrics.empty:

        st.dataframe(
            unseen_metrics,
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.write(
            "Notebook 06 retained explicit unseen-airport testing as "
            "part of the model's geographic generalization audit."
        )


st.caption(
    "Performance at unseen airports is informative but should be "
    "interpreted together with sample size, damage prevalence, and "
    "historical support. Small unusual subsets can produce unstable "
    "metrics."
)


if support_metrics is not None and not support_metrics.empty:

    with st.expander(
        "Performance by historical support tier",
        expanded=False,
    ):
        st.dataframe(
            support_metrics,
            use_container_width=True,
            hide_index=True,
        )


# =====================================================================
# 5. Global explainability
# =====================================================================

st.subheader("5. What Drives the Damage Model?")

st.markdown(
    """
    Notebook 09 uses two complementary approaches:

    - **Grouped TreeSHAP** asks where the fitted XGBoost model places
      attribution across the original scenario variables.
    - **Permutation importance** asks how much held-out PR-AUC is lost
      when one original input is disrupted.

    Importance describes model reliance, not causation.
    """
)


col1, col2 = st.columns(2)

with col1:

    st.markdown("#### Grouped SHAP Importance")

    if grouped_shap is not None and not grouped_shap.empty:

        feature_col = find_column(
            grouped_shap,
            ["feature"],
        )

        importance_col = find_column(
            grouped_shap,
            ["mean_abs_grouped_shap"],
        )

        if feature_col is not None and importance_col is not None:

            shap_chart = (
                grouped_shap[
                    [feature_col, importance_col]
                ]
                .head(12)
                .copy()
            )

            shap_chart[feature_col] = (
                shap_chart[feature_col]
                .map(format_feature_name)
            )

            shap_chart = shap_chart.set_index(feature_col)

            st.bar_chart(
                shap_chart,
                use_container_width=True,
            )

        st.dataframe(
            grouped_shap.head(12),
            use_container_width=True,
            hide_index=True,
        )

    else:

        shap_image = existing_image(
            NB09_DIR,
            "09_shap_grouped_original_features.png",
        )

        if shap_image is not None:
            st.image(
                str(shap_image),
                use_container_width=True,
            )
        else:
            display_artifact_warning(
                "Grouped SHAP importance"
            )


with col2:

    st.markdown("#### Permutation Importance")

    if permutation is not None and not permutation.empty:

        feature_col = find_column(
            permutation,
            ["feature"],
        )

        importance_col = find_column(
            permutation,
            ["importance_mean_pr_auc_drop"],
        )

        if feature_col is not None and importance_col is not None:

            perm_chart = (
                permutation[
                    [feature_col, importance_col]
                ]
                .head(12)
                .copy()
            )

            perm_chart[feature_col] = (
                perm_chart[feature_col]
                .map(format_feature_name)
            )

            perm_chart = perm_chart.set_index(feature_col)

            st.bar_chart(
                perm_chart,
                use_container_width=True,
            )

        st.dataframe(
            permutation.head(12),
            use_container_width=True,
            hide_index=True,
        )

    else:

        perm_image = existing_image(
            NB09_DIR,
            "09_permutation_importance_original_features.png",
        )

        if perm_image is not None:
            st.image(
                str(perm_image),
                use_container_width=True,
            )
        else:
            display_artifact_warning(
                "Permutation importance"
            )


st.caption(
    "A feature can rank differently under SHAP and permutation "
    "importance because the methods answer different questions and "
    "because correlated or redundant predictors can share information."
)


# =====================================================================
# 6. Directional interpretation
# =====================================================================

st.subheader("6. Direction of Selected Model Effects")

st.markdown(
    """
    Global importance says **how influential** a variable is but not
    which values move the fitted damage score upward or downward.
    Notebook 09 therefore created targeted directional SHAP summaries
    for key research variables.
    """
)

direction_options = {
    "Wildlife Size": "09_shap_direction_size.png",
    "Aircraft Mass Group": "09_shap_direction_ac_mass_group.png",
    "Phase of Flight": "09_shap_direction_phase_of_flight.png",
    "Number Struck": "09_shap_direction_num_struck.png",
    "FAA Region": "09_shap_direction_faaregion.png",
    "Season": "09_shap_direction_season.png",
    "Time of Day": "09_shap_direction_time_of_day.png",
}

available_direction_options = {
    label: filename
    for label, filename in direction_options.items()
    if (NB09_DIR / filename).exists()
}

if available_direction_options:

    selected_direction = st.selectbox(
        "Directional SHAP view",
        options=list(available_direction_options.keys()),
    )

    direction_path = (
        NB09_DIR
        / available_direction_options[selected_direction]
    )

    st.image(
        str(direction_path),
        use_container_width=True,
    )

else:

    st.info(
        "Directional SHAP figures were not found in the expected "
        "Notebook 09 output directory."
    )


st.markdown(
    """
    The executed Notebook 09 interpretation found particularly clear
    directional behavior for wildlife size: larger wildlife generally
    moves the fitted damage score upward while small wildlife moves it
    downward. These are conditional model effects and must not be
    described as causal physical effects.
    """
)


# =====================================================================
# 7. Airport dependence
# =====================================================================

st.subheader("7. Airport Dependence Audit")

st.markdown(
    """
    Exact airport identity was deliberately audited because an
    airport-aware model can improve fit while also creating a risk of
    memorizing persistent local patterns. The dashboard therefore
    presents airport reliance as a model limitation as well as a source
    of predictive information.
    """
)

if airport_dependence is not None and not airport_dependence.empty:

    st.dataframe(
        airport_dependence,
        use_container_width=True,
        hide_index=True,
    )

airport_comparison_path = existing_image(
    NB09_DIR,
    "09_shap_dedicated_seen_vs_unseen_airports.png",
)

if airport_comparison_path is None:
    airport_comparison_path = existing_image(
        NB09_DIR,
        "09_shap_seen_vs_unseen_airports.png",
    )

if airport_comparison_path is not None:

    st.image(
        str(airport_comparison_path),
        caption=(
            "Notebook 09 geographic explanation comparison."
        ),
        use_container_width=True,
    )


st.caption(
    "Evidence from unseen airports is useful but does not prove "
    "universal geographic generalization. This is one reason the "
    "simulation separately checks historical scenario support."
)


# =====================================================================
# 8. Secondary probability systems
# =====================================================================

st.subheader("8. Downstream Severity and Component Systems")

st.markdown(
    """
    The binary damage model is the primary probability system.
    Severity and component models are downstream conditional systems
    and are used only because their own Notebook 07/08 decision gates
    permitted them.
    """
)

if secondary_status is not None and not secondary_status.empty:

    st.dataframe(
        secondary_status,
        use_container_width=True,
        hide_index=True,
    )

else:

    st.markdown(
        """
        **Severity:** simplified known-severity binary system,
        S + D versus M, conditional on a reported damaging strike with
        usable severity information.

        **Retained components:** engine damage, wing/rotor damage,
        forward-cockpit damage, landing-gear damage, and propeller
        damage. These component probabilities are conditional on
        aircraft damage and are not mutually exclusive.
        """
    )


# =====================================================================
# 9. Monte Carlo trust decision
# =====================================================================

st.subheader("9. Suitability for Simulation")

st.success("Notebook 06 decision: PASS WITH WARNINGS")

st.markdown(
    """
    The calibrated damage-probability system was retained for
    scenario-based Monte Carlo simulation because its probability
    quality and future-period behavior were considered adequate for
    the project's operational purpose.

    The warning remains important: unseen airports, rare groups,
    low-support combinations, reporting changes, and future
    distribution shift should not be presented with the same confidence
    as well-supported historical scenarios.
    """
)

if trust_evidence is not None and not trust_evidence.empty:

    with st.expander(
        "Notebook 06 Monte Carlo decision evidence",
        expanded=False,
    ):
        st.dataframe(
            trust_evidence,
            use_container_width=True,
            hide_index=True,
        )


# =====================================================================
# 10. Interpretation boundaries
# =====================================================================

with st.expander(
    "How to interpret this page",
    expanded=False,
):

    st.markdown(
        """
        - The primary probability is **P(reported aircraft damage |
          reported wildlife strike scenario)**.
        - It is **not** the probability that a normal flight will
          experience a wildlife strike.
        - SHAP and permutation importance describe model behavior, not
          causal aviation mechanisms.
        - The locked classification threshold is a reporting reference,
          not an operational safety policy.
        - Calibration improves probability interpretation but cannot
          remove distribution shift or reporting bias.
        - Historical-support counts measure data coverage, not physical
          plausibility or statistical certainty.
        - Severity and component probabilities are conditional
          downstream quantities and must not be interpreted as
          unconditional outcomes across all strikes.
        """
    )
