from pathlib import Path
import json

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DASHBOARD_DIR = PROJECT_ROOT / "data" / "dashboard"


PARQUET_FILES = [
    "historical_explorer.parquet",
    "simulation_donor_pool.parquet",
    "scenario_support.parquet",
]


def inspect_parquet(filename):
    path = DASHBOARD_DIR / filename

    if not path.exists():
        raise FileNotFoundError(f"Missing artifact: {path}")

    df = pd.read_parquet(path)

    print("\n" + "=" * 70)
    print(filename)
    print("=" * 70)

    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns):,}")

    print("\nColumn names:")
    for col in df.columns:
        print(f"  - {col}")

    print("\nFirst 3 rows:")
    print(df.head(3).to_string())

    print("\nMissing values — top 10:")
    missing = df.isna().sum().sort_values(ascending=False).head(10)
    print(missing.to_string())

    print("\nDuplicate INDEX_NR:")

    if "INDEX_NR" in df.columns:
        print(df["INDEX_NR"].duplicated().sum())
    else:
        print("INDEX_NR not included in this artifact.")


def inspect_overview():
    path = DASHBOARD_DIR / "overview_summary.json"

    if not path.exists():
        raise FileNotFoundError(f"Missing artifact: {path}")

    with open(path, "r", encoding="utf-8") as f:
        overview = json.load(f)

    print("\n" + "=" * 70)
    print("overview_summary.json")
    print("=" * 70)

    for key, value in overview.items():
        print(f"{key}: {value}")


def main():
    print("Validating dashboard artifacts...")

    for filename in PARQUET_FILES:
        inspect_parquet(filename)

    inspect_overview()

    print("\nDashboard artifact validation complete.")


if __name__ == "__main__":
    main()