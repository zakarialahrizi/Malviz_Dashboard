"""
utils/config_manager.py — Lecture et écriture de config/config.json.
"""

import json
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "config.json"

DEFAULT_CONFIG = {
    "confidence_threshold": 0.90,
    "logs_folder": "data/",
}


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(config: dict) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
