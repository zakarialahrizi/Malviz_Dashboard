"""
utils/ui.py — Couleurs, CSS partagé et setup de page.
Importer dans chaque page pour garder le style cohérent.
"""

from pathlib import Path
import streamlit as st

# ── Palette fixe ──────────────────────────────────────────────────────────────
COLORS = {
    "primary":   "#005DA1",
    "secondary": "#3B8B85",
    "malware":   "#C0392B",
    "benign":    "#27AE60",
    "uncertain": "#E67E22",
    "bg":        "#0E1117",
    "card":      "#161C27",
}

# ── CSS minimal — métriques + cartes ─────────────────────────────────────────
_CSS = f"""
<style>
/* Metric cards */
[data-testid="metric-container"] {{
    background: rgba(0, 93, 161, 0.13);
    border: 1px solid rgba(0, 93, 161, 0.40);
    border-radius: 12px;
    padding: 16px 20px;
}}
[data-testid="metric-container"] label {{
    color: {COLORS['secondary']} !important;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    font-weight: 600;
}}
[data-testid="metric-container"] [data-testid="metric-value"] {{
    color: #ffffff !important;
    font-size: 2rem;
    font-weight: 700;
}}
/* Sidebar logo area */
[data-testid="stSidebarHeader"] {{
    padding-top: 1rem;
}}
/* Divider color */
hr {{
    border-color: rgba(0, 93, 161, 0.25) !important;
}}
</style>
"""


def setup_page() -> None:
    """
    Injecte le CSS et affiche le logo dans la sidebar.
    À appeler au début de chaque page, après set_page_config.
    """
    st.markdown(_CSS, unsafe_allow_html=True)

    logo_path = Path(__file__).resolve().parent.parent / "assets" / "logo.png"
    if logo_path.exists():
        st.logo(str(logo_path), size="large")
