"""Reusable metric displays for dashboard pages."""

from __future__ import annotations

import streamlit as st


def metric_row(
    metrics: list[tuple[str, str, str | None]],
) -> None:
    """
    Render a responsive row of dashboard metrics.

    Each metric is:
        (label, value, help_text)
    """

    columns = st.columns(
        len(metrics),
        gap="medium",
        border=True,
    )

    for column, (label, value, help_text) in zip(columns, metrics):
        with column:
            st.metric(
                label=label,
                value=value,
                help=help_text,
            )