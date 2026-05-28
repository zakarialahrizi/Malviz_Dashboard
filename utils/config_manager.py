"""
utils/config_manager.py — Lecture et écriture de config/config.json.
"""

import json
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "config.json"

DEFAULT_CONFIG = {
    "confidence_threshold": 0.90,
    "logs_folder": "data/",
    "colors": {
        "primary":   "#005DA1",
        "secondary": "#3B8B85",
        "malware":   "#C0392B",
        "benign":    "#27AE60",
        "uncertain": "#E67E22",
        "chart_bg":  "#0E1117",
    },
}


def load_config() -> dict:
    """Charge la config. Crée le fichier avec les défauts si absent."""
    if not CONFIG_PATH.exists():
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
    # S'assurer que la clé colors existe (migration depuis ancienne config)
    if "colors" not in config:
        config["colors"] = DEFAULT_CONFIG["colors"]
        save_config(config)
    return config


def save_config(config: dict) -> None:
    """Sauvegarde le dict config dans config.json."""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


def get_colors() -> dict:
    """Raccourci pour récupérer uniquement la palette de couleurs."""
    return load_config().get("colors", DEFAULT_CONFIG["colors"])
