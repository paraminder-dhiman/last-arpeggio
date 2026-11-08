import json
from pathlib import Path

FILE = Path(__file__).parent.parent / "settings.json"

DEFAULTS = {
    "flick_distance": 400,      # how far to move the mouse to pick a chord
    "settle": 0.05,             # wait after moving, so the game registers it (seconds)
    "tap": 0.03,                # how long a key is held down (seconds)
    "countdown": 5,             # seconds before a song starts
    "stop_key": "f8",
    "window_title": "The Last of Us™ Part II",
}

def load():
    settings = dict(DEFAULTS)
    if FILE.exists():
        settings.update(json.loads(FILE.read_text()))
    return settings

def save(settings):
    FILE.write_text(json.dumps(settings, indent=2))