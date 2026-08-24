import joblib

from src.utils.paths import (
    DAMAGE_MODEL_PATH,
    SEVERITY_MODEL_PATH,
    COMPONENT_MODEL_DIR,
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
    """Load one final component probability system."""
    if component not in COMPONENT_MODEL_FILES:
        raise ValueError(
            f"Unknown component model: {component}"
        )

    model_path = COMPONENT_MODEL_DIR / COMPONENT_MODEL_FILES[component]

    if not model_path.exists():
        raise FileNotFoundError(
            f"Component model not found: {model_path}"
        )

    return joblib.load(model_path)