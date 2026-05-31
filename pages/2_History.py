"""
pages/2_History.py — Historique complet + graphiques détaillés.
"""

import sys
from pathlib import Path

import streamlit as st

MALVIZ_DIR = Path(__file__).resolve().parent.parent
for p in [str(MALVIZ_DIR), str(MALVIZ_DIR.parent)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from utils.csv_manager import load_history, get_stats
from utils.charts      import (
    donut_results, bars_daily, hist_confidence,
    bar_families, line_confidence_time,
)
from utils.ui_helpers  import inject_css, page_title

st.set_page_config(page_title="malviz — Historique", layout="wide")
inject_css()
page_title("Historique des scans")
st.caption("Tous les fichiers analysés — tableau, filtres, graphiques.")
st.divider()

df = load_history()

if df.empty:
    st.info("Aucun scan enregistré. Analysez un fichier sur la page Home.")
    st.stop()

# ── Métriques ──────────────────────────────────────────────────────────────────
stats = get_stats(df)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total scans",      stats["total"])
c2.metric("Malware",          stats["malware"])
c3.metric("Benign",           stats["benign"])
c4.metric("Taux d'infection", f"{stats['infection_rate']} %")

st.divider()

# ── Tableau filtrable ──────────────────────────────────────────────────────────
st.subheader("Tableau")

fcol, _ = st.columns([1, 3])
with fcol:
    filtre = st.selectbox("Filtrer", ["Tous", "Malware", "Benign"])

if filtre == "Malware":
    df_view = df[df["prediction"] != "Benign"]
elif filtre == "Benign":
    df_view = df[df["prediction"] == "Benign"]
else:
    df_view = df

st.caption(f"{len(df_view)} entrée(s)")
st.dataframe(df_view, width="stretch", hide_index=True)

st.download_button(
    "Télécharger le CSV",
    data=df_view.to_csv(index=False).encode("utf-8"),
    file_name="scan_history_export.csv",
    mime="text/csv",
)
if st.button("Effacer l'historique", type="secondary"):
    from utils.csv_manager import CSV_PATH, ensure_csv_exists
    CSV_PATH.unlink(missing_ok=True)
    ensure_csv_exists()
    st.success("Historique effacé.")
    st.rerun()
st.divider()

# ── Graphiques — ligne 1 ───────────────────────────────────────────────────────
st.subheader("Graphiques")

col_a, col_b = st.columns(2)
with col_a:
    st.plotly_chart(donut_results(df), width="stretch")
with col_b:
    st.plotly_chart(bars_daily(df), width="stretch")

# ── Graphiques — ligne 2 ───────────────────────────────────────────────────────
col_c, col_d = st.columns(2)
with col_c:
    st.plotly_chart(hist_confidence(df), width="stretch")
with col_d:
    st.plotly_chart(line_confidence_time(df), width="stretch")

# ── Graphique — familles de malware (pleine largeur) ──────────────────────────
st.plotly_chart(bar_families(df), width="stretch")
