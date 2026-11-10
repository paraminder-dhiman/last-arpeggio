import customtkinter as ctk

from .. import settings
from . import theme as t
from .playing import wheel_test_job
from .widgets import Segmented, button, entry, label, panel, section
from .window_picker import WindowPicker

FIELDS = [
    ("flick_distance", "Flick distance", "How far the mouse moves to pick a direction"),
    ("settle", "Settle", "Seconds to wait after aiming"),
    ("tap", "Tap", "Seconds a key is held"),
    ("countdown", "Countdown", "Seconds before playing starts"),
    ("stop_key", "Stop key", "Press it in the game to stop"),
    ("window_title", "Game window", ""),
]

MODIFIERS = {"Control_L": "ctrl", "Control_R": "ctrl", "Shift_L": "shift", "Shift_R": "shift",
             "Alt_L": "alt", "Alt_R": "alt"}
SPECIAL = {"prior": "page_up", "next": "page_down", "return": "enter", "backspace": "backspace",
           "tab": "tab", "space": "space", "insert": "insert", "delete": "delete", "home": "home",
           "end": "end", "pause": "pause", "scroll_lock": "scroll_lock",
           "up": "up", "down": "down", "left": "left", "right": "right"}
GUITAR_KEYS = {"1", "2", "3", "4", "5", "6", "q", "e", "space"}   # the app presses these itself


def key_name(keysym):
    """Tk's name for a key -> the name pynput uses, or None if we don't support it."""
    k = keysym.lower()
    if k in SPECIAL:
        return SPECIAL[k]
    if (k[0] == "f" and k[1:].isdigit()) or (len(k) == 1 and k.isalnum()):
        return k
    return None

class SettingsPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app, self.inputs, self.held = app, {}, set()
        self.columnconfigure(0, weight=1)
        label(self, "Settings", 26, 500).grid(row=0, column=0, sticky="w", pady=(18, 16))

        section(self, "Playing").grid(row=1, column=0, sticky="w", pady=(0, 6))
        box = panel(self)
        box.grid(row=2, column=0, sticky="ew")
        box.columnconfigure(1, weight=1)
        for i, (key, name, hint) in enumerate(FIELDS):
            pad = (14 if i == 0 else 6, 14 if i == len(FIELDS) - 1 else 6)
            label(box, name, 15, 500).grid(row=i, column=0, sticky="w", padx=(20, 24), pady=pad)
            hint_label = label(box, hint, 13, 400, t.MUTED)
            hint_label.grid(row=i, column=1, sticky="w", pady=pad)
            if key == "window_title":
                self.window_hint = hint_label
                button(box, "Choose", self.picker_open, "outline", 120).grid(row=i, column=2, sticky="e", padx=20, pady=pad)
                continue
            if key == "stop_key":
                self.key_btn = button(box, "", self.record, "outline", 120)
                self.key_btn.grid(row=i, column=2, sticky="e", padx=20, pady=pad)
                continue
            e = entry(box, 120)
            e.grid(row=i, column=2, sticky="e", padx=20, pady=pad)
            self.inputs[key] = e

        section(self, "Appearance").grid(row=3, column=0, sticky="w", pady=(18, 6))
        look = panel(self)
        look.grid(row=4, column=0, sticky="ew")
        look.columnconfigure(1, weight=1)
        label(look, "Theme", 15, 500).grid(row=0, column=0, sticky="w", padx=(20, 24), pady=14)
        self.theme = Segmented(look, ["System", "Light", "Dark"], self.theme_chosen, 90)
        self.theme.grid(row=0, column=2, sticky="e", padx=20, pady=14)

        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.grid(row=5, column=0, sticky="ew", pady=(18, 0))
        button(bar, "Save", self.save, "fill", 90).pack(side="left")
        button(bar, "Reset to defaults", self.reset, "outline").pack(side="left", padx=12)
        self.test_btn = button(bar, "Test the wheel", self.test, "outline")
        self.test_btn.pack(side="left")
        self.status = label(bar, "", 13, 400, t.MUTED)
        self.status.pack(side="left", padx=14)
        self.picker = WindowPicker(self, self.window_picked)
        self.load(settings.load())

    def load(self, s):
        for key, e in self.inputs.items():
            e.delete(0, "end")
            e.insert(0, str(s[key]))
        self.key_btn.configure(text=settings.key_label(s["stop_key"]))
        self.show_window(s["window_title"])
        self.theme.set(s.get("theme", "system").title())

    def read(self):
        s = settings.load()
        for key, e in self.inputs.items():
            kind = type(settings.DEFAULTS[key])
            s[key] = kind(e.get().strip())
        return s

    def save(self):
        try:
            settings.save(self.read())
        except ValueError:
            self.status.configure(text="One of the numbers isn't a number", text_color=t.ACCENT)
            return
        self.status.configure(text="Saved", text_color=t.SOFT)
        self.app.pages["Library"].reset_hint()

    def reset(self):
        s = dict(settings.DEFAULTS)
        old = settings.load()
        s["theme"] = old.get("theme", "system")
        settings.save(s)
        self.load(s)
        self.status.configure(text="Back to defaults", text_color=t.SOFT)

    def theme_chosen(self, value):
        self.app.set_theme(value.lower())

    def test(self):
        if self.app.busy:
            return
        self.test_btn.configure(state="disabled")
        self.app.run(wheel_test_job, self.on_message)

    def on_message(self, kind, value):
        if kind == "count":
            self.status.configure(text=f"Starting in {value}", text_color=t.ACCENT)
        elif kind == "playing":
            self.status.configure(text="Strumming all six directions", text_color=t.ACCENT)
        else:
            self.test_btn.configure(state="normal")
            self.status.configure(text=value, text_color=t.ACCENT if kind == "error" else t.SOFT)

    def record(self):
        self.held = set()
        self.key_btn.configure(text="Press keys…")
        self.status.configure(text="Press the key or combo · Esc cancels", text_color=t.ACCENT)
        self.app.focus_set()
        self.app.bind("<KeyPress>", self.key_down)
        self.app.bind("<KeyRelease>", self.key_up)

    def key_up(self, e):
        self.held.discard(MODIFIERS.get(e.keysym))

    def key_down(self, e):
        if e.keysym in MODIFIERS:
            self.held.add(MODIFIERS[e.keysym])
            return "break"
        if e.keysym == "Escape":
            return self.stop_recording("Kept the old stop key")
        name = key_name(e.keysym)
        if name is None:
            return self.stop_recording("That key can't be used · try an F key")
        if not self.held and name in GUITAR_KEYS:
            return self.stop_recording(f"{settings.key_label(name)} plays the guitar · pick another")
        combo = "+".join([m for m in ("ctrl", "alt", "shift") if m in self.held] + [name])
        s = settings.load()
        s["stop_key"] = combo
        settings.save(s)
        self.app.pages["Library"].reset_hint()
        return self.stop_recording(f"Stop key set to {settings.key_label(combo)}", ok=True)

    def stop_recording(self, message, ok=False):
        self.app.unbind("<KeyPress>")
        self.app.unbind("<KeyRelease>")
        self.key_btn.configure(text=settings.key_label(settings.load()["stop_key"]))
        self.status.configure(text=message, text_color=t.SOFT if ok else t.ACCENT)
        return "break"

    def show_window(self, title):
        short = title if len(title) <= 48 else title[:47] + "…"
        self.window_hint.configure(text=short or "Not picked · finds the game by its name")

    def picker_open(self):
        self.picker.open()

    def window_picked(self, title):
        s = settings.load()
        s["window_title"] = title
        settings.save(s)
        self.show_window(title)
        self.status.configure(text="Game window set", text_color=t.SOFT)
