from dataclasses import dataclass, asdict
from typing import Any


REQUIRED_USER_FIELDS = [
    "AC_CLASS",
    "AC_MASS_GROUP",
    "SEASON",
    "PHASE_OF_FLIGHT",
]

GEOGRAPHY_FIELDS = [
    "AIRPORT_ID",
    "FAAREGION",
]

OPTIONAL_USER_FIELDS = [
    "WILDLIFE_TYPE",
    "SIZE",
    "NUM_STRUCK",
    "TYPE_ENG",
    "NUM_ENGS",
    "WARNED",
    "HEIGHT",
    "SPEED",
    "TIME_OF_DAY",
    "SKY",
    "PRECIPITATION",
    "STATE",
]


@dataclass
class Scenario:
    # Required aircraft / temporal / flight context
    ac_class: str
    ac_mass_group: str
    season: str
    phase_of_flight: str

    # Geography: at least one is required
    airport_id: str | None = None
    faa_region: str | None = None

    # Optional scenario context
    wildlife_type: str | None = None
    size: str | None = None
    num_struck: int | None = None

    type_eng: str | None = None
    num_engs: float | None = None
    warned: str | None = None

    height: float | None = None
    speed: float | None = None

    time_of_day: str | None = None
    sky: str | None = None
    precipitation: str | None = None
    state: str | None = None

    def validate(self) -> None:
        """
        Validate the structural requirements of a scenario.

        Historical support is checked separately by SupportEvaluator.
        """
        errors = []

        required_values = {
            "AC_CLASS": self.ac_class,
            "AC_MASS_GROUP": self.ac_mass_group,
            "SEASON": self.season,
            "PHASE_OF_FLIGHT": self.phase_of_flight,
        }

        for field, value in required_values.items():
            if value is None or str(value).strip() == "":
                errors.append(f"{field} is required.")

        if not self.airport_id and not self.faa_region:
            errors.append(
                "A scenario requires either AIRPORT_ID or FAAREGION."
            )

        if self.num_struck is not None and self.num_struck < 0:
            errors.append("NUM_STRUCK cannot be negative.")

        if self.num_engs is not None and self.num_engs < 0:
            errors.append("NUM_ENGS cannot be negative.")

        if self.height is not None and self.height < 0:
            errors.append("HEIGHT cannot be negative.")

        if self.speed is not None and self.speed < 0:
            errors.append("SPEED cannot be negative.")

        if errors:
            raise ValueError(
                "Invalid scenario:\n- " + "\n- ".join(errors)
            )

    @property
    def geography_level(self) -> str:
        """
        Return the geographic level controlling the scenario.

        Airport takes precedence when both are supplied.
        """
        if self.airport_id:
            return "airport"

        if self.faa_region:
            return "region"

        return "missing"

    def to_model_overrides(self) -> dict[str, Any]:
        """
        Convert the user-facing Scenario object into analytical
        column names used by the simulation/model pipeline.

        Fields with value None are omitted so the donor sampler
        can fill them empirically.
        """
        values = {
            "AIRPORT_ID": self.airport_id,
            "FAAREGION": self.faa_region,
            "AC_CLASS": self.ac_class,
            "AC_MASS_GROUP": self.ac_mass_group,
            "SEASON": self.season,
            "PHASE_OF_FLIGHT": self.phase_of_flight,
            "WILDLIFE_TYPE": self.wildlife_type,
            "SIZE": self.size,
            "NUM_STRUCK": self.num_struck,
            "TYPE_ENG": self.type_eng,
            "NUM_ENGS": self.num_engs,
            "WARNED": self.warned,
            "HEIGHT": self.height,
            "SPEED": self.speed,
            "TIME_OF_DAY": self.time_of_day,
            "SKY": self.sky,
            "PRECIPITATION": self.precipitation,
            "STATE": self.state,
        }

        return {
            key: value
            for key, value in values.items()
            if value is not None
        }

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)