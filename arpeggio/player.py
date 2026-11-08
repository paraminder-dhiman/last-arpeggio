import threading
import time
from pynput import keyboard

from .game import Game
from .planner import Plan

def wait_until(moment, stop):
    """Sleep until a moment on the clock · sleeps in short naps, then waits the last bit exactly."""
    while not stop.is_set():
        left = moment - time.perf_counter()
        if left <= 0:
            return
        if left > 0.003:
            time.sleep(min(left - 0.002, 0.05))

class Player:
    def __init__(self, settings):
        self.s = settings
        self.stop = threading.Event()
        self.game = Game(settings)
        self.late = []                       # how late each sound landed, in seconds

    def _listen(self):
        stop_key = getattr(keyboard.Key, self.s["stop_key"])
        def on_press(key):
            if key == stop_key:
                self.stop.set()
                return False                 # ends the listener
        listener = keyboard.Listener(on_press=on_press)
        listener.start()
        return listener

    def play(self, plan: Plan, on_step=None):
        self.stop.clear()
        listener = self._listen()
        head = max((st.lead for st in plan.steps[:1]), default=0) + 0.1
        t0 = time.perf_counter() + head
        try:
            for i, st in enumerate(plan.steps):
                wait_until(t0 + st.time - st.lead, self.stop)
                if self.stop.is_set():
                    break
                self.game.prepare(st.place)
                wait_until(t0 + st.time, self.stop)
                if self.stop.is_set():
                    break
                self.late.append(time.perf_counter() - (t0 + st.time))
                self.game.sound(st.place)
                if on_step:
                    on_step(i, st)
        finally:
            listener.stop()
            self.game.go_home()
        return not self.stop.is_set()