# build_release.py · builds the Windows release of The Last Arpeggio
#
# Run it from the project folder, with the venv active:
#     python scripts/build_release.py
#
# 1. PyInstaller builds the app into dist/TheLastArpeggio/ · TheLastArpeggio.exe plus an _internal folder
# 2. The example songs go into a songs folder next to the .exe, so they're in the Library on first launch
# 3. The licence and the README go in too
# 4. Everything is zipped into release/TheLastArpeggio-<version>-windows.zip, ready to attach to a GitHub release

import re
import shutil
import sys
from pathlib import Path

import PyInstaller.__main__

ROOT = Path(__file__).resolve().parent.parent
NAME = "TheLastArpeggio"
DIST = ROOT / "dist"
WORK = ROOT / "build" / "pyinstaller"       # PyInstaller's working files and its .spec stay in here
APP = DIST / NAME


def version():
    """The version shown in the app's sidebar, read from app.py so there's only one place to change it."""
    text = (ROOT / "arpeggio" / "ui" / "app.py").read_text(encoding="utf-8")
    return re.search(r'VERSION\s*=\s*"([^"]+)"', text).group(1)


def build():
    data = ROOT / "arpeggio" / "data"
    PyInstaller.__main__.run([
        str(ROOT / "main.py"),
        "--name", NAME,
        "--windowed",                                          # no console window · errors go to arpeggio.log
        "--noconfirm", "--clean",
        "--icon", str(data / "icon.ico"),
        "--add-data", f"{data}{';' if sys.platform == 'win32' else ':'}arpeggio/data",   # fonts, chords, icon
        "--collect-data", "customtkinter",                     # CustomTkinter's theme files
        "--hidden-import", "pynput.keyboard._win32",           # pynput picks its Windows backend at run time
        "--hidden-import", "pynput.mouse._win32",
        "--hidden-import", "PIL._tkinter_finder",              # Pillow needs this to hand the icons to Tk
        "--distpath", str(DIST),
        "--workpath", str(WORK),
        "--specpath", str(WORK),
    ])


def extras():
    songs = APP / "songs"
    songs.mkdir(exist_ok=True)
    for song in sorted((ROOT / "examples").glob("*.json")):
        if song.name != "test-song.json":                       # the test song is only for the check scripts
            shutil.copy2(song, songs / song.name)
            print(f"Example song · {song.name}")
    for name in ("LICENSE", "README.md"):
        shutil.copy2(ROOT / name, APP / name)


def zip_it(v):
    out = ROOT / "release"
    out.mkdir(exist_ok=True)
    base = out / f"{NAME}-{v}-windows"
    path = shutil.make_archive(str(base), "zip", root_dir=DIST, base_dir=NAME)
    size = Path(path).stat().st_size / 1e6
    print(f"\nRelease zip · {path} · {size:.0f} MB")


if __name__ == "__main__":
    if sys.platform != "win32":
        print("Heads up: this builds for the system it runs on · run it on Windows for the real release\n")
    v = version()
    build()
    extras()
    zip_it(v)
