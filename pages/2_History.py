"""
pages/2_History.py — Historique complet des scans.
"""

import sys
from pathlib import Path

import streamlit as st

MALVIZ_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR   = MALVIZ_DIR.parent
for p in [str(MALVIZ_DIR), str(ROOT_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from utils.config_manager import get_colors
from utils.csv_manager import load_history, get_stats
from utils.charts import bar_chart_daily, confidence_histogram

st.set_page_config(page_title="malviz - Historique", layout="wide")

colors = get_colors()

st.markdown(f"""
<style>
[data-testid="metric-container"] {{
    background: rgba(0,93,161,0.12);
    border: 1px solid rgba(0,93,161,0.35);
    border-radius: 10px;
    padding: 14px 18px;
}}
[data-testid="metric-container"] label {{
    color: {colors['secondary']} !important;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}}
[data-testid="metric-container"] [data-testid="metric-value"] {{
    color: #fff !important;
    font-size: 1.9rem;
    font-weight: 700;
}}
</style>
""", unsafe_allow_html=True)

st.markdown(f"<h1 style='color:{colors['primary']}'>Historique des scans</h1>", unsafe_allow_html=True)
st.caption("Tous les fichiers analysés, avec filtres et export.")
st.divider()

df = load_history()

if df.empty:
    st.info("Aucun scan enregistré. Rendez-vous sur Home pour analyser un fichier.")
    st.stop()

# ── Métriques ─────────────────────────────────────────────────────────────────
stats = get_stats(df)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total scans",      stats["total"])
c2.metric("Malware",          stats["malware"])
c3.metric("Benign",           stats["benign"])
c4.metric("Taux d'infection", f"{stats['infection_rate']} %")

st.divider()

# ── Tableau filtrable ─────────────────────────────────────────────────────────
st.subheader("Tableau")

filter_col, _ = st.columns([1, 3])
with filter_col:
    selected = st.selectbox("Filtrer par résultat", ["Tous", "Malware", "Benign"])

if selected == "Malware":
    df_display = df[df["prediction"] != "Benign"]
elif selected == "Benign":
    df_display = df[df["prediction"] == "Benign"]
else:
    df_display = df

st.caption(f"{len(df_display)} entrée(s) affichée(s).")
st.dataframe(df_display, width="stretch", hide_index=True)

csv_bytes = df_display.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Télécharger le CSV",
    data=csv_bytes,
    file_name="scan_history_export.csv",
    mime="text/csv",
)

st.divider()

# ── Graphiques ────────────────────────────────────────────────────────────────
st.subheader("Graphiques")

col_left, col_right = st.columns(2)

with col_left:
    st.plotly_chart(bar_chart_daily(df, colors), width="stretch")

with col_right:
    st.plotly_chart(confidence_histogram(df, colors), width="stretch")
