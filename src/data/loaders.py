import json

import pandas as pd

from src.utils.paths import (
    ANALYTICAL_DATA_PATH,
    SCENARIO_SCHEMA_PATH,
)


def load_analytical_data() -> pd.DataFrame:
    """Load the processed analytical FAA wildlife strike dataset."""
    if not ANALYTICAL_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Analytical dataset not found: {ANALYTICAL_DATA_PATH}"
        )

    return pd.read_csv(
        ANALYTICAL_DATA_PATH,
        low_memory=False
    )


def load_scenario_schema() -> dict:
    """Load the input schema defined by Notebook 10."""
    if not SCENARIO_SCHEMA_PATH.exists():
        raise FileNotFoundError(
            f"Scenario schema not found: {SCENARIO_SCHEMA_PATH}"
        )

    with open(SCENARIO_SCHEMA_PATH, "r", encoding="utf-8") as file:
        return json.load(file)