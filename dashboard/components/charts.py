"""Shared Plotly formatting helpers for the dashboard."""

from __future__ import annotations

import plotly.graph_objects as go


def apply_chart_layout(
    fig: go.Figure,
    *,
    height: int | None = None,
) -> go.Figure:
    """
    Apply shared presentation settings to dashboard Plotly figures.

    Colors are intentionally left to Plotly/Streamlit so charts remain
    compatible with both light and dark themes.
    """

    fig.update_layout(
        margin=dict(
            l=10,
            r=10,
            t=30,
            b=10,
        ),
        hovermode="x unified",
        legend_title_text=None,
    )

    if height is not None:
        fig.update_layout(height=height)

    return fig