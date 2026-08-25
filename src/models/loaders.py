import __main__
import joblib
import numpy as np

from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression

from src.utils.paths import (
    DAMAGE_MODEL_PATH,
    SEVERITY_MODEL_PATH,
    COMPONENT_MODEL_DIR,
)


SEED = 42


class BinaryProbabilityCalibrator:
    """
    Compatibility class required to deserialize the final
    Notebook 08 component probability-system artifacts.

    The original artifacts were saved when this class existed
    in the notebook's __main__ namespace.
    """

    def __init__(self, method="sigmoid"):
        self.method = method
        self.model = None

    def fit(self, raw_probabilities, y):
        p = np.asarray(raw_probabilities, dtype=float)
        y = np.asarray(y, dtype=int)

        if self.method == "sigmoid":
            self.model = LogisticRegression(
                solver="lbfgs",
                random_state=SEED,
            )

            self.model.fit(
                p.reshape(-1, 1),
                y,
            )

        else:
            self.model = IsotonicRegression(
                out_of_bounds="clip"
            )

            self.model.fit(p, y)

        return self

    def predict(self, raw_probabilities):
        p = np.asarray(
            raw_probabilities,
            dtype=float,
        )

        if self.method == "sigmoid":
            return self.model.predict_proba(
                p.reshape(-1, 1)
            )[:, 1]

        return np.asarray(
            self.model.predict(p),
            dtype=float,
        )


COMPONENT_MODEL_FILES = {
    "engine_damage":
        "engine_damage_component_probability_system.joblib",

    "forward_cockpit_damage":
        "forward_cockpit_damage_component_probability_system.joblib",

    "landing_gear_damage":
        "landing_gear_damage_component_probability_system.joblib",

    "propeller_damage":
        "propeller_damage_component_probability_system.joblib",

    "wing_rotor_damage":
        "wing_rotor_damage_component_probability_system.joblib",
}


def _register_serialization_compatibility():
    """
    Expose notebook-defined compatibility classes under __main__
    so legacy joblib component artifacts can be deserialized.
    """
    if not hasattr(
        __main__,
        "BinaryProbabilityCalibrator",
    ):
        __main__.BinaryProbabilityCalibrator = (
            BinaryProbabilityCalibrator
        )


def load_damage_model():
    """Load the final calibrated binary damage model."""
    if not DAMAGE_MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Damage model not found: {DAMAGE_MODEL_PATH}"
        )

    return joblib.load(DAMAGE_MODEL_PATH)


def load_severity_model():
    """Load the final known-severity probability system."""
    if not SEVERITY_MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Severity model not found: {SEVERITY_MODEL_PATH}"
        )

    return joblib.load(SEVERITY_MODEL_PATH)


def load_component_model(component: str):
    """
    Load one final component probability system.

    Registers the Notebook 08 calibration compatibility class
    before deserialization.
    """
    if component not in COMPONENT_MODEL_FILES:
        raise ValueError(
            f"Unknown component model: {component}"
        )

    model_path = (
        COMPONENT_MODEL_DIR
        / COMPONENT_MODEL_FILES[component]
    )

    if not model_path.exists():
        raise FileNotFoundError(
            f"Component model not found: {model_path}"
        )

    _register_serialization_compatibility()

    return joblib.load(model_path)


def load_all_component_models():
    """Load all retained final component probability systems."""
    return {
        component: load_component_model(component)
        for component in COMPONENT_MODEL_FILES
    }