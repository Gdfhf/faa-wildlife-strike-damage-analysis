import numpy as np
import pandas as pd

from src.models.loaders import (
    load_damage_model,
    load_severity_model,
    load_all_component_models,
)


def _positive_probability(model, X: pd.DataFrame) -> np.ndarray:
    """
    Return P(class=1) from a fitted binary classifier.
    """
    probabilities = model.predict_proba(X)

    return np.asarray(
        probabilities[:, 1],
        dtype=float,
    )


def _apply_artifact_calibration(
    system: dict,
    raw_probabilities: np.ndarray,
) -> np.ndarray:
    """
    Apply the calibration method stored in a severity/component
    probability-system artifact.

    'raw' means the base pipeline probability is already the
    probability used downstream.
    """
    method = system["calibration_method"]

    if method == "raw":
        return np.asarray(
            raw_probabilities,
            dtype=float,
        )

    calibrator = system.get("calibrator")

    if calibrator is None:
        raise ValueError(
            f"Artifact specifies calibration method '{method}' "
            "but contains no calibrator."
        )

    return np.asarray(
        calibrator.predict(raw_probabilities),
        dtype=float,
    )


class PredictionService:
    """
    Unified probability interface for the final damage, severity,
    and retained component probability systems.
    """

    def __init__(self):
        self.damage_model = load_damage_model()
        self.severity_system = load_severity_model()
        self.component_systems = load_all_component_models()

    def predict_damage_probability(
        self,
        scenario_rows: pd.DataFrame,
    ) -> np.ndarray:
        """
        Estimate P(damage | scenario inputs).
        """
        features = list(
            self.damage_model.feature_names_in_
        )

        X = scenario_rows[features]

        return _positive_probability(
            self.damage_model,
            X,
        )

    def predict_severity_probability(
        self,
        scenario_rows: pd.DataFrame,
    ) -> np.ndarray:
        """
        Estimate the conditional known-severity probability.

        This system is evaluated downstream only for simulated
        damaged cases.
        """
        system = self.severity_system
        features = system["features"]

        X = scenario_rows[features]

        raw = _positive_probability(
            system["base_pipeline"],
            X,
        )

        return _apply_artifact_calibration(
            system,
            raw,
        )

    def predict_component_probability(
        self,
        component: str,
        scenario_rows: pd.DataFrame,
    ) -> np.ndarray:
        """
        Estimate a retained component-damage probability,
        conditional on aircraft damage having occurred.
        """
        if component not in self.component_systems:
            raise ValueError(
                f"Unknown component: {component}"
            )

        system = self.component_systems[component]

        if system.get("decision") != "MODELLED":
            raise ValueError(
                f"Component '{component}' is not approved "
                "for simulation."
            )

        features = system["features"]

        X = scenario_rows[features]

        raw = _positive_probability(
            system["base_pipeline"],
            X,
        )

        return _apply_artifact_calibration(
            system,
            raw,
        )

    def predict_all_component_probabilities(
        self,
        scenario_rows: pd.DataFrame,
    ) -> dict[str, np.ndarray]:
        """
        Estimate probabilities for all retained component systems.
        """
        return {
            component: self.predict_component_probability(
                component,
                scenario_rows,
            )
            for component in self.component_systems
        }