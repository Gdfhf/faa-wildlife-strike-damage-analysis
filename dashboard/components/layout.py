"""Shared layout helpers for the Streamlit dashboard."""

from __future__ import annotations

import streamlit as st


def page_header(
    title: str,
    description: str | None = None,
) -> None:
    """Render the standard heading used at the top of dashboard pages."""

    st.title(title)

    if description:
        st.markdown(
            f'<p class="page-description">{description}</p>',
            unsafe_allow_html=True,
        )


def section_header(
    title: str,
    description: str | None = None,
) -> None:
    """Render a consistent dashboard section heading."""

    st.subheader(title)

    if description:
        st.caption(description)


def section_divider() -> None:
    """Render the standard divider between major page sections."""

    st.divider()