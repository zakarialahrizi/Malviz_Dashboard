"""
pages/3_Settings.py — Paramètres : seuil de confiance + palette de couleurs.
"""

import sys
from pathlib import Path

import streamlit as st

MALVIZ_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR   = MALVIZ_DIR.parent
for p in [str(MALVIZ_DIR), str(ROOT_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from utils.config_manager import load_config, save_config, DEFAULT_CONFIG

st.set_page_config(page_title="malviz - Settings", layout="wide")

config = load_config()
colors = config.get("colors", DEFAULT_CONFIG["colors"])

st.markdown(f"<h1 style='color:{colors['primary']}'>Paramètres</h1>", unsafe_allow_html=True)
st.caption("Configuration du scanner et de l'interface.")
st.divider()

# ── Scanner ───────────────────────────────────────────────────────────────────
st.subheader("Scanner")

new_threshold = st.slider(
    "Seuil de confiance",
    min_value=0.50, max_value=1.00,
    value=float(config.get("confidence_threshold", 0.90)),
    step=0.01,
    help="En dessous de ce seuil, le résultat est marqué 'uncertain'.",
)
st.caption(f"Valeur actuelle : **{new_threshold:.2f}**")

new_logs_folder = st.text_input(
    "Dossier des logs",
    value=config.get("logs_folder", "data/"),
)

st.divider()


# ── Bouton sauvegarde ─────────────────────────────────────────────────────────
if st.button("Sauvegarder", type="primary"):
    updated = {
        "confidence_threshold": new_threshold,
        "logs_folder":          new_logs_folder,
    }
    save_config(updated)
    st.success("Paramètres sauvegardés dans config/config.json")


st.divider()
st.subheader("config.json actuel")
st.json(load_config())
