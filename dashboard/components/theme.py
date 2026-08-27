"""Global visual styling for the Streamlit dashboard."""

from __future__ import annotations

import streamlit as st


GLOBAL_CSS = """
<style>

/* ---------------------------------------------------------
   Main application
   --------------------------------------------------------- */

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}


/* ---------------------------------------------------------
   Typography
   --------------------------------------------------------- */

.page-description {
    font-size: 1.05rem;
    line-height: 1.6;
    opacity: 0.75;
    margin-top: -0.5rem;
    margin-bottom: 2rem;
}


/* ---------------------------------------------------------
   Mobile adjustments
   --------------------------------------------------------- */

@media (max-width: 768px) {

    .block-container {
        padding-top: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .page-description {
        font-size: 0.95rem;
    }
}

/* ---------------------------------------------------------
   Internal page links
   --------------------------------------------------------- */

div[data-testid="stPageLink"] a {
    border: 1px solid rgba(128, 128, 128, 0.35);
    border-radius: 0.5rem;
    padding: 0.55rem 0.75rem;
    margin-bottom: 0.35rem;
    transition:
        border-color 0.15s ease,
        background-color 0.15s ease,
        transform 0.15s ease;
}

div[data-testid="stPageLink"] a:hover {
    border-color: var(--primary-color);
    background-color: color-mix(
        in srgb,
        var(--primary-color) 10%,
        transparent
    );
    transform: translateX(2px);
}

div[data-testid="stPageLink"] a p {
    color: var(--primary-color);
    font-weight: 600;
}


</style>
"""


def apply_global_theme() -> None:
    """Apply dashboard-wide visual styling."""

    st.markdown(
        GLOBAL_CSS,
        unsafe_allow_html=True,
    )