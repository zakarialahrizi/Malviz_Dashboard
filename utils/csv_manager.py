"""
utils/csv_manager.py — Lecture et écriture de l'historique des scans.
"""

import csv
from datetime import datetime
from pathlib import Path

import pandas as pd

CSV_PATH = Path("data/scan_history.csv")

# Colonnes du fichier CSV
COLUMNS = ["timestamp", "filename", "prediction", "confidence", "scan_time"]


def ensure_csv_exists() -> None:
    """Crée le CSV avec les en-têtes si le fichier n'existe pas."""
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not CSV_PATH.exists():
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=COLUMNS)
            writer.writeheader()


def append_scan(filename: str, prediction: str, confidence: float, scan_time: float) -> None:
    """Ajoute une ligne au CSV pour chaque scan effectué."""
    ensure_csv_exists()
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writerow({
            "timestamp":  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "filename":   filename,
            "prediction": prediction,
            "confidence": round(confidence, 4),
            "scan_time":  round(scan_time, 3),
        })


def load_history() -> pd.DataFrame:
    """Charge l'historique complet depuis le CSV sous forme de DataFrame."""
    ensure_csv_exists()
    df = pd.read_csv(CSV_PATH)
    if df.empty:
        # Retourne un DataFrame vide avec les bonnes colonnes
        return pd.DataFrame(columns=COLUMNS)
    return df


def get_stats(df: pd.DataFrame) -> dict:
    """Calcule les métriques globales depuis le DataFrame historique."""
    total = len(df)
    if total == 0:
        return {"total": 0, "malware": 0, "benign": 0, "infection_rate": 0.0}

    malware_count = len(df[df["prediction"] != "Benign"])
    benign_count  = total - malware_count
    infection_rate = malware_count / total * 100

    return {
        "total":          total,
        "malware":        malware_count,
        "benign":         benign_count,
        "infection_rate": round(infection_rate, 1),
    }
