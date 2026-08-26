"""Reusable display-label helpers for coded project fields."""

from __future__ import annotations

import pandas as pd


AIRCRAFT_CLASS_LABELS = {
    "A": "Airplane",
    "B": "Helicopter",
    "C": "Glider",
    "D": "Balloon",
    "F": "Dirigible",
    "I": "Gyroplane",
    "J": "Ultralight",
    "Y": "Other",
    "Z": "Unknown",
}


def format_aircraft_class(code: str) -> str:
    """Return a readable aircraft-class label while preserving the code."""
    code = str(code).strip()

    return f"{code} — {AIRCRAFT_CLASS_LABELS.get(code, 'Unknown')}"


def build_airport_labels(
    data: pd.DataFrame,
) -> dict[str, str]:
    """
    Build a mapping from AIRPORT_ID to a readable ID + airport-name label.

    Example:
        KDEN -> KDEN — DENVER INTERNATIONAL AIRPORT
    """
    if "AIRPORT_ID" not in data.columns:
        return {}

    airport_data = data[["AIRPORT_ID"]].copy()

    airport_data["AIRPORT_ID"] = (
        airport_data["AIRPORT_ID"]
        .astype("string")
        .fillna("")
        .str.strip()
    )

    if "AIRPORT" in data.columns:
        airport_data["AIRPORT"] = (
            data["AIRPORT"]
            .astype("string")
            .fillna("")
            .str.strip()
        )
    else:
        airport_data["AIRPORT"] = ""

    airport_data = airport_data[
        airport_data["AIRPORT_ID"] != ""
    ]

    labels: dict[str, str] = {}

    for airport_id, group in airport_data.groupby("AIRPORT_ID"):
        names = group["AIRPORT"]
        names = names[names != ""]

        if not names.empty:
            modes = names.mode()

            airport_name = (
                modes.iloc[0]
                if not modes.empty
                else names.iloc[0]
            )

            labels[airport_id] = (
                f"{airport_id} — {airport_name}"
            )

        else:
            labels[airport_id] = airport_id

    return labels