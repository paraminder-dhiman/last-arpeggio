import sys
import traceback
from pathlib import Path
import tkinter as tk
import customtkinter as ctk

from .. import settings
from ..library import ROOT
from . import icons, theme as t
from .import_page import ImportPage
from .library_page import LibraryPage
from .now_playing_page import NowPlayingPage
from .playing import Background, Previewer
from .settings_page import SettingsPage
from .widgets import Row, label

VERSION = "v0.1.0"
PAGES = [("Library", "library", LibraryPage), ("Import", "import", ImportPage), ("Settings", "settings", SettingsPage)]
DATA = Path(__file__).resolve().parent.parent / "data"

class App(ctk.CTk):
    def __init__(self):
        t.load_fonts()
        s = settings.load()
        ctk.set_appearance_mode(s.get("theme", "system"))
        if sys.platform == "win32":
            # its own taskbar entry and icon, instead of being grouped under Python's
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("TheLastArpeggio.App")
        super().__init__(fg_color=t.BASE)
        self.title("The Last Arpeggio")
        self.set_icon()
        self.geometry("1100x680")
        self.minsize(960, 620)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(0, weight=1)
        self.job, self.previewer = None, Previewer(self)

        self.sidebar = ctk.CTkFrame(self, width=214, corner_radius=0, fg_color=t.GROUND)
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)
        self.sidebar.columnconfigure(0, weight=1)
        self.sidebar.rowconfigure(len(PAGES), weight=1)
        ctk.CTkFrame(self, width=1, corner_radius=0, fg_color=t.HAIR).grid(row=0, column=1, sticky="ns")

        self.content = ctk.CTkFrame(self, corner_radius=0, fg_color=t.BASE)
        self.content.grid(row=0, column=2, sticky="nsew")
        self.content.columnconfigure(0, weight=1)
        self.content.rowconfigure(0, weight=1)

        self.nav, self.pages, self.current = {}, {}, None
        for i, (name, kind, Page) in enumerate(PAGES):
            pics = (icons.icon(kind, t.SOFT), icons.icon(kind, t.ACCENT), icons.icon(kind, t.DIM))
            row = Row(self.sidebar, name, icons=pics, nav=True, on_click=lambda n=name: self.show(n))
            row.grid(row=i, column=0, sticky="ew", padx=12, pady=(24 if i == 0 else 4, 4))
            self.nav[name] = row
            self.pages[name] = Page(self.content, self)

        self.pages["Now playing"] = NowPlayingPage(self.content, self)    # not in the sidebar

        foot = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        foot.grid(row=len(PAGES) + 1, column=0, sticky="w", padx=16, pady=16)
        self.toggle = ctk.CTkButton(foot, text="", image=icons.theme_toggle(t.MUTED), width=32, height=28,
                                    corner_radius=t.CONTROL_R, fg_color="transparent", hover_color=t.HOVER,
                                    border_width=1, border_color=t.HAIR, command=self.toggle_theme)
        self.toggle.pack(side="left")
        label(foot, VERSION, 13, 400, t.MUTED).pack(side="left", padx=12)

        self.show("Library")

    def set_icon(self):
        """The wheel-and-pick icon on the window and the taskbar."""
        try:
            if sys.platform == "win32":
                self.iconbitmap(str(DATA / "icon.ico"))       # also stops CustomTkinter putting its own icon there
            else:
                self.iconphoto(True, tk.PhotoImage(file=str(DATA / "icon.png")))
        except Exception:
            pass                                              # a missing icon shouldn't stop the app

    def show(self, name):
        if name == self.current or (self.busy and name != "Now playing"):
            return
        self.previewer.stop()
        self.current = name
        for n in self.nav:
            self.nav[n].select(n == name or (name == "Now playing" and n == "Library"))
        for n, page in self.pages.items():
            if n == self.current:
                page.grid(row=0, column=0, sticky="nsew", padx=28, pady=(0, 28))
            else:
                page.grid_forget()

    def report_callback_exception(self, kind, value, tb):
        text = "".join(traceback.format_exception(kind, value, tb))
        print(text)
        with (ROOT / "arpeggio.log").open("a", encoding="utf-8") as log:
            log.write(text + "\n")

    def set_theme(self, mode):
        ctk.set_appearance_mode(mode)
        s = settings.load()
        s["theme"] = mode
        settings.save(s)
        self.pages["Settings"].theme.set(mode.title())

    def toggle_theme(self):
        self.set_theme("light" if ctk.get_appearance_mode() == "Dark" else "dark")

    @property
    def busy(self):
        return self.job is not None

    def play_song(self, song, speed):
        """Opens Now playing and starts the song."""
        self.show("Now playing")
        self.pages["Now playing"].start(song, speed)

    def stop_job(self):
        if self.job:
            self.job.player.stop.set()

    def lock(self, on):
        """While a song plays, any click in the app would take focus from the game, so the sidebar is locked."""
        for row in self.nav.values():
            row.lock(on)
        self.toggle.configure(state="disabled" if on else "normal")

    def run(self, job, on_message):
        self.job, self.on_message = Background(job), on_message
        self.lock(True)
        self.after(50, self.poll)

    def poll(self):
        for kind, value in self.job.poll():
            self.on_message(kind, value)
            if kind in ("done", "error"):
                self.job = None
                self.lock(False)
                self.lift()
                self.focus_force()
                return
        self.after(50, self.poll)