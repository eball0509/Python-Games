"""Tiny JSON-backed settings persistence (R11).

Kept deliberately minimal: one file, one dict, load/save. Not a general
config system -- just enough to remember the player's volume choice
between sessions.
"""

import json
import os

DEFAULT_SETTINGS = {"master_volume": 1.0}
SETTINGS_PATH = "settings.json"


def load_settings(path=SETTINGS_PATH):
    if not os.path.exists(path):
        return dict(DEFAULT_SETTINGS)
    try:
        with open(path, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return dict(DEFAULT_SETTINGS)
    merged = dict(DEFAULT_SETTINGS)
    merged.update(data)
    return merged


def save_settings(data, path=SETTINGS_PATH):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)