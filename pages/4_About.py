"""
pages/4_About.py — Présentation du projet malviz.
"""

import sys
from pathlib import Path

import streamlit as st

MALVIZ_DIR = Path(__file__).resolve().parent.parent
for p in [str(MALVIZ_DIR), str(MALVIZ_DIR.parent)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from utils.ui_helpers import inject_css, page_title, PRIMARY, SECONDARY

st.set_page_config(page_title="malviz — À propos", layout="wide")
inject_css()

# ── En-tête ────────────────────────────────────────────────────────────────────
logo = MALVIZ_DIR / "assets" / "logo.png"


_, c, _ = st.columns([1, 2, 1])
with c:
    #if logo.exists():
        #st.image(str(logo), width=100)
    st.markdown(
        f"""
        <div style="text-align:center">
          <h1 style="color:{PRIMARY};font-size:2.2rem;margin-bottom:4px">malviz</h1>
          <p style="color:{SECONDARY};font-size:1rem">
            Scanner de malware basé sur la visualisation de binaires Windows
          </p>
          <div style="margin-top:10px">
            <img src="https://img.shields.io/badge/version-1.2.1-blue" style="margin:3px">
            <img src="https://img.shields.io/badge/python-3.10%2B-blue" style="margin:3px">
            <img src="https://img.shields.io/pypi/v/malviz" style="margin:3px">
            <img src="https://img.shields.io/badge/license-MIT-green" style="margin:3px">
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")
st.divider()

# ── Vue d'ensemble ─────────────────────────────────────────────────────────────
st.subheader("Vue d'ensemble")
st.markdown("""
**malviz** est un outil de classification de malware développé comme Projet Personnel Professionnel (PPP).

Il implémente la technique **binaire → image** : les fichiers binaires bruts sont interprétés comme
des matrices de pixels en niveaux de gris, puis soumis à un réseau de neurones convolutif pour classification.

L'outil est conçu pour permettre à des analystes de sécurité de **trier des fichiers PE Windows suspects
sans les exécuter** — analyse statique uniquement.
""")

st.divider()

# ── Pipeline ───────────────────────────────────────────────────────────────────
st.subheader("Comment ça fonctionne")
st.markdown(f"""
<div style="background:rgba(0,93,161,0.10);border:1px solid rgba(0,93,161,0.25);border-radius:10px;padding:20px 24px;margin-bottom:12px">
  <h4 style="color:{PRIMARY};margin:0 0 8px 0">1 — Binaire → Image</h4>
  <p style="color:#C9D1D9;margin:0;font-size:0.9rem">
    Les octets du fichier sont lus et reorganisés en matrice 2D.
    La largeur est calculée dynamiquement : prochaine puissance de 2
    au-dessus de la racine carrée de la taille du fichier.
    Les motifs (sections packées, charges chiffrées, structures répétitives)
    deviennent visuellement distincts.
  </p>
</div>

<div style="background:rgba(59,139,133,0.10);border:1px solid rgba(59,139,133,0.25);border-radius:10px;padding:20px 24px;margin-bottom:12px">
  <h4 style="color:{SECONDARY};margin:0 0 8px 0">2 — Prétraitement</h4>
  <p style="color:#C9D1D9;margin:0;font-size:0.9rem">
    Conversion RGB · Redimensionnement 224×224 · Normalisation ImageNet
    (mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])
  </p>
</div>

<div style="background:rgba(0,93,161,0.10);border:1px solid rgba(0,93,161,0.25);border-radius:10px;padding:20px 24px;margin-bottom:12px">
  <h4 style="color:{PRIMARY};margin:0 0 8px 0">3 — ResNet-18 (ONNX)</h4>
  <p style="color:#C9D1D9;margin:0;font-size:0.9rem">
    Architecture ResNet-18 pré-entraînée sur ImageNet, fine-tunée sur le
    dataset <strong>malimg</strong> augmenté d'une classe Benign.<br><br>
    Entrée : tenseur <code>(1, 3, 224, 224)</code> float32<br>
    Sortie : <code>(1, 26)</code> logits sur 26 classes<br>
    Runtime : CPU uniquement via <code>onnxruntime</code>
  </p>
</div>

<div style="background:rgba(59,139,133,0.10);border:1px solid rgba(59,139,133,0.25);border-radius:10px;padding:20px 24px;margin-bottom:12px">
  <h4 style="color:{SECONDARY};margin:0 0 8px 0">4 — Softmax + Seuil</h4>
  <p style="color:#C9D1D9;margin:0;font-size:0.9rem">
    Les logits sont convertis en probabilités par softmax.
    Si la confiance est sous le seuil configuré → <strong>UNCERTAIN</strong>.
    Sinon → <strong>Benign</strong> ou <strong>Malware (famille)</strong>.
  </p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ── Familles supportées ────────────────────────────────────────────────────────
st.subheader("25 familles de malware supportées")
st.caption("Entraîné sur le dataset malimg + classe Benign ajoutée manuellement.")

families = [
    ("Adialer.C",      "Agent.FYI",      "Allaple.A",     "Allaple.L",     "Alueron.gen!J"),
    ("Autorun.K",      "C2LOP.P",        "C2LOP.gen!g",   "Dialplatform.B","Dontovo.A"),
    ("Fakerean",       "Instantaccess",  "Lolyda.AA1",    "Lolyda.AA2",    "Lolyda.AA3"),
    ("Lolyda.AT",      "Malex.gen!J",    "Obfuscator.AD", "Rbot!gen",      "Skintrim.N"),
    ("Swizzor.gen!E",  "Swizzor.gen!I",  "VB.AT",         "Wintrim.BX",    "Yuner.A"),
]

cols = st.columns(5)
for col_i, col in enumerate(cols):
    with col:
        for row in families:
            st.markdown(
                f"<div style='padding:5px 0;color:#C9D1D9;font-size:0.88rem'>"
                f"· {row[col_i]}</div>",
                unsafe_allow_html=True,
            )

st.divider()

# ── Limites ────────────────────────────────────────────────────────────────────
st.subheader("Portée et limitations")

lims = [
    ("Fichiers PE Windows uniquement",
     "Conçu pour .exe, .dll, .sys, .scr, .drv. Les résultats sur ELF Linux, APK Android ou autres formats sont peu fiables."),
    ("Prototype de recherche",
     "Outil étudiant — pas un antivirus de production. Toujours vérifier avec un logiciel professionnel."),
    ("Analyse statique uniquement",
     "Le fichier n'est jamais exécuté. Pas de sandbox, pas d'analyse comportementale dynamique."),
    ("25 familles de malware",
     "Les familles absentes du dataset d'entraînement ne seront pas correctement identifiées."),
    ("CPU uniquement",
     "Pas d'accélération GPU à l'inférence — onnxruntime en mode CPUExecutionProvider."),
]

for title, desc in lims:
    st.markdown(
        f"""
<div style="
    border-left: 3px solid {PRIMARY};
    padding: 10px 16px;
    margin-bottom: 10px;
    background: rgba(0,93,161,0.06);
    border-radius: 0 8px 8px 0;
">
  <strong style="color:{PRIMARY}">{title}</strong>
  <p style="color:#8B949E;margin:4px 0 0;font-size:0.88rem">{desc}</p>
</div>
""",
        unsafe_allow_html=True,
    )

st.divider()

# ── Liens ──────────────────────────────────────────────────────────────────────
st.subheader("Liens")
st.markdown("""
CLI tool: [PyPI — malviz](https://pypi.org/project/malviz/)
""")
