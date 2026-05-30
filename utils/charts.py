"""
utils/charts.py — Graphiques Plotly pour malviz_dashboard.
Palette fixe : #005DA1 (bleu) / #3B8B85 (teal).
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── Palette fixe ───────────────────────────────────────────────────────────────
PRIMARY   = "#005DA1"
SECONDARY = "#3B8B85"
MALWARE   = "#C0392B"
BENIGN    = "#27AE60"
UNCERTAIN = "#E67E22"
GRID      = "rgba(255,255,255,0.07)"
PAPER     = "rgba(0,0,0,0)"


def _base(fig: go.Figure, title: str) -> go.Figure:
    """Style commun appliqué à tous les graphiques."""
    fig.update_layout(
        title=dict(text=title, font=dict(size=15, color=PRIMARY)),
        paper_bgcolor=PAPER,
        plot_bgcolor=PAPER,
        font=dict(color="#C9D1D9", size=12),
        margin=dict(t=50, b=30, l=10, r=10),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#C9D1D9")),
    )
    fig.update_xaxes(gridcolor=GRID, zerolinecolor=GRID)
    fig.update_yaxes(gridcolor=GRID, zerolinecolor=GRID)
    return fig


def _empty(title: str) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(
        text="Aucune donnée disponible",
        showarrow=False, font=dict(size=13, color="#666"),
        xref="paper", yref="paper", x=0.5, y=0.5,
    )
    return _base(fig, title)


# ── 1. Donut Benign / Malware ──────────────────────────────────────────────────
def donut_results(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty("Répartition globale")

    df = df.copy()
    df["cat"] = df["prediction"].apply(lambda x: "Benign" if x == "Benign" else "Malware")
    counts = df["cat"].value_counts().reset_index()
    counts.columns = ["Catégorie", "N"]

    fig = go.Figure(go.Pie(
        labels=counts["Catégorie"],
        values=counts["N"],
        hole=0.58,
        marker=dict(
            colors=[BENIGN if c == "Benign" else MALWARE for c in counts["Catégorie"]],
            line=dict(color="#0D1117", width=3),
        ),
        textfont=dict(size=13),
        hovertemplate="%{label}: %{value} (%{percent})<extra></extra>",
    ))
    total = int(counts["N"].sum())
    fig.add_annotation(
        text=f"<b>{total}</b><br><span style='font-size:11px;color:#888'>scans</span>",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=20, color="#E6EDF3"),
        xref="paper", yref="paper",
    )
    return _base(fig, "Répartition globale")


# ── 2. Barres empilées par jour ────────────────────────────────────────────────
def bars_daily(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty("Scans par jour")

    df = df.copy()
    df["date"] = pd.to_datetime(df["timestamp"]).dt.date
    df["cat"]  = df["prediction"].apply(lambda x: "Benign" if x == "Benign" else "Malware")
    grouped    = df.groupby(["date", "cat"]).size().reset_index(name="n")

    fig = px.bar(
        grouped, x="date", y="n", color="cat", barmode="stack",
        color_discrete_map={"Benign": BENIGN, "Malware": MALWARE},
        labels={"date": "Date", "n": "Scans", "cat": ""},
    )
    fig.update_traces(marker_line_width=0)
    return _base(fig, "Scans par jour")


# ── 3. Histogramme des scores de confiance ─────────────────────────────────────
def hist_confidence(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty("Scores de confiance")

    df = df.copy()
    df["cat"] = df["prediction"].apply(lambda x: "Benign" if x == "Benign" else "Malware")

    fig = px.histogram(
        df, x="confidence", color="cat", nbins=25,
        barmode="overlay", opacity=0.78,
        color_discrete_map={"Benign": BENIGN, "Malware": MALWARE},
        labels={"confidence": "Score de confiance", "count": "Nombre", "cat": ""},
    )
    fig.update_traces(marker_line_width=0)
    fig.add_vline(
        x=0.90, line_dash="dot", line_color=UNCERTAIN,
        annotation_text="seuil par défaut",
        annotation_font_color=UNCERTAIN,
        annotation_position="top right",
    )
    return _base(fig, "Distribution des scores de confiance")


# ── 4. Top familles de malware ────────────────────────────────────────────────
def bar_families(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty("Familles de malware")

    mal = df[df["prediction"] != "Benign"].copy()
    if mal.empty:
        return _empty("Familles de malware — aucun malware détecté")

    counts = mal["prediction"].value_counts().reset_index()
    counts.columns = ["Famille", "N"]
    counts = counts.head(15).sort_values("N")

    # Gradient de couleur du bleu au teal
    n = len(counts)
    palette = [
        f"rgba({int(0 + (59-0)*i/(max(n-1,1)))}, "
        f"{int(93 + (139-93)*i/(max(n-1,1)))}, "
        f"{int(161 + (133-161)*i/(max(n-1,1)))}, 0.9)"
        for i in range(n)
    ]

    fig = go.Figure(go.Bar(
        x=counts["N"],
        y=counts["Famille"],
        orientation="h",
        marker=dict(color=palette, line=dict(width=0)),
        hovertemplate="%{y}: %{x} détection(s)<extra></extra>",
    ))
    fig.update_layout(height=max(300, n * 32))
    return _base(fig, "Top familles de malware détectées")


# ── 5. Ligne temporelle de confiance ──────────────────────────────────────────
def line_confidence_time(df: pd.DataFrame) -> go.Figure:
    if df.empty or len(df) < 2:
        return _empty("Évolution de la confiance")

    df = df.copy()
    df["ts"]  = pd.to_datetime(df["timestamp"])
    df["cat"] = df["prediction"].apply(lambda x: "Benign" if x == "Benign" else "Malware")
    df = df.sort_values("ts")

    fig = go.Figure()
    for cat, color in [("Benign", BENIGN), ("Malware", MALWARE)]:
        sub = df[df["cat"] == cat]
        if sub.empty:
            continue
        fig.add_trace(go.Scatter(
            x=sub["ts"], y=sub["confidence"],
            mode="markers+lines",
            name=cat,
            line=dict(color=color, width=1.5),
            marker=dict(size=6, color=color),
            hovertemplate="%{y:.2%} — %{x}<extra>" + cat + "</extra>",
        ))
    fig.add_hline(
        y=0.90, line_dash="dot", line_color=UNCERTAIN,
        annotation_text="seuil", annotation_font_color=UNCERTAIN,
    )
    return _base(fig, "Évolution de la confiance dans le temps")


# ── 6. Jauge pour un scan individuel ─────────────────────────────────────────
def gauge_confidence(confidence: float, label: str) -> go.Figure:
    color = BENIGN if label == "Benign" else MALWARE

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=round(confidence * 100, 1),
        number=dict(suffix="%", font=dict(size=30, color="#E6EDF3")),
        gauge=dict(
            axis=dict(range=[0, 100], tickcolor="#444"),
            bar=dict(color=color, thickness=0.65),
            bgcolor=PAPER,
            borderwidth=0,
            steps=[
                dict(range=[0, 50],  color="rgba(255,255,255,0.03)"),
                dict(range=[50, 90], color="rgba(255,255,255,0.05)"),
                dict(range=[90, 100],color="rgba(255,255,255,0.08)"),
            ],
            threshold=dict(
                line=dict(color=UNCERTAIN, width=2),
                thickness=0.8, value=90,
            ),
        ),
        title=dict(text="Score de confiance", font=dict(size=12, color="#888")),
    ))
    fig.update_layout(
        paper_bgcolor=PAPER,
        font=dict(color="#C9D1D9"),
        margin=dict(t=40, b=10, l=20, r=20),
        height=230,
    )
    return fig
