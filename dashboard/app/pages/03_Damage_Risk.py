"""Damage-risk model performance and explainability page."""

from __future__ import annotations

from pathlib import Path
import json

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


# =====================================================================
# Portable project paths
# =====================================================================

def find_project_root() -> Path:
    """Find the repository root from the current working directory/page."""
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
def load_csv(path_string: str):
    path = Path(path_string)
    if not path.exists():
        return None
    return pd.read_csv(path)


@st.cache_data
def load_json(path_string: str):
    path = Path(path_string)
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def existing_image(directory: Path, filename: str):
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


def display_artifact_warning(name: str) -> None:
    st.info(
        f"{name} was not found in the expected output directory. "
        "The remaining sections will use the available Notebook 06/09 artifacts."
    )


def format_feature_name(value) -> str:
    return (
        str(value)
        .replace("_", " ")
        .title()
    )


def style_figure(fig, *, hovermode: str = "closest"):
    """Apply shared dashboard Plotly styling."""
    fig = apply_chart_layout(fig)
    fig.update_layout(hovermode=hovermode)
    return fig


PLOTLY_CONFIG = {
    "displaylogo": False,
    "responsive": True,
}


# =====================================================================
# Load artifacts
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
# Page introduction
# =====================================================================

page_header(
    "Damage Risk & Model Insights",
    (
        "Review the validated aircraft-damage probability system, its "
        "out-of-time performance, and the explainability evidence used "
        "to support the operational simulation."
    ),
)

st.caption(
    "The primary model estimates reported aircraft-damage probability "
    "conditional on a reported wildlife strike. This page reads saved "
    "Notebook 06 and 09 artifacts; it does not retrain models or recompute SHAP."
)


# =====================================================================
# Canonical model
# =====================================================================

section_divider()

section_header(
    "Canonical damage probability model",
    (
        "The approved probability system was selected, calibrated, and "
        "evaluated using a temporally separated workflow."
    ),
)

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

    metric_row(
        [
            (
                "Base candidate",
                "XGBoost",
                (
                    "Selected base damage model before final calibration. "
                    f"Artifact: {model_name}"
                ),
            ),
            (
                "Calibration",
                str(calibration).title(),
                "Probability-calibration method retained in Notebook 06.",
            ),
            (
                "Feature set",
                str(feature_set).replace("_", " ").title(),
                "Feature set used by the final probability system.",
            ),
            (
                "Input features",
                str(n_features),
                "Number of original inputs supplied to the final system.",
            ),
        ]
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
        f"Base fit: {base_period} · "
        f"Calibration/selection: {calibration_period} · "
        f"Locked final test: {final_period}"
    )

else:
    display_artifact_warning("Final model manifest")

st.info(
    "The Monte Carlo simulator uses the model's continuous damage "
    "probabilities directly. The classification threshold shown below "
    "is a validation reference, not an operational safety rule."
)

if metadata is not None:
    with st.expander(
        "Validation design and locked decisions",
        expanded=False,
    ):
        st.json(metadata)


# =====================================================================
# Final-test probability performance
# =====================================================================

section_divider()

section_header(
    "Locked final-test probability performance",
    (
        "These results come from the 2022–2024 out-of-time test period "
        "after model, calibration, and threshold choices had been locked."
    ),
)

if probability_metrics is not None and not probability_metrics.empty:

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

        final_row = (
            probability_metrics.iloc[-1]
            if final_rows.empty
            else final_rows.iloc[-1]
        )

        summary_metrics = []

        if pr_col is not None:
            summary_metrics.append(
                (
                    "Final PR-AUC",
                    f"{float(final_row[pr_col]):.3f}",
                    "Higher values indicate better discrimination for the uncommon damage outcome.",
                )
            )

        if brier_col is not None:
            summary_metrics.append(
                (
                    "Final Brier score",
                    f"{float(final_row[brier_col]):.4f}",
                    "Lower values indicate better probability accuracy.",
                )
            )

        if logloss_col is not None:
            summary_metrics.append(
                (
                    "Final log loss",
                    f"{float(final_row[logloss_col]):.4f}",
                    "Lower values indicate better probabilistic predictions, with stronger penalties for confident errors.",
                )
            )

        if summary_metrics:
            metric_row(summary_metrics)

    with st.expander(
        "View probability-metric table",
        expanded=False,
    ):
        st.dataframe(
            probability_metrics,
            use_container_width=True,
            hide_index=True,
        )

