import json
import sys
from pathlib import Path

# settings.json lives next to the app: next to the .exe in the release, in the project folder when run from source
ROOT = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent.parent
FILE = ROOT / "settings.json"

DEFAULTS = {
    "flick_distance": 400,      # how far to move the mouse to pick a chord
    "settle": 0.05,             # wait after moving, so the game registers it (seconds)
    "tap": 0.03,                # how long a key is held down (seconds)
    "countdown": 5,             # seconds before a song starts
    "stop_key": "f8",
    "window_title": "The Last of Us™ Part II",
    "theme": "system",
}

def load():
    settings = dict(DEFAULTS)
    if FILE.exists():
        try:
            settings.update(json.loads(FILE.read_text(encoding="utf-8")))
        except ValueError:
            pass                    # a damaged settings file falls back to the defaults instead of stopping the app
    return settings

def save(settings):
    FILE.write_text(json.dumps(settings, indent=2), encoding="utf-8")

def key_label(combo):
    """ctrl+shift+f8 -> Ctrl + Shift + F8"""
    return " + ".join(k.upper() if len(k) <= 3 else k.replace("_", " ").title() for k in combo.split("+"))
