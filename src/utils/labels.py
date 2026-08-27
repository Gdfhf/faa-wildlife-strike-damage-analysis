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

ENGINE_TYPE_LABELS = {
    "A": "Reciprocating / piston",
    "B": "Turbojet",
    "C": "Turboprop",
    "D": "Turbofan",
    "E": "None / glider",
    "F": "Turboshaft / helicopter",
    "Y": "Other",
}


def format_engine_type(code: str) -> str:
    """Return a readable aircraft-engine label while preserving the code."""
    code = str(code).strip()

    return (
        f"{code} — "
        f"{ENGINE_TYPE_LABELS.get(code, 'Unknown')}"
    )
    
STATE_LABELS = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming",
    "DC": "District of Columbia",
    "PR": "Puerto Rico",
    "VI": "U.S. Virgin Islands",
    "GU": "Guam",
}

STATE_LABELS.update({
    # Canadian provinces
    "AB": "Alberta",
    "BC": "British Columbia",
    "MB": "Manitoba",
    "NL": "Newfoundland and Labrador",
    "NS": "Nova Scotia",
    "ON": "Ontario",
    "QC": "Quebec",
    "SK": "Saskatchewan",

    # U.S. territories / associated areas
    "AS": "American Samoa",
    "MH": "Marshall Islands",
    "MP": "Northern Mariana Islands",
    "UM": "U.S. Minor Outlying Islands",

    # Dataset-specific values
    "Not reported": "Not reported",
})


def format_state(code: str) -> str:
    """Return a readable state label while preserving the code."""
    code = str(code).strip().upper()

    label = STATE_LABELS.get(code)

    if label is None:
        return f"{code} — Unmapped code"

    return f"{code} — {label}"