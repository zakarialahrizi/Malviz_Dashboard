"""
pages/1_Home.py — Accueil : logo centré, scan multi-fichiers, aperçu.
"""

import sys, time
from pathlib import Path

import pandas as pd
import streamlit as st

MALVIZ_DIR = Path(__file__).resolve().parent.parent
for p in [str(MALVIZ_DIR), str(MALVIZ_DIR.parent)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from utils.config_manager import load_config
from utils.csv_manager    import append_scan, load_history, get_stats
from utils.charts         import donut_results, gauge_confidence
from utils.ui_helpers     import inject_css, page_title, PRIMARY, SECONDARY, MALWARE, BENIGN, UNCERTAIN

st.set_page_config(page_title="malviz", layout="wide")
inject_css()

logo_path = MALVIZ_DIR / "assets" / "logo.png"

_, hero, _ = st.columns([1, 2, 1])
with hero:
    st.markdown(
        f"""
        <div style="text-align:center;margin-top:10px">
          <h1 style="color:{PRIMARY};font-size:2.6rem;margin-bottom:4px;letter-spacing:.04em">
            malviz
          </h1>
          <p style="color:{SECONDARY};font-size:1.05rem;margin-bottom:6px">
            Bienvenue dans votre scanner de malware
          </p>
          <p style="color:#8B949E;font-size:0.88rem;line-height:1.7">
            Déposez un ou plusieurs fichiers binaires Windows ci-dessous.<br>
            Le modèle ResNet-18 les analyse par visualisation de l'image des octets.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")
st.divider()

# ── Upload multi-fichiers ─────────────────────────────────────────────────────
config    = load_config()
threshold = config.get("confidence_threshold", 0.90)

st.subheader("Scanner des fichiers")

uploaded_files = st.file_uploader(
    "Fichiers binaires Windows",
    type=["exe", "dll", "sys", "scr", "drv"],
    accept_multiple_files=True,
    help="Formats acceptés : EXE, DLL, SYS, SCR, DRV — analyse statique uniquement, aucun fichier n'est exécuté.",
)

n = len(uploaded_files) if uploaded_files else 0
label = f"Scanner {n} fichier{'s' if n > 1 else ''}" if n > 0 else "Scanner"
scan_btn = st.button(label, type="primary", disabled=(n == 0))

if scan_btn and n > 0:
    st.divider()
    st.subheader(f"Résultats — {n} fichier{'s' if n > 1 else ''}")

    try:
        from scanner import scan_file
    except Exception as e:
        st.error(f"Impossible de charger le scanner : {e}")
        st.stop()

    # Tableau de résultats
    rows = []
    tmp_dir = MALVIZ_DIR / "data" / "tmp_uploads"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    progress = st.progress(0, text="Initialisation…")

    for i, f in enumerate(uploaded_files):
        progress.progress((i) / n, text=f"Analyse de {f.name}…")

        tmp = tmp_dir / f.name
        tmp.write_bytes(f.read())

        try:
            t0      = time.time()
            result  = scan_file(str(tmp), threshold=threshold)
            elapsed = time.time() - t0

            append_scan(
                filename=f.name,
                prediction=result["prediction"],
                confidence=result["confidence"],
                scan_time=elapsed,
            )

            rows.append({
                "Fichier":    f.name,
                "Verdict":    result["result"].upper(),
                "Famille":    result["prediction"],
                "Confiance":  f"{result['confidence']*100:.1f} %",
                "Durée (s)":  f"{elapsed:.2f}",
                "_result":    result["result"],   # colonne interne pour la couleur
            })

        except Exception as e:
            rows.append({
                "Fichier":   f.name,
                "Verdict":   "ERREUR",
                "Famille":   str(e),
                "Confiance": "—",
                "Durée (s)": "—",
                "_result":   "error",
            })
        finally:
            if tmp.exists():
                tmp.unlink()

    progress.progress(1.0, text="Terminé.")

    # ── Résumé rapide ────────────────────────────────────────────────────────
    nb_mal  = sum(1 for r in rows if r["_result"] == "malware")
    nb_ben  = sum(1 for r in rows if r["_result"] == "benign")
    nb_unc  = sum(1 for r in rows if r["_result"] == "uncertain")
    nb_err  = sum(1 for r in rows if r["_result"] == "error")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Malware",   nb_mal)
    c2.metric("Benign",    nb_ben)
    c3.metric("Incertain", nb_unc)
    c4.metric("Erreurs",   nb_err)

    st.write("")

    # ── Tableau des résultats ────────────────────────────────────────────────
    df_results = pd.DataFrame(rows).drop(columns=["_result"])
    st.dataframe(df_results, width="stretch", hide_index=True)

    # ── Bannières individuelles pour chaque fichier ──────────────────────────
    st.write("")
    for r in rows:
        res = r["_result"] if "_result" in r else "error"
        if res == "benign":
            st.success(f"BENIGN — {r['Fichier']} — {r['Famille']} ({r['Confiance']})")
        elif res == "malware":
            st.error(f"MALWARE — {r['Fichier']} — {r['Famille']} ({r['Confiance']})")
        elif res == "uncertain":
            st.warning(f"INCERTAIN — {r['Fichier']} — {r['Famille']} ({r['Confiance']})")
        else:
            st.error(f"ERREUR — {r['Fichier']} — {r['Famille']}")

    # Jauge uniquement si un seul fichier scanné
    if n == 1 and rows and rows[0]["_result"] in ("benign", "malware", "uncertain"):
        conf_val = float(rows[0]["Confiance"].replace(" %", "")) / 100
        st.plotly_chart(
            gauge_confidence(conf_val, rows[0]["Famille"]),
            width="stretch",
        )

st.divider()

# ── Aperçu global ─────────────────────────────────────────────────────────────
st.subheader("Aperçu global")

df      = load_history()
stats   = get_stats(df)

g1, g2, g3 = st.columns(3)
g1.metric("Total scans",      stats["total"])
g2.metric("Malware détectés", stats["malware"])
g3.metric("Taux d'infection", f"{stats['infection_rate']} %")

st.write("")

if df.empty:
    st.info("Aucun scan enregistré pour l'instant.")
else:
    st.plotly_chart(donut_results(df), width="stretch")
