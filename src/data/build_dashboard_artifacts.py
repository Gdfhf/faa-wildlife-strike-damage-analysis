from pathlib import Path
import json

import pandas as pd

from src.utils.paths import (
    FAA_ANALYTICAL_DATA_PATH,
    DASHBOARD_DATA_DIR,
)

# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SOURCE_PATH = FAA_ANALYTICAL_DATA_PATH
OUTPUT_DIR = DASHBOARD_DATA_DIR


# ---------------------------------------------------------
# Dashboard artifact schemas
# ---------------------------------------------------------

HISTORICAL_EXPLORER_COLUMNS = [
    "INDEX_NR",
    "INCIDENT_DATE",
    "INCIDENT_MONTH",
    "INCIDENT_YEAR",
    "SEASON",
    "TIME_OF_DAY",

    "AIRPORT_ID",
    "AIRPORT",
    "AIRPORT_LATITUDE",
    "AIRPORT_LONGITUDE",
    "STATE",
    "FAAREGION",

    "AIRCRAFT",
    "AC_CLASS",
    "AC_MASS",
    "AC_MASS_GROUP",
    "TYPE_ENG",
    "NUM_ENGS",

    "PHASE_OF_FLIGHT",
    "HEIGHT",
    "SPEED",
    "SKY",
    "PRECIPITATION",

    "SPECIES",
    "WILDLIFE_TYPE",
    "SIZE",
    "NUM_SEEN",
    "NUM_STRUCK",

    "INDICATED_DAMAGE",
    "DAMAGE_LEVEL",
    "NR_INJURIES",
    "NR_FATALITIES",

    "DAM_RAD",
    "DAM_WINDSHLD",
    "DAM_NOSE",
    "DAM_ENG1",
    "DAM_ENG2",
    "DAM_ENG3",
    "DAM_ENG4",
    "DAM_PROP",
    "DAM_WING_ROT",
    "DAM_FUSE",
    "DAM_LG",
    "DAM_TAIL",
    "DAM_LGHTS",
    "DAM_OTHER",

    "TEMPORAL_SPLIT",
]


SIMULATION_DONOR_COLUMNS = [
    "INDEX_NR",

    "AIRPORT_ID",
    "AIRPORT",
    "STATE",
    "FAAREGION",

    "AIRCRAFT",
    "AC_CLASS",
    "AC_MASS",
    "AC_MASS_GROUP",
    "TYPE_ENG",
    "NUM_ENGS",
    
    "WARNED",

    "INCIDENT_MONTH",
    "INCIDENT_YEAR",
    "SEASON",
    "TIME_OF_DAY",

    "PHASE_OF_FLIGHT",

    "HEIGHT",
    "SPEED",

    "SKY",
    "PRECIPITATION",

    "SPECIES",
    "WILDLIFE_TYPE",
    "SIZE",
    "NUM_SEEN",
    "NUM_STRUCK",

    "MONTH_SIN",
    "MONTH_COS",

    "HEIGHT_MISSING_FLAG",
    "SPEED_MISSING_FLAG",
    "TIME_OF_DAY_MISSING_FLAG",
    "PHASE_OF_FLIGHT_MISSING_FLAG",
    "SIZE_MISSING_FLAG",
    "SKY_MISSING_FLAG",
    "PRECIPITATION_MISSING_FLAG",

    "TEMPORAL_SPLIT",
]


SCENARIO_SUPPORT_COLUMNS = [
    "AIRPORT_ID",
    "AIRPORT",
    "STATE",
    "FAAREGION",

    "AC_CLASS",
    "AC_MASS_GROUP",

    "SEASON",
    "TIME_OF_DAY",
    "PHASE_OF_FLIGHT",

    "WILDLIFE_TYPE",
    "SIZE",

    "TEMPORAL_SPLIT",
]


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def validate_columns(df, required_columns, artifact_name):
    missing = [col for col in required_columns if col not in df.columns]

    if missing:
        raise ValueError(
            f"{artifact_name} is missing required columns:\n"
            + "\n".join(missing)
        )


def print_artifact_info(path, df):
    size_mb = path.stat().st_size / (1024 * 1024)

    print(f"\nCreated: {path.name}")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns):,}")
    print(f"File size: {size_mb:.2f} MB")


# ---------------------------------------------------------
# Main build
# ---------------------------------------------------------

def main():
    print("Building dashboard artifacts...")
    print(f"Source: {SOURCE_PATH}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not SOURCE_PATH.exists():
        raise FileNotFoundError(
            f"Analytical dataset was not found at:\n{SOURCE_PATH}"
        )

    # Load canonical analytical dataset once
    df = pd.read_csv(SOURCE_PATH, low_memory=False)

    print(f"\nSource rows: {len(df):,}")
    print(f"Source columns: {len(df.columns):,}")

    # Convert the date to a proper datetime type
    df["INCIDENT_DATE"] = pd.to_datetime(
        df["INCIDENT_DATE"],
        errors="coerce"
    )

    # -----------------------------------------------------
    # Historical Explorer
    # -----------------------------------------------------

    validate_columns(
        df,
        HISTORICAL_EXPLORER_COLUMNS,
        "historical_explorer"
    )

    historical = df[HISTORICAL_EXPLORER_COLUMNS].copy()

    historical_path = (
        OUTPUT_DIR / "historical_explorer.parquet"
    )

    historical.to_parquet(
        historical_path,
        index=False
    )

    print_artifact_info(
        historical_path,
        historical
    )

    # -----------------------------------------------------
    # Simulation Donor Pool
    # -----------------------------------------------------

    validate_columns(
        df,
        SIMULATION_DONOR_COLUMNS,
        "simulation_donor_pool"
    )

    donors = (
        df.loc[
            df["INCIDENT_YEAR"].le(2021),
            SIMULATION_DONOR_COLUMNS
        ]
        .copy()
    )

    donor_path = (
        OUTPUT_DIR / "simulation_donor_pool.parquet"
    )

    donors.to_parquet(
        donor_path,
        index=False
    )

    print_artifact_info(
        donor_path,
        donors
    )

    # -----------------------------------------------------
    # Scenario Support
    # -----------------------------------------------------

    validate_columns(
        df,
        SCENARIO_SUPPORT_COLUMNS,
        "scenario_support"
    )

    support = (
        df.loc[
            df["INCIDENT_YEAR"].le(2021),
            SCENARIO_SUPPORT_COLUMNS
        ]
        .copy()
    )

    support_path = (
        OUTPUT_DIR / "scenario_support.parquet"
    )

    support.to_parquet(
        support_path,
        index=False
    )

    print_artifact_info(
        support_path,
        support
    )

    # -----------------------------------------------------
    # Overview Summary
    # -----------------------------------------------------

    overview = {
        "n_records": int(len(df)),
        "start_year": int(df["INCIDENT_YEAR"].min()),
        "end_year": int(df["INCIDENT_YEAR"].max()),
        "n_airports": int(df["AIRPORT_ID"].nunique()),
        "n_species": int(df["SPECIES"].nunique()),
        "n_damaged": int(df["INDICATED_DAMAGE"].sum()),
        "damage_rate": float(df["INDICATED_DAMAGE"].mean()),
    }

    overview_path = OUTPUT_DIR / "overview_summary.json"

    with open(overview_path, "w", encoding="utf-8") as f:
        json.dump(
            overview,
            f,
            indent=2
        )

    print(f"\nCreated: {overview_path.name}")

    # -----------------------------------------------------
    # Finish
    # -----------------------------------------------------

    print("\nDashboard artifact build complete.")


if __name__ == "__main__":
    main()