import customtkinter as ctk

from .. import library, settings
from ..planner import plan
from . import theme as t
from .playing import at_speed, clock, seconds
from .widgets import RowList, button, label, panel, section, slider


def key_text(shift):
    return "same key" if shift % 12 == 0 else f"shift {shift:+d}".replace("-", "−")

class LibraryPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app, self.songs, self.path, self.timer = app, {}, None, None
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        head = ctk.CTkFrame(self, fg_color="transparent")
        head.grid(row=0, column=0, columnspan=2, sticky="w", pady=(18, 16))
        label(head, "Library", 26, 500).pack(side="left")
        self.count = label(head, "", 14, 400, t.MUTED)
        self.count.pack(side="left", padx=(14, 0), pady=(8, 0))

        self.list = RowList(self, self.show, width=380)
        self.list.grid(row=1, column=0, sticky="ns", padx=(0, 20))

        self.detail = panel(self)
        self.detail.grid(row=1, column=1, sticky="nsew")
        self.detail.columnconfigure(0, weight=1)
        self.detail.rowconfigure(6, weight=1)
        d = self.detail

        self.title = label(d, "", 24, 500)
        self.title.grid(row=0, column=0, columnspan=2, sticky="w", padx=24, pady=(20, 0))
        self.meta = label(d, "", 14, 400, t.MUTED)
        self.meta.grid(row=1, column=0, columnspan=2, sticky="w", padx=24, pady=(4, 0))

        section(d, "Speed").grid(row=2, column=0, sticky="w", padx=24, pady=(28, 6))
        self.speed = slider(d, self.speed_moved, from_=50, to=100, number_of_steps=10)
        self.speed.grid(row=3, column=0, sticky="ew", padx=(24, 10))
        self.pct = label(d, "100%", 14, 500)
        self.pct.grid(row=3, column=1, sticky="w", padx=(0, 24))

        section(d, "Fit").grid(row=4, column=0, sticky="w", padx=24, pady=(28, 6))
        self.fit = label(d, "", 14, 400, t.SOFT)
        self.fit.grid(row=5, column=0, columnspan=2, sticky="nw", padx=24)

        bar = ctk.CTkFrame(d, fg_color="transparent")
        bar.grid(row=7, column=0, columnspan=2, sticky="ew", padx=24)
        bar.columnconfigure(2, weight=1)
        self.play_btn = button(bar, "Play", self.play, "fill", 110)
        self.play_btn.grid(row=0, column=0)
        self.preview_btn = button(bar, "Preview", self.preview, "outline", 96)
        self.preview_btn.grid(row=0, column=1, padx=12)
        self.delete_btn = button(bar, "Delete", self.delete, "quiet", 70)
        self.delete_btn.grid(row=0, column=3)
        self.hint = label(d, "", 13, 400, t.MUTED)
        self.hint.grid(row=8, column=0, columnspan=2, sticky="w", padx=24, pady=(10, 18))

        self.empty = ctk.CTkFrame(d, fg_color=t.GROUND, corner_radius=t.PANEL_R)
        label(self.empty, "No songs yet", 20, 500).pack(anchor="w", padx=24, pady=(20, 0))
        label(self.empty, "Import a MIDI file and it lands here.", 14, 400, t.MUTED).pack(anchor="w", padx=24, pady=(4, 16))
        button(self.empty, "Import", lambda: app.show("Import"), "fill", 110).pack(anchor="w", padx=24)
        self.refresh()

    def refresh(self, select=None):
        found = library.songs()
        self.songs = {str(p): song for p, song in found}
        self.count.configure(text=f"{len(found)} song" + ("" if len(found) == 1 else "s"))
        self.list.fill([(str(p), s.title, f"{s.mode.title()} · {clock(seconds(s))} · {key_text(s.shift)}", False)
                        for p, s in found])
        if not found:
            self.path = None
            self.empty.place(x=1, y=1, relwidth=0.99, relheight=0.99)
            return
        self.empty.place_forget()
        self.list.select(str(select) if str(select) in self.songs else next(iter(self.songs)))

    def show(self, path):
        self.path = path
        song = self.songs[path]
        self.title.configure(text=song.title)
        notes = sum(e.kind != "strum" for e in song.events)
        chords = len(song.events) - notes
        bits = [song.mode.title(), clock(seconds(song))]
        bits += [f"{notes} notes"] if notes else []
        bits += [f"{chords} chords"] if chords else []
        self.meta.configure(text=" · ".join(bits + [key_text(song.shift)]))
        self.speed.set(100)
        self.speed_moved(100)
        self.reset_hint()

    def speed_moved(self, value):
        self.pct.configure(text=f"{int(value)}%")
        if self.timer:
            self.after_cancel(self.timer)
        self.timer = self.after(250, self.update_fit)

    def update_fit(self):
        self.timer = None
        if not self.path:
            return
        song = self.songs[self.path]
        p = plan(at_speed(song, self.speed.get() / 100), settings.load())
        missing = sum("isn't on the guitar" in m for _, m in p.problems)
        fast = sum("too fast" in m for _, m in p.problems)
        lines = [f"{key_text(song.shift).capitalize()} · {p.switches} wheel switches",
                 f"{fast} spots too fast" if fast else "Nothing too fast"]
        if missing:
            lines.append(f"{missing} notes not on the guitar")
        self.fit.configure(text="\n".join(lines), text_color=t.ACCENT if fast else t.SOFT)

    def reset_hint(self):
        s = settings.load()
        self.hint.configure(text=f"Switches to the game, counts down from {s['countdown']} · "
                                 f"{settings.key_label(s['stop_key'])} stops", text_color=t.MUTED)

    def play(self):
        if self.path and not self.app.busy:
            self.app.play_song(self.songs[self.path], self.speed.get() / 100)

    def preview(self):
        if self.app.previewer.busy:
            self.app.previewer.stop()
        elif self.path:
            self.preview_btn.configure(text="Stop")
            self.app.previewer.start(self.songs[self.path], self.speed.get() / 100,
                                     lambda: self.preview_btn.configure(text="Preview"))

    def delete(self):
        if self.delete_btn.cget("text") == "Delete":
            self.delete_btn.configure(text="Sure?", text_color=t.ACCENT)
            self.after(3000, lambda: self.delete_btn.configure(text="Delete", text_color=t.MUTED))
            return
        self.delete_btn.configure(text="Delete", text_color=t.MUTED)
        library.delete(self.path)
        self.refresh()