from functools import lru_cache
import json

import pandas as pd

from src.utils.paths import (
    HISTORICAL_EXPLORER_PATH,
    SIMULATION_DONOR_POOL_PATH,
    SCENARIO_SUPPORT_PATH,
    OVERVIEW_SUMMARY_PATH,
)


def _require_file(path):
    if not path.exists():
        raise FileNotFoundError(
            f"Required dashboard artifact was not found:\n{path}\n\n"
            "Run:\n"
            "python -m src.data.build_dashboard_artifacts"
        )


@lru_cache(maxsize=1)
def load_historical_data():
    _require_file(HISTORICAL_EXPLORER_PATH)
    return pd.read_parquet(HISTORICAL_EXPLORER_PATH)


@lru_cache(maxsize=1)
def load_simulation_donors():
    _require_file(SIMULATION_DONOR_POOL_PATH)
    return pd.read_parquet(SIMULATION_DONOR_POOL_PATH)


@lru_cache(maxsize=1)
def load_scenario_support():
    _require_file(SCENARIO_SUPPORT_PATH)
    return pd.read_parquet(SCENARIO_SUPPORT_PATH)


@lru_cache(maxsize=1)
def load_overview_summary():
    _require_file(OVERVIEW_SUMMARY_PATH)

    with open(OVERVIEW_SUMMARY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def clear_data_caches():
    load_historical_data.cache_clear()
    load_simulation_donors.cache_clear()
    load_scenario_support.cache_clear()
    load_overview_summary.cache_clear()