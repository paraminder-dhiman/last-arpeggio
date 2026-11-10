import math
import time
import pydirectinput
import pygetwindow

from . import guitar

pydirectinput.PAUSE = 0
pydirectinput.FAILSAFE = False

APP_TITLE = "The Last Arpeggio"


def looks_like_game(title):
    return "last of us part ii" in title.lower().replace("™", "")


def open_windows():
    """Titles of the windows open on the desktop, for picking the game."""
    titles = []
    for w in pygetwindow.getAllWindows():
        title = w.title.strip()
        if title and title not in (APP_TITLE, "Program Manager") and title not in titles:
            titles.append(title)
    return sorted(titles, key=str.lower)

class Game:
    """Everything that touches the game: the mouse picks chords, the keys switch wheels and play."""

    def __init__(self, settings):
        self.s = settings
        self.wheel = guitar.HOME_WHEEL      # songs start on the C wheel
        self.aimed = None                   # the direction the mouse points at, or None at the centre
        self.offset = (0, 0)                # how far the mouse is from the centre

    def _tap(self, key):
        pydirectinput.keyDown(key)
        time.sleep(self.s["tap"])
        pydirectinput.keyUp(key)

    def centre(self):
        if self.aimed:
            dx, dy = self.offset
            pydirectinput.moveRel(-dx, -dy, relative=True)
            self.aimed, self.offset = None, (0, 0)
            time.sleep(self.s["settle"])

    def aim(self, direction):
        if self.aimed == direction:
            return
        self.centre()
        angle = math.radians(guitar.DIRECTIONS[direction])
        d = self.s["flick_distance"]
        dx, dy = round(math.cos(angle) * d), round(-math.sin(angle) * d)
        pydirectinput.moveRel(dx, dy, relative=True)
        self.aimed, self.offset = direction, (dx, dy)
        time.sleep(self.s["settle"])

    def switch_wheel(self, target):
        n = len(guitar.WHEELS)
        forward, back = (target - self.wheel) % n, (self.wheel - target) % n
        key, steps = ("e", forward) if forward <= back else ("q", back)
        for _ in range(steps):
            self._tap(key)
            time.sleep(self.s["settle"])
        self.wheel = target

    def prepare(self, place):
        self.switch_wheel(place.wheel)
        self.aim(place.direction)

    def sound(self, place):
        self._tap(str(place.key) if place.key else "space")

    def pluck(self, place):
        self.prepare(place)
        self.sound(place)

    def strum(self, wheel, direction):
        self.prepare(guitar.Place(wheel, direction, None))
        self.sound(guitar.Place(wheel, direction, None))

    def go_home(self):
        self.centre()
        self.switch_wheel(guitar.HOME_WHEEL)

    def find(self):
        """The game's window: the one picked in Settings, or anything that looks like the game."""
        title = self.s["window_title"].strip()
        windows = pygetwindow.getWindowsWithTitle(title) if title else []
        if not windows:
            windows = [w for w in pygetwindow.getAllWindows() if looks_like_game(w.title)]
        return windows[0] if windows else None

    def focus(self):
        window = self.find()
        if window is None:
            raise RuntimeError("Couldn't find the game · is it running? You can pick its window in Settings")
        try:
            window.activate()
        except pygetwindow.PyGetWindowException:
            window.minimize()                 # Windows sometimes refuses activate() · this brings it forward instead
            window.restore()
        time.sleep(0.5)