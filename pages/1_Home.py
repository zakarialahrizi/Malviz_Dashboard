"""
pages/1_Home.py — Page principale : upload, scan, résultats, métriques.
"""

import sys
import time
from pathlib import Path

import streamlit as st

# ── Chemins ───────────────────────────────────────────────────────────────────
MALVIZ_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR   = MALVIZ_DIR.parent
for p in [str(MALVIZ_DIR), str(ROOT_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from utils.config_manager import load_config, get_colors
from utils.csv_manager import append_scan, load_history, get_stats
from utils.charts import pie_chart_results, gauge_confidence

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="malviz", layout="wide")

colors = get_colors()

# ── Minimal CSS — uniquement pour les métriques et la bannière de résultat ────
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

# ── En-tête ───────────────────────────────────────────────────────────────────
logo_path = MALVIZ_DIR / "assets" / "logo.png"
if logo_path.exists():
    st.image(str(logo_path), width=72)

st.markdown(f"<h1 style='color:{colors['primary']};margin-bottom:0'>malviz</h1>", unsafe_allow_html=True)
st.caption("Détection de malware par visualisation de fichiers binaires — ResNet-18 / ONNX")
st.divider()

# ── Métriques globales ────────────────────────────────────────────────────────
df_history = load_history()
stats      = get_stats(df_history)

c1, c2, c3 = st.columns(3)
c1.metric("Total scans",      stats["total"])
c2.metric("Malware détectés", stats["malware"])
c3.metric("Taux d'infection", f"{stats['infection_rate']} %")

st.divider()

# ── Upload ────────────────────────────────────────────────────────────────────
st.subheader("Scanner un fichier")

config    = load_config()
threshold = config.get("confidence_threshold", 0.90)

uploaded_file = st.file_uploader(
    "Déposer un fichier binaire (PE, EXE, DLL…)",
    type=None,
    help="Converti en image niveaux de gris puis classifié par le modèle.",
)

scan_button = st.button("Lancer le scan", type="primary", disabled=(uploaded_file is None))

if scan_button and uploaded_file is not None:
    tmp_path = MALVIZ_DIR / "data" / uploaded_file.name
    tmp_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path.write_bytes(uploaded_file.read())

    with st.spinner("Analyse en cours..."):
        try:
            from scanner import scan_file

            start   = time.time()
            result  = scan_file(str(tmp_path), threshold=threshold)
            elapsed = time.time() - start

            append_scan(
                filename=uploaded_file.name,
                prediction=result["prediction"],
                confidence=result["confidence"],
                scan_time=elapsed,
            )

            st.subheader("Résultat")

            # Bannière de résultat
            if result["result"] == "benign":
                st.success(f"BENIGN — {result['prediction']} — aucune menace détectée.")
            elif result["result"] == "malware":
                st.error(f"MALWARE — {result['prediction']}")
            else:
                st.warning(f"INCERTAIN — {result['prediction']} — confiance insuffisante ({result['confidence']*100:.1f} %)")

            # Métriques + jauge côte à côte
            col_metrics, col_gauge = st.columns([2, 1])

            with col_metrics:
                m1, m2 = st.columns(2)
                m1.metric("Classe détectée", result["prediction"])
                m2.metric("Confiance",       f"{result['confidence'] * 100:.1f} %")
                m3, m4 = st.columns(2)
                m3.metric("Résultat",        result["result"].upper())
                m4.metric("Temps d'analyse", f"{elapsed:.2f} s")

            with col_gauge:
                fig_gauge = gauge_confidence(result["confidence"], result["prediction"], colors)
                st.plotly_chart(fig_gauge, width="stretch")

        except Exception as e:
            st.error(f"Erreur lors du scan : {e}")
            st.code(f"sys.path[:3] = {sys.path[:3]}", language="python")
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

st.divider()

# ── Graphique historique ──────────────────────────────────────────────────────
st.subheader("Aperçu de l'historique")
df_history = load_history()

if df_history.empty:
    st.info("Aucun scan enregistré. Lancez votre premier scan ci-dessus.")
else:
    fig = pie_chart_results(df_history, colors)
    st.plotly_chart(fig, width="stretch")
