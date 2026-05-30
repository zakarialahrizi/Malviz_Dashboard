"""
app.py — Point d'entrée avec navigation explicite (supprime "app" de la sidebar).
Lance : streamlit run app.py
"""
import sys
from pathlib import Path

MALVIZ_DIR = Path(__file__).resolve().parent
for p in [str(MALVIZ_DIR), str(MALVIZ_DIR.parent)]:
    if p not in sys.path:
        sys.path.insert(0, p)

import streamlit as st

# Navigation explicite — remplace la navigation automatique MPA
# Avantage : "app" n'apparaît plus dans la sidebar
pages = st.navigation([
    st.Page("pages/1_Home.py",     title="Home",       icon=":material/home:"),
    st.Page("pages/2_History.py",  title="History",    icon=":material/history:"),
    st.Page("pages/3_Settings.py", title="Settings",   icon=":material/settings:"),
    st.Page("pages/4_About.py",    title="About",      icon=":material/info:"),
])

# Logo dans la sidebar (st.logo = coin supérieur gauche de la sidebar)
logo = MALVIZ_DIR / "assets" / "logo.png"
if logo.exists():
    st.logo(str(logo), size="large")

pages.run()
