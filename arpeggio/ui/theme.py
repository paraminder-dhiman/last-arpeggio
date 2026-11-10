from pathlib import Path
import customtkinter as ctk

# (light, dark) pairs
BASE      = ("#e3e7e3", "#182229")
GROUND    = ("#eef0ec", "#212f3a")
HAIR      = ("#d3d9d8", "#3d4e59")
TEXT      = ("#1c2830", "#e2e5e1")
SOFT      = ("#34434d", "#c9d0cf")
MUTED     = ("#4a575e", "#a9b4b6")
ACCENT    = ("#145b63", "#63c5ce")
ACCENT_HI = ("#0e434a", "#9be0e6")
TINT      = ("#dde4e1", "#263b46")   # accent at 8% over ground
HOVER     = ("#e5eae7", "#243540")   # accent at 4% over ground
ON_ACCENT = GROUND
FADED     = ("#81a6a8", "#427a84")   # text on a disabled filled button
DIM       = ("#9ca3a5", "#657178")   # locked sidebar items · halfway between muted and ground

PANEL_R = 10
CONTROL_R = 7

FONT_DIR = Path(__file__).resolve().parent.parent / "data" / "fonts"
FAMILY = {400: "IBM Plex Sans", 500: "IBM Plex Sans Medium"}

def load_fonts():
    for path in FONT_DIR.glob("*.ttf"):
        ctk.FontManager.load_font(str(path))

_fonts = {}

def font(size, weight=400):
    if (size, weight) not in _fonts:
        _fonts[size, weight] = ctk.CTkFont(family=FAMILY[weight], size=size)
    return _fonts[size, weight]