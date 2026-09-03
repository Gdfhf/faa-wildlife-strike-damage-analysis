"""Runtime configuration shared by local and hosted deployments."""

from __future__ import annotations

import os


DEFAULT_MAX_MONTE_CARLO_TRIALS = 100_000


def get_max_monte_carlo_trials() -> int:
    """Return the configured upper limit for interactive simulation runs."""
    raw_value = os.getenv(
        "CAPSTONE_MAX_MONTE_CARLO_TRIALS",
        str(DEFAULT_MAX_MONTE_CARLO_TRIALS),
    )

    try:
        value = int(raw_value)
    except ValueError:
        return DEFAULT_MAX_MONTE_CARLO_TRIALS

    return max(100, value)


def debug_errors_enabled() -> bool:
    """Return whether detailed exception traces should be shown in the UI."""
    return (
        os.getenv("CAPSTONE_DEBUG_ERRORS", "")
        .strip()
        .lower()
        in {"1", "true", "yes", "on"}
    )