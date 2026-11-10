import re
import sys
from pathlib import Path
from .song import Song

ROOT = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent.parent
SONGS = ROOT / "songs"

def songs():
    SONGS.mkdir(exist_ok=True)
    found = []
    for path in SONGS.glob("*.json"):
        try:
            found.append((path, Song.load(str(path))))
        except Exception:
            pass  # not one of ours, or damaged
    return sorted(found, key=lambda pair: pair[1].title.lower())

def safe_name(title):
    name = re.sub(r'[<>:"/\\|?*]', "", title).strip().rstrip(".")
    return name or "Untitled"

def save(song):
    SONGS.mkdir(exist_ok=True)
    path, n = SONGS / f"{safe_name(song.title)}.json", 2
    while path.exists():
        path, n = SONGS / f"{safe_name(song.title)} ({n}).json", n + 1
    song.save(str(path))
    return path

def delete(path):
    Path(path).unlink(missing_ok=True)