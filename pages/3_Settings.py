"""
pages/3_Settings.py — Paramètres du scanner.
"""

import sys
from pathlib import Path

import streamlit as st

MALVIZ_DIR = Path(__file__).resolve().parent.parent
for p in [str(MALVIZ_DIR), str(MALVIZ_DIR.parent)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from utils.config_manager import load_config, save_config, DEFAULT_CONFIG
from utils.ui_helpers     import inject_css, page_title

st.set_page_config(page_title="malviz — Paramètres", layout="wide")
inject_css()
page_title("Paramètres")
st.caption("Configuration du scanner sauvegardée dans config/config.json.")
st.divider()

config = load_config()

# ── Scanner ────────────────────────────────────────────────────────────────────
st.subheader("Scanner")

col, _ = st.columns([2, 2])
with col:
    new_threshold = st.slider(
        "Seuil de confiance",
        min_value=0.50, max_value=1.00,
        value=float(config.get("confidence_threshold", 0.90)),
        step=0.01,
        help="En dessous de ce seuil le résultat est marqué 'uncertain'.",
    )

st.markdown("""
| Seuil | Comportement |
|-------|-------------|
| 0.90 (défaut) | Conservateur — verdicts à haute confiance uniquement |
| 0.75 | Équilibré — moins de résultats incertains |
| 0.50 | Permissif — plus de verdicts, risque de faux positifs |
""")

st.divider()

# ── Stockage ───────────────────────────────────────────────────────────────────
st.subheader("Stockage")

col2, _ = st.columns([2, 2])
with col2:
    new_logs = st.text_input(
        "Dossier des logs",
        value=config.get("logs_folder", "data/"),
    )

st.divider()

# ── Sauvegarde ─────────────────────────────────────────────────────────────────
b1, b2, _ = st.columns([1, 1, 2])
with b1:
    if st.button("Sauvegarder", type="primary"):
        save_config({"confidence_threshold": new_threshold, "logs_folder": new_logs})
        st.success("Sauvegardé.")
with b2:
    if st.button("Réinitialiser"):
        save_config(DEFAULT_CONFIG)
        st.success("Paramètres réinitialisés.")
        st.rerun()

st.divider()
st.subheader("config.json actuel")
st.json(load_config())
