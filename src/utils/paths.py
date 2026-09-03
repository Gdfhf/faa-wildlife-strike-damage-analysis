from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
DASHBOARD_DATA_DIR = DATA_DIR / "dashboard"

MODELS_DIR = PROJECT_ROOT / "models"
FINAL_MODELS_DIR = MODELS_DIR / "final"

OUTPUTS_DIR = PROJECT_ROOT / "outputs"

GODOT_DIR = PROJECT_ROOT / "godot"

SIMULATION_DIR = PROJECT_ROOT / "simulation"
WEB_VISUALIZER_DIR = (
    SIMULATION_DIR / "web_visualizer"
)


# =====================================================================
# Data
# =====================================================================

ANALYTICAL_DATA_PATH = (
    PROCESSED_DATA_DIR / "faa_strikes_analytical.csv"
)

BINARY_MODEL_DATA_PATH = (
    PROCESSED_DATA_DIR / "faa_strikes_binary_model.csv"
)

BINARY_MODEL_READY_PATH = (
    PROCESSED_DATA_DIR / "faa_strikes_binary_model_ready.csv"
)

HISTORICAL_EXPLORER_PATH = (
    DASHBOARD_DATA_DIR / "historical_explorer.parquet"
)

SIMULATION_DONOR_POOL_PATH = (
    DASHBOARD_DATA_DIR / "simulation_donor_pool.parquet"
)

SCENARIO_SUPPORT_PATH = (
    DASHBOARD_DATA_DIR / "scenario_support.parquet"
)

OVERVIEW_SUMMARY_PATH = (
    DASHBOARD_DATA_DIR / "overview_summary.json"
)


# =====================================================================
# Final models
# =====================================================================

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


# =====================================================================
# Metadata
# =====================================================================

DAMAGE_OUTPUT_DIR = (
    OUTPUTS_DIR / "06_calibration_validation"
)

SEVERITY_OUTPUT_DIR = (
    OUTPUTS_DIR / "07_severity_modelling"
)

COMPONENT_OUTPUT_DIR = (
    OUTPUTS_DIR / "08_component_modelling"
)

SIMULATION_OUTPUT_DIR = (
    OUTPUTS_DIR / "10_simulation_analysis"
)

SCENARIO_SCHEMA_PATH = (
    SIMULATION_OUTPUT_DIR / "scenario_input_schema.json"
)


# =====================================================================
# Godot visualization
# =====================================================================

GODOT_TRIAL_PATH = (
    GODOT_DIR
    / "data"
    / "latest_trial.json"
)

GODOT_BUILD_PATH = (
    GODOT_DIR
    / "builds"
    / "CapstoneAirstrikeVisualizer.exe"
)

GODOT_WEB_URL = (
    "https://gdfhf.github.io/"
    "faa-wildlife-strike-damage-analysis/"
)