else:
    display_artifact_warning("Final-test probability metrics")

st.caption(
    "PR-AUC emphasizes discrimination for the relatively uncommon damage "
    "class. Brier score and log loss evaluate probability quality rather "
    "than only hard classifications."
)


# =====================================================================
# Locked-threshold classification reference
# =====================================================================

section_divider()

section_header(
    "Classification reference at the locked threshold",
    (
        "The threshold is retained for classification diagnostics and "
        "error analysis, not as a recommended aviation decision threshold."
    ),
)

st.warning(
    "Do not interpret the locked threshold as a safety rule. "
    "The simulation uses continuous calibrated probabilities."
)

confusion_path = existing_image(
    NB09_DIR,
    "09_locked_threshold_confusion_matrix.png",
)

classification_col, threshold_col = st.columns(
    [1.2, 1],
    gap="medium",
)

with classification_col:
    with st.container(border=True):
        st.markdown("#### Confusion matrix")

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
            st.write(
                "TN = 55,651 · FP = 1,322 · "
                "FN = 1,314 · TP = 932"
            )

with threshold_col:
    with st.container(border=True):
        st.markdown("#### Threshold metrics")

        if threshold_metrics is not None and not threshold_metrics.empty:
            st.dataframe(
                threshold_metrics,
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.metric("Locked F1 threshold", "0.20")
            st.metric("Precision", "≈ 41.35%")
            st.metric("Recall", "≈ 41.50%")

st.caption(
    "At threshold 0.20, false-positive and false-negative counts are similar. "
    "That reflects the validation-derived F1 trade-off rather than an "
    "accuracy-maximizing or safety-cost-based policy."
)


# =====================================================================
# Generalization evidence
# =====================================================================

section_divider()

section_header(
    "Temporal and geographic generalization",
    (
        "The final model was checked across future years, unseen airports, "
        "and different levels of historical support."
    ),
)

generalization_col1, generalization_col2 = st.columns(
    2,
    gap="medium",
)

with generalization_col1:
    with st.container(border=True):
        st.markdown("#### Performance by future year")

        if year_metrics is not None and not year_metrics.empty:

            year_col = find_column(
                year_metrics,
                ["INCIDENT_YEAR", "year"],
            )

            year_pr_col = find_column(
                year_metrics,
                ["pr_auc", "average_precision"],
            )

            if year_col is not None and year_pr_col is not None:

                year_chart = (
                    year_metrics[
                        [year_col, year_pr_col]
                    ]
                    .dropna()
                    .copy()
                )

                fig = px.line(
                    year_chart,
                    x=year_col,
                    y=year_pr_col,
                    markers=True,
                    labels={
                        year_col: "Year",
                        year_pr_col: "PR-AUC",
                    },
                )
                fig = style_figure(
                    fig,
                    hovermode="x unified",
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    config=PLOTLY_CONFIG,
                )

            with st.expander(
                "View yearly metrics",
                expanded=False,
            ):
                st.dataframe(
                    year_metrics,
                    use_container_width=True,
                    hide_index=True,
                )

        else:
            display_artifact_warning(
                "Final-test metrics by year"
            )

with generalization_col2:
    with st.container(border=True):
        st.markdown("#### Unseen-airport evaluation")

        if unseen_metrics is not None and not unseen_metrics.empty:
            st.dataframe(
                unseen_metrics,
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.write(
                "Notebook 06 retained explicit unseen-airport testing "
                "as part of the geographic generalization audit."
            )

st.caption(
    "Unseen-airport results should be read together with sample size, "
    "damage prevalence, and support. Small or unusual subsets can produce "
    "unstable metrics."
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
# Global explainability
# =====================================================================

section_divider()

section_header(
    "What drives the damage model?",
    (
        "Notebook 09 used complementary explainability methods to measure "
        "model reliance on the original scenario variables."
    ),
)

st.caption(
    "Grouped TreeSHAP measures attribution within the fitted model. "
    "Permutation importance measures held-out PR-AUC loss when an input "
    "is disrupted. Importance describes model reliance, not causation."
)

explain_col1, explain_col2 = st.columns(
    2,
    gap="medium",
)

with explain_col1:
    with st.container(border=True):
        st.markdown("#### Grouped SHAP importance")

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

                shap_chart = shap_chart.sort_values(
                    importance_col,
                    ascending=True,
                )

                fig = px.bar(
                    shap_chart,
                    x=importance_col,
                    y=feature_col,
                    orientation="h",
                    labels={
                        importance_col: "Mean |grouped SHAP|",
                        feature_col: "Feature",
                    },
                )
                fig = style_figure(fig)

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    config=PLOTLY_CONFIG,
                )

            with st.expander(
                "View grouped SHAP table",
                expanded=False,
            ):
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

with explain_col2:
    with st.container(border=True):
        st.markdown("#### Permutation importance")

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

                perm_chart = perm_chart.sort_values(
                    importance_col,
                    ascending=True,
                )

                fig = px.bar(
                    perm_chart,
                    x=importance_col,
                    y=feature_col,
                    orientation="h",
                    labels={
                        importance_col: "Mean PR-AUC drop",
                        feature_col: "Feature",
                    },
                )
                fig = style_figure(fig)

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    config=PLOTLY_CONFIG,
                )

            with st.expander(
                "View permutation table",
                expanded=False,
            ):
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
    "A feature can rank differently under SHAP and permutation importance "
    "because the methods answer different questions and correlated or "
    "redundant predictors can share information."
)


