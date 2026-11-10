import customtkinter as ctk

from .. import game
from . import theme as t
from .widgets import RowList, button, label


class WindowPicker(ctk.CTkFrame):
    """Covers the Settings page with a list of open windows · picking one sets the game window."""

    def __init__(self, master, on_pick):
        super().__init__(master, fg_color=t.BASE, corner_radius=0)
        self.on_pick, self.chosen = on_pick, None
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        label(self, "Pick the game window", 26, 500).grid(row=0, column=0, sticky="w", pady=(18, 4))
        label(self, "Start the game first, then pick it from the windows open right now.",
              14, 400, t.MUTED).grid(row=1, column=0, sticky="nw", pady=(0, 16))

        self.list = RowList(self, self.select)
        self.list.grid(row=2, column=0, sticky="nsew")

        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.grid(row=3, column=0, sticky="ew", pady=(18, 0))
        self.use_btn = button(bar, "Use this window", self.use, "fill")
        self.use_btn.pack(side="left")
        button(bar, "Refresh", self.refresh, "outline").pack(side="left", padx=12)
        button(bar, "Cancel", self.close, "quiet").pack(side="left")

    def open(self):
        self.place(x=0, y=0, relwidth=1, relheight=1)
        self.lift()
        self.refresh()

    def refresh(self):
        titles = game.open_windows()
        self.list.fill([(title, title, "looks like the game" if game.looks_like_game(title) else "",
                         game.looks_like_game(title)) for title in titles])
        self.chosen = None
        self.use_btn.configure(state="disabled")
        guess = next((title for title in titles if game.looks_like_game(title)), None)
        if guess:
            self.list.select(guess)

    def select(self, title):
        self.chosen = title
        self.use_btn.configure(state="normal")

    def use(self):
        if self.chosen:
            self.on_pick(self.chosen)
        self.close()

    def close(self):
        self.place_forget()
