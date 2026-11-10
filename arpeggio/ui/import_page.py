from pathlib import Path
from tkinter import filedialog
import customtkinter as ctk

from .. import fit, library, midi_import, settings
from ..guitar import number_to_note
from . import theme as t
from .widgets import RowList, Segmented, button, entry, label, panel, section

class ImportPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app, self.midi, self.parts, self.song, self.report, self.dropped = app, None, {}, None, None, 0
        self.columnconfigure(1, weight=1)
        self.rowconfigure(3, weight=1)

        head = ctk.CTkFrame(self, fg_color="transparent")
        head.grid(row=0, column=0, columnspan=2, sticky="w", pady=(18, 16))
        label(head, "Import", 26, 500).pack(side="left")
        label(head, "a MIDI file", 14, 400, t.MUTED).pack(side="left", padx=(14, 0), pady=(8, 0))

        top = panel(self)
        top.grid(row=1, column=0, columnspan=2, sticky="ew")
        top.columnconfigure(1, weight=1)
        self.file = label(top, "No file yet", 15, 500)
        self.file.grid(row=0, column=0, padx=(20, 14), pady=12)
        self.info = label(top, "", 14, 400, t.MUTED)
        self.info.grid(row=0, column=1, sticky="w")
        button(top, "Choose file", self.choose, "outline", 118).grid(row=0, column=2, padx=14)

        section(self, "Part").grid(row=2, column=0, sticky="w", pady=(18, 6))
        self.list = RowList(self, self.part_chosen, width=340)
        self.list.grid(row=3, column=0, sticky="ns", padx=(0, 20))

        r = ctk.CTkFrame(self, fg_color="transparent")
        r.grid(row=2, column=1, rowspan=2, sticky="nsew", pady=(18, 0))
        r.columnconfigure(0, weight=1)
        r.rowconfigure(8, weight=1)
        section(r, "Mode").grid(row=0, column=0, sticky="w", pady=(0, 6))
        self.mode = Segmented(r, ["Melody", "Chords", "Both"], lambda v: self.build())
        self.mode.set("Melody")
        self.mode.grid(row=1, column=0, sticky="w")

        section(r, "Fit").grid(row=2, column=0, sticky="w", pady=(18, 6))
        box = panel(r)
        box.grid(row=3, column=0, sticky="ew")
        self.fit = label(box, "Choose a file to see how it fits the guitar.", 14, 400, t.SOFT)
        self.fit.pack(anchor="w", padx=18, pady=14)
        self.warn = label(box, "", 14, 500, t.ACCENT)

        self.choices = ctk.CTkFrame(r, fg_color="transparent")
        button(self.choices, "Thin out · recommended", lambda: self.speed_fix("thin"), "fill").pack(side="left")
        button(self.choices, "Slow down", lambda: self.speed_fix("slow"), "outline").pack(side="left", padx=10)
        button(self.choices, "Keep", lambda: self.speed_fix("keep"), "outline").pack(side="left")

        section(r, "Title").grid(row=5, column=0, sticky="w", pady=(18, 6))
        self.title = entry(r)
        self.title.grid(row=6, column=0, sticky="ew")

        bar = ctk.CTkFrame(r, fg_color="transparent")
        bar.grid(row=9, column=0, sticky="ew", pady=(0, 4))
        self.save_btn = button(bar, "Save to library", self.save, "fill")
        self.save_btn.pack(side="left")
        self.preview_btn = button(bar, "Preview", self.preview, "outline", 96)
        self.preview_btn.pack(side="left", padx=12)
        self.status = label(bar, "", 13, 400, t.MUTED)
        self.status.pack(side="left", padx=6)
        self.save_btn.configure(state="disabled")

    def choose(self):
        path = filedialog.askopenfilename(title="Choose a MIDI file", filetypes=[("MIDI", "*.mid *.midi")])
        if not path:
            return
        try:
            self.midi = midi_import.read(path)
        except Exception as e:
            self.status.configure(text=f"Couldn't read that file · {e}", text_color=t.ACCENT)
            return
        f = self.midi
        self.file.configure(text=Path(path).name)
        self.parts = {str(i): p for i, p in enumerate(f.parts) if not p.is_drums}
        self.info.configure(text=f"{len(self.parts)} parts · {round(f.tempo[0][1])} bpm")
        suggested = midi_import.suggest_melody(list(self.parts.values()))
        names = [p.name for p in self.parts.values()]
        rows = []
        for key, p in self.parts.items():
            lo, hi = p.range()
            tag = " · suggested" if p is suggested else ""
            title = p.name if names.count(p.name) == 1 else f"{p.instrument} · channel {p.channel + 1}"
            rows.append((key, title, f"{len(p.notes)} notes · {number_to_note(lo)}–{number_to_note(hi)}{tag}", bool(tag)))
        self.list.fill(rows)
        self.title.delete(0, "end")
        self.title.insert(0, Path(path).stem.replace("-", " ").replace("_", " ").title())
        first = next((k for k, p in self.parts.items() if p is suggested), next(iter(self.parts), None))
        if first:
            self.list.select(first)

    def part_chosen(self, key):
        self.build()

    def build(self):
        if not self.midi or self.list.current is None:
            return
        part = self.parts[self.list.current]
        s = settings.load()
        self.song, self.dropped = midi_import.to_song(self.midi, part, self.mode.get().lower())
        self.report = fit.fit(self.song, s)
        self.show_report()
        if self.report.too_fast:
            self.warn.configure(text=f"{self.report.too_fast} spots are too fast · pick a fix below")
            self.warn.pack(anchor="w", padx=18, pady=(0, 14))
            self.choices.grid(row=4, column=0, sticky="w", pady=(12, 0))
            self.save_btn.configure(state="disabled")
        else:
            self.warn.pack_forget()
            self.choices.grid_forget()
            self.save_btn.configure(state="normal")
        self.status.configure(text="")

    def show_report(self):
        lines = list(self.report.lines())
        if self.dropped:
            lines.append(f"Melody notes dropped for chords: {self.dropped}")
        self.fit.configure(text="\n".join(lines) or "Fits as it is")

    def speed_fix(self, choice):
        fit.fix_speed(self.song, settings.load(), self.report, choice)
        self.warn.pack_forget()
        self.choices.grid_forget()
        self.show_report()
        self.save_btn.configure(state="normal")

    def save(self):
        self.song.title = self.title.get().strip() or "Untitled"
        path = library.save(self.song)
        self.status.configure(text=f"Saved as {path.name}", text_color=t.SOFT)
        self.app.pages["Library"].refresh(select=path)
        self.app.show("Library")

    def preview(self):
        if self.app.previewer.busy:
            self.app.previewer.stop()
        elif self.song:
            self.preview_btn.configure(text="Stop")
            self.app.previewer.start(self.song, 1.0, lambda: self.preview_btn.configure(text="Preview"))