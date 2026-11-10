import customtkinter as ctk
from . import theme as t

def label(master, text, size=14, weight=400, colour=t.TEXT, **kw):
    return ctk.CTkLabel(master, text=text, font=t.font(size, weight), text_color=colour,
                        height=size + 8, anchor="w", justify="left", **kw)

def section(master, text):
    return label(master, text.upper(), 12, 500, t.MUTED)

def panel(master, **kw):
    return ctk.CTkFrame(master, corner_radius=t.PANEL_R, fg_color=t.GROUND,
                        border_width=1, border_color=t.HAIR, **kw)

def button(master, text, command, kind="fill", width=None):
    look = {
        "fill":    dict(fg_color=t.ACCENT, hover_color=t.ACCENT_HI, text_color=t.ON_ACCENT, border_width=0,
                        text_color_disabled=t.FADED),
        "outline": dict(fg_color="transparent", hover_color=t.TINT, text_color=t.ACCENT,
                        border_width=1, border_color=t.ACCENT),
        "quiet":   dict(fg_color="transparent", hover_color=t.HOVER, text_color=t.MUTED, border_width=0),
    }[kind]
    look.setdefault("text_color_disabled", t.MUTED)
    f = t.font(14, 400 if kind == "quiet" else 500)
    return ctk.CTkButton(master, text=text, command=command, height=32, corner_radius=t.CONTROL_R,
                         width=width or f.measure(text) + 32, font=f, **look)

def entry(master, width=200, **kw):
    return ctk.CTkEntry(master, width=width, height=34, corner_radius=t.CONTROL_R, fg_color=t.GROUND,
                        border_width=1, border_color=t.HAIR, text_color=t.TEXT, font=t.font(14), **kw)

def slider(master, command, **kw):
    return ctk.CTkSlider(master, command=command, height=18, fg_color=t.HAIR, progress_color=t.ACCENT,
                         button_color=t.ACCENT, button_hover_color=t.ACCENT_HI, **kw)

class Row(ctk.CTkFrame):
    """A selectable rounded pill with a short accent bar on the left."""

    def __init__(self, master, title, sub="", on_click=None, sub_accent=False, icons=None, nav=False):
        super().__init__(master, corner_radius=t.CONTROL_R, fg_color="transparent")
        self.on_click, self.icons, self.nav, self.selected, self.locked = on_click, icons, nav, False, False
        self.columnconfigure(1, weight=1)
        if icons:
            self.pic = ctk.CTkLabel(self, text="", image=icons[0], width=20, height=20)
            self.pic.grid(row=0, column=0, padx=(16, 0), pady=8)
        self.title = label(self, title, 15, 400 if nav else 500, t.SOFT if nav else t.TEXT)
        self.title.grid(row=0, column=1, padx=(12 if icons else 14, 12), pady=(8, 0 if sub else 8), sticky="w")
        if sub:
            self.sub = label(self, sub, 13, 400, t.ACCENT if sub_accent else t.MUTED)
            self.sub.grid(row=1, column=1, padx=(14, 12), pady=(0, 8), sticky="w")
        self.bar = ctk.CTkFrame(self, width=3, height=28 if sub else 18, corner_radius=2, fg_color=t.ACCENT)
        for w in (self, *self.winfo_children()):
            w.bind("<Button-1>", self._click)
            w.bind("<Enter>", lambda e: self._hover(True))
            w.bind("<Leave>", lambda e: self._hover(self._inside()))

    def _inside(self):
        w = self.winfo_containing(*self.winfo_pointerxy())
        return w is not None and str(w).startswith(str(self))

    def _hover(self, on):
        if not self.selected and not self.locked:
            self.configure(fg_color=t.HOVER if on else "transparent")

    def _click(self, _):
        if self.on_click and not self.locked:
            self.on_click()

    def lock(self, on):
        """Dims the row and ignores clicks, e.g. the sidebar while a song plays."""
        self.locked = on
        if not self.selected:
            self.configure(fg_color="transparent")
            self.title.configure(text_color=t.DIM if on else (t.SOFT if self.nav else t.TEXT))
            if self.icons and len(self.icons) > 2:
                self.pic.configure(image=self.icons[2 if on else 0])

    def select(self, on):
        self.selected = on
        self.configure(fg_color=t.TINT if on else "transparent")
        if on:
            self.bar.place(x=0, rely=0.5, anchor="w")
        else:
            self.bar.place_forget()
        if self.nav:
            self.title.configure(text_color=t.TEXT if on else t.SOFT, font=t.font(15, 500 if on else 400))
        if self.icons:
            self.pic.configure(image=self.icons[1 if on else 0])

class RowList(ctk.CTkScrollableFrame):
    """A rounded panel holding Rows separated by hairlines; one can be selected."""

    def __init__(self, master, on_select, **kw):
        super().__init__(master, corner_radius=t.PANEL_R, fg_color=t.GROUND, border_width=1,
                         border_color=t.HAIR, scrollbar_button_color=t.HAIR,
                         scrollbar_button_hover_color=t.MUTED, **kw)
        self.on_select, self.rows, self.current = on_select, {}, None

    def fill(self, items):
        """items: list of (key, title, sub, sub_accent)"""
        for w in self.winfo_children():
            w.destroy()
        self.rows, self.current = {}, None
        for i, (key, title, sub, accent) in enumerate(items):
            if i:
                ctk.CTkFrame(self, height=1, corner_radius=0, fg_color=t.HAIR).pack(fill="x", padx=14)
            row = Row(self, title, sub, lambda k=key: self.select(k), accent)
            row.pack(fill="x", padx=2, pady=4)
            self.rows[key] = row

    def select(self, key):
        if key not in self.rows:
            return
        if self.current in self.rows:
            self.rows[self.current].select(False)
        self.current = key
        self.rows[key].select(True)
        self.on_select(key)

class Segmented(ctk.CTkFrame):
    """A rounded track with a rounded highlight on the chosen value."""

    def __init__(self, master, values, command, width=110):
        super().__init__(master, corner_radius=9, fg_color=t.GROUND, border_width=1, border_color=t.HAIR)
        self.command, self.value, self.buttons = command, None, {}
        for i, v in enumerate(values):
            b = ctk.CTkButton(self, text=v, width=width, height=28, corner_radius=6, font=t.font(14, 500),
                              fg_color="transparent", hover_color=t.HOVER, text_color=t.SOFT,
                              command=lambda v=v: self.set(v, notify=True))
            b.grid(row=0, column=i, padx=(3 if i == 0 else 0, 3), pady=3)
            self.buttons[v] = b

    def set(self, value, notify=False):
        self.value = value
        for v, b in self.buttons.items():
            on = v == value
            b.configure(fg_color=t.ACCENT if on else "transparent", text_color=t.ON_ACCENT if on else t.SOFT,
                        hover_color=t.ACCENT_HI if on else t.HOVER)
        if notify:
            self.command(value)

    def get(self):
        return self.value