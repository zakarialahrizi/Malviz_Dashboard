"""
utils/ui_helpers.py — CSS partagé et helpers UI.
"""

from pathlib import Path
import streamlit as st

PRIMARY   = "#005DA1"
SECONDARY = "#3B8B85"
MALWARE   = "#C0392B"
BENIGN    = "#27AE60"
UNCERTAIN = "#E67E22"

MALVIZ_DIR = Path(__file__).resolve().parent.parent


def inject_css() -> None:
    """CSS minimal partagé entre toutes les pages."""
    st.markdown(f"""
<style>
/* ── Métriques ── */
[data-testid="metric-container"] {{
    background   : rgba(0, 93, 161, 0.10);
    border       : 1px solid rgba(0, 93, 161, 0.28);
    border-radius: 10px;
    padding      : 16px 20px;
}}
[data-testid="metric-container"] label {{
    color          : {SECONDARY} !important;
    font-size      : 0.75rem;
    text-transform : uppercase;
    letter-spacing : 0.06em;
}}
[data-testid="metric-container"] [data-testid="metric-value"] {{
    color       : #E6EDF3 !important;
    font-size   : 1.8rem;
    font-weight : 700;
}}

/* ── Logo sidebar centré ── */
[data-testid="stSidebarHeader"] {{
    display         : flex;
    justify-content : center;
    padding         : 1.2rem 0 0.8rem 0;
}}
[data-testid="stSidebarHeader"] img {{
    max-width : 110px !important;
    width     : 110px !important;
}}
</style>
""", unsafe_allow_html=True)


def page_title(text: str) -> None:
    st.markdown(
        f"<h1 style='color:{PRIMARY};margin-bottom:4px'>{text}</h1>",
        unsafe_allow_html=True,
    )