# =====================================================================
# Directional interpretation
# =====================================================================

section_divider()

section_header(
    "Direction of selected model effects",
    (
        "Global importance indicates how influential a feature is; "
        "directional SHAP views show which values tend to move the fitted "
        "damage score upward or downward."
    ),
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

st.caption(
    "Notebook 09 found particularly clear directional behavior for wildlife "
    "size: larger wildlife generally moved the fitted damage score upward "
    "while small wildlife moved it downward. These are conditional model "
    "effects and should not be described as causal physical effects."
)


# =====================================================================
# Airport-dependence audit
# =====================================================================

section_divider()

section_header(
    "Airport dependence audit",
    (
        "Exact airport identity can add predictive information, but it can "
        "also encourage the model to rely on persistent local patterns."
    ),
)

airport_text_col, airport_visual_col = st.columns(
    [1, 2],
    gap="medium",
)

with airport_text_col:
    if airport_dependence is not None and not airport_dependence.empty:
        st.dataframe(
            airport_dependence,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info(
            "Airport-dependence summary data were not found."
        )

with airport_visual_col:
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
    else:
        st.info(
            "Seen-versus-unseen airport explanation figure was not found."
        )

st.caption(
    "Unseen-airport evidence is useful but does not establish universal "
    "geographic generalization. This is one reason the simulator separately "
    "checks exact historical scenario support."
)


# =====================================================================
# Downstream probability systems
# =====================================================================

section_divider()

section_header(
    "Downstream severity and component systems",
    (
        "Severity and component models are conditional downstream systems, "
        "not replacements for the primary damage-probability model."
    ),
)

if secondary_status is not None and not secondary_status.empty:
    st.dataframe(
        secondary_status,
        use_container_width=True,
        hide_index=True,
    )
else:
    downstream_col1, downstream_col2 = st.columns(
        2,
        gap="medium",
    )

    with downstream_col1:
        with st.container(border=True):
            st.markdown("#### Severity")
            st.write(
                "Simplified known-severity binary system: "
                "S + D versus M, conditional on a reported damaging "
                "strike with usable severity information."
            )

    with downstream_col2:
        with st.container(border=True):
            st.markdown("#### Components")
            st.write(
                "Retained systems include engine, wing/rotor, "
                "forward-cockpit, landing-gear, and propeller damage. "
                "Component outcomes are not mutually exclusive."
            )


# =====================================================================
# Suitability for simulation
# =====================================================================

section_divider()

section_header(
    "Suitability for simulation",
    (
        "Notebook 06 explicitly evaluated whether the calibrated damage "
        "probability system was suitable for downstream Monte Carlo use."
    ),
)

st.success("Notebook 06 decision: PASS WITH WARNINGS")

st.write(
    "The calibrated system was retained because its probability quality "
    "and future-period behavior were considered adequate for the project's "
    "scenario-based operational purpose. Confidence should still be reduced "
    "for unseen airports, rare groups, low-support combinations, reporting "
    "changes, and future distribution shift."
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
# Interpretation boundaries
# =====================================================================

section_divider()

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
