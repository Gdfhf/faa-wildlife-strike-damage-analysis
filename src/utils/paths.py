from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

MODELS_DIR = PROJECT_ROOT / "models"
FINAL_MODELS_DIR = MODELS_DIR / "final"

OUTPUTS_DIR = PROJECT_ROOT / "outputs"


# Data
ANALYTICAL_DATA_PATH = (
    PROCESSED_DATA_DIR / "faa_strikes_analytical.csv"
)

BINARY_MODEL_DATA_PATH = (
    PROCESSED_DATA_DIR / "faa_strikes_binary_model.csv"
)

BINARY_MODEL_READY_PATH = (
    PROCESSED_DATA_DIR / "faa_strikes_binary_model_ready.csv"
)


# Final models
DAMAGE_MODEL_PATH = (
    FINAL_MODELS_DIR
    / "06_calibration_validation"
    / "final_calibrated_pipeline.joblib"
)

SEVERITY_MODEL_PATH = (
    FINAL_MODELS_DIR
    / "07_severity_modelling"
    / "final_known_severity_probability_system.joblib"
)

COMPONENT_MODEL_DIR = (
    FINAL_MODELS_DIR
    / "08_component_modelling"
)


# Metadata
DAMAGE_OUTPUT_DIR = OUTPUTS_DIR / "06_calibration_validation"
SEVERITY_OUTPUT_DIR = OUTPUTS_DIR / "07_severity_modelling"
COMPONENT_OUTPUT_DIR = OUTPUTS_DIR / "08_component_modelling"
SIMULATION_OUTPUT_DIR = OUTPUTS_DIR / "10_simulation_analysis"

SCENARIO_SCHEMA_PATH = (
    SIMULATION_OUTPUT_DIR / "scenario_input_schema.json"
)