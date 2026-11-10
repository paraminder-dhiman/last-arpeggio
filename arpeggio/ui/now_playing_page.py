import time
import customtkinter as ctk

from .. import guitar, settings
from . import theme as t
from .playing import at_speed, clock, play_job, seconds
from .library_page import key_text
from .widgets import button, label, panel, section


class NowPlayingPage(ctk.CTkFrame):
    """The countdown, the live wheel · note · bar while a song plays, and the result when it ends."""

    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app, self.song, self.speed, self.ticker = app, None, 1.0, None
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        c = ctk.CTkFrame(self, fg_color="transparent")
        c.grid(row=1, column=0)
        section(c, "Now in the game").pack()
        self.title = label(c, "", 32, 500)
        self.title.pack(pady=(6, 0))
        self.meta = label(c, "", 14, 400, t.MUTED)
        self.meta.pack(pady=(2, 0))

        # the middle swaps between the countdown, the live stats and the result
        self.mid = ctk.CTkFrame(c, fg_color="transparent")
        self.mid.pack(pady=(28, 0))

        self.count = ctk.CTkFrame(self.mid, fg_color="transparent")
        self.number = ctk.CTkLabel(self.count, text="", font=t.font(96), text_color=t.ACCENT, height=110)
        self.number.pack()
        label(self.count, "The game is in front · get to the guitar · playing starts at 0",
              14, 400, t.SOFT).pack(pady=(4, 0))

        self.stats = panel(self.mid)
        self.values = {}
        for i, name in enumerate(("Wheel", "Note", "Bar")):
            self.stats.columnconfigure(i, uniform="stat", minsize=150)
            cap = section(self.stats, name)
            cap.grid(row=0, column=i, padx=20, pady=(16, 0))
            value = ctk.CTkLabel(self.stats, text="", font=t.font(38), height=50,
                                 text_color=t.ACCENT if name == "Note" else t.TEXT)
            value.grid(row=1, column=i, padx=20, pady=(0, 16))
            self.values[name] = (cap, value)

        self.result = ctk.CTkFrame(self.mid, fg_color="transparent")
        self.result_title = label(self.result, "", 22, 500)
        self.result_title.pack()
        self.result_line = label(self.result, "", 14, 400, t.SOFT)
        self.result_line.pack(pady=(4, 0))

        bar = ctk.CTkFrame(c, fg_color="transparent")
        bar.pack(pady=(28, 0))
        bar.columnconfigure(1, weight=1)
        self.progress = ctk.CTkProgressBar(bar, width=520, height=6, corner_radius=3,
                                           fg_color=t.HAIR, progress_color=t.ACCENT)
        self.progress.grid(row=0, column=0, columnspan=2)
        self.elapsed = label(bar, "0:00", 13, 400, t.MUTED)
        self.elapsed.grid(row=1, column=0, sticky="w", pady=(6, 0))
        self.total = label(bar, "0:00", 13, 400, t.MUTED)
        self.total.grid(row=1, column=1, sticky="e", pady=(6, 0))

        # while playing: the stop key hint and a Stop button
        self.live = ctk.CTkFrame(c, fg_color="transparent")
        hint = ctk.CTkFrame(self.live, fg_color="transparent")
        hint.pack()
        label(hint, "Press", 14, 400, t.SOFT).pack(side="left")
        chip = ctk.CTkFrame(hint, fg_color="transparent", border_width=1, border_color=t.ACCENT, corner_radius=6)
        chip.pack(side="left", padx=8)
        self.key = ctk.CTkLabel(chip, text="", font=t.font(13, 500), text_color=t.ACCENT, height=22)
        self.key.pack(padx=9, pady=2)
        label(hint, "any time to stop", 14, 400, t.SOFT).pack(side="left")
        button(self.live, "Stop", app.stop_job, "outline", 96).pack(pady=(16, 0))

        # when it's over: play again or go back
        self.after_bar = ctk.CTkFrame(c, fg_color="transparent")
        button(self.after_bar, "Play again", self.play_again, "fill").pack(side="left")
        button(self.after_bar, "Back to library", lambda: app.show("Library"), "outline").pack(side="left", padx=12)

    # ── starting ──

    def start(self, song, speed):
        self.song, self.speed = song, speed
        self.title.configure(text=song.title)
        self.meta.configure(text=f"{song.mode.title()} · {round(speed * 100)}% speed · {key_text(song.shift)}")
        self.values["Note"][0].configure(text="CHORD" if song.mode == "chords" else "NOTE")
        played = at_speed(song, speed)
        self.length = seconds(played)
        beats_per_bar = song.meter[0] if song.meter else 4
        last_beat = max((e.beat + e.length for e in song.events), default=0)
        self.bars = max(1, int(-(-last_beat // beats_per_bar)))
        self.beats_per_bar = beats_per_bar
        self.total.configure(text=clock(self.length))
        self.key.configure(text=settings.key_label(settings.load()["stop_key"]))
        self.last_step, self.got_step = (0.0, None), False
        self.set_progress(0)
        self.show_part(self.count)
        self.number.configure(text=str(settings.load()["countdown"]))
        self.after_bar.pack_forget()
        self.live.pack(pady=(26, 0))
        self.app.run(play_job(song, speed), self.on_message)

    def play_again(self):
        if self.song and not self.app.busy:
            self.start(self.song, self.speed)

    # ── while it runs ──

    def on_message(self, kind, value):
        if kind == "count":
            self.number.configure(text=str(value))
        elif kind == "playing":
            self.show_part(self.stats)
            for name in self.values:
                self.values[name][1].configure(text="–")
            self.tick()
        elif kind == "step":
            self.step(*value)
        else:
            self.finish(kind, value)

    def step(self, i, st):
        e = st.event
        self.got_step = True
        self.last_step = (st.time, time.perf_counter())
        self.values["Wheel"][1].configure(text=guitar.WHEELS[st.place.wheel])
        self.values["Note"][1].configure(text=e.chord if e.chord else guitar.number_to_note(e.pitch))
        bar = int(e.beat // self.beats_per_bar) + 1
        self.values["Bar"][1].configure(text=f"{bar} / {self.bars}")

    def tick(self):
        """Moves the clock along smoothly between notes."""
        at, wall = self.last_step
        now = at + (time.perf_counter() - wall) if wall else 0.0
        self.set_progress(now)
        self.ticker = self.after(200, self.tick)

    def set_progress(self, secs):
        secs = max(0.0, min(secs, self.length))
        self.progress.set(secs / self.length if self.length else 0)
        self.progress.configure(progress_color=t.ACCENT if secs > 0 else t.HAIR)
        self.elapsed.configure(text=clock(secs))

    # ── when it's over ──

    def finish(self, kind, value):
        if self.ticker:
            self.after_cancel(self.ticker)
            self.ticker = None
        stopped_at = self.last_step[0] if self.got_step else 0.0
        if kind == "error":
            title, line, colour = "Couldn't start", value, t.ACCENT
        elif value == "Stopped":
            title = "Stopped"
            line = f"At {clock(stopped_at)} of {clock(self.length)}" if self.got_step else "Before the first note"
            colour = t.SOFT
        else:
            title, line, colour = "Finished", value.replace("Finished · ", "").capitalize(), t.SOFT
            self.set_progress(self.length)
        self.result_title.configure(text=title)
        self.result_line.configure(text=line, text_color=colour)
        self.show_part(self.result)
        self.live.pack_forget()
        self.after_bar.pack(pady=(26, 0))

    def show_part(self, part):
        for p in (self.count, self.stats, self.result):
            if p is part:
                p.pack()
            else:
                p.pack_forget()
