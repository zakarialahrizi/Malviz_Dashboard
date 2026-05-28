"""
utils/charts.py — Graphiques Plotly avec couleurs configurables.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def _empty_fig(title: str) -> go.Figure:
    """Figure vide avec message centré."""
    fig = go.Figure()
    fig.add_annotation(
        text="Aucune donnée disponible",
        showarrow=False,
        font=dict(size=14, color="#888"),
        xref="paper", yref="paper", x=0.5, y=0.5,
    )
    fig.update_layout(
        title=title,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#ccc"),
    )
    return fig


def _base_layout(fig: go.Figure, title: str, colors: dict) -> go.Figure:
    """Applique le style commun à tous les graphiques."""
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color=colors["primary"])),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#ccc", size=12),
        margin=dict(t=50, b=30, l=20, r=20),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#ccc")),
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.08)", zerolinecolor="rgba(255,255,255,0.1)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.08)", zerolinecolor="rgba(255,255,255,0.1)")
    return fig


def pie_chart_results(df: pd.DataFrame, colors: dict) -> go.Figure:
    """Donut chart : répartition Benign vs Malware."""
    if df.empty:
        return _empty_fig("Répartition des résultats")

    df = df.copy()
    df["category"] = df["prediction"].apply(
        lambda x: "Benign" if x == "Benign" else "Malware"
    )
    counts = df["category"].value_counts().reset_index()
    counts.columns = ["Catégorie", "Nombre"]

    fig = go.Figure(data=[go.Pie(
        labels=counts["Catégorie"],
        values=counts["Nombre"],
        hole=0.55,
        marker=dict(
            colors=[
                colors["benign"] if c == "Benign" else colors["malware"]
                for c in counts["Catégorie"]
            ],
            line=dict(color="#111", width=2),
        ),
        textfont=dict(size=13),
        hovertemplate="%{label}: %{value} (%{percent})<extra></extra>",
    )])

    # Texte central
    total = int(counts["Nombre"].sum())
    fig.add_annotation(
        text=f"<b>{total}</b><br>scans",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=16, color="#fff"),
        xref="paper", yref="paper",
    )

    return _base_layout(fig, "Répartition des résultats", colors)


def bar_chart_daily(df: pd.DataFrame, colors: dict) -> go.Figure:
    """Barres : nombre de scans par jour, empilées Benign / Malware."""
    if df.empty:
        return _empty_fig("Scans par jour")

    df = df.copy()
    df["date"]     = pd.to_datetime(df["timestamp"]).dt.date
    df["category"] = df["prediction"].apply(
        lambda x: "Benign" if x == "Benign" else "Malware"
    )

    grouped = (
        df.groupby(["date", "category"])
        .size()
        .reset_index(name="count")
    )

    fig = px.bar(
        grouped,
        x="date", y="count", color="category",
        barmode="stack",
        color_discrete_map={
            "Benign":  colors["benign"],
            "Malware": colors["malware"],
        },
        labels={"date": "Date", "count": "Scans", "category": ""},
    )
    fig.update_traces(marker_line_width=0)
    return _base_layout(fig, "Scans par jour", colors)


def confidence_histogram(df: pd.DataFrame, colors: dict) -> go.Figure:
    """Histogramme des scores de confiance, coloré par catégorie."""
    if df.empty:
        return _empty_fig("Distribution des scores de confiance")

    df = df.copy()
    df["category"] = df["prediction"].apply(
        lambda x: "Benign" if x == "Benign" else "Malware"
    )

    fig = px.histogram(
        df,
        x="confidence",
        color="category",
        nbins=25,
        barmode="overlay",
        opacity=0.8,
        color_discrete_map={
            "Benign":  colors["benign"],
            "Malware": colors["malware"],
        },
        labels={"confidence": "Score de confiance", "count": "Nombre", "category": ""},
    )
    fig.update_traces(marker_line_width=0)
    fig.add_vline(
        x=0.90, line_dash="dash",
        line_color=colors["uncertain"],
        annotation_text="seuil", annotation_font_color=colors["uncertain"],
    )
    return _base_layout(fig, "Distribution des scores de confiance", colors)


def gauge_confidence(confidence: float, label: str, colors: dict) -> go.Figure:
    """Jauge de confiance pour le résultat d'un scan."""
    color = colors["benign"] if label == "Benign" else colors["malware"]

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=round(confidence * 100, 1),
        number=dict(suffix="%", font=dict(size=28, color="#fff")),
        gauge=dict(
            axis=dict(range=[0, 100], tickcolor="#555"),
            bar=dict(color=color, thickness=0.7),
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
            steps=[
                dict(range=[0, 50],  color="rgba(255,255,255,0.04)"),
                dict(range=[50, 90], color="rgba(255,255,255,0.07)"),
                dict(range=[90, 100],color="rgba(255,255,255,0.10)"),
            ],
            threshold=dict(
                line=dict(color=colors["uncertain"], width=2),
                thickness=0.8, value=90,
            ),
        ),
        title=dict(text="Confiance", font=dict(size=13, color="#aaa")),
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#ccc"),
        margin=dict(t=30, b=10, l=20, r=20),
        height=220,
    )
    return fig
