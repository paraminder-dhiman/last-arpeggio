import copy
import queue
import threading
import time
import winsound

from .. import guitar, preview, settings
from ..library import ROOT
from ..planner import plan
from ..player import Player

WAV = ROOT / "build" / "preview.wav"


def at_speed(song, speed):
    if speed >= 0.999:
        return song
    slower = copy.deepcopy(song)
    slower.tempo = [(beat, bpm * speed) for beat, bpm in slower.tempo]
    return slower


def seconds(song):
    d = song.duration
    return d() if callable(d) else d


def clock(secs):
    return f"{int(secs // 60)}:{int(secs % 60):02d}"

class Background:
    """Runs a job on a thread; the window reads its messages with poll()."""

    def __init__(self, job):
        self.messages = queue.Queue()
        self.s = settings.load()
        self.player = Player(self.s)
        threading.Thread(target=self._run, args=(job,), daemon=True).start()

    def say(self, kind, value=None):
        self.messages.put((kind, value))

    def _run(self, job):
        listener = None
        try:
            game = self.player.game
            game.focus()
            listener = self.player._listen()
            for n in range(int(self.s["countdown"]), 0, -1):
                if self.player.stop.is_set():
                    break
                self.say("count", n)
                winsound.Beep(660, 120)
                time.sleep(0.88)
            if self.player.stop.is_set():
                self.say("done", "Stopped")
                return
            winsound.Beep(990, 200)
            self.say("done", job(self))
        except Exception as e:
            self.say("error", str(e))
        finally:
            if listener:
                listener.stop()
            try:
                self.player.game.go_home()
            except Exception:
                pass

    def poll(self):
        out = []
        while not self.messages.empty():
            out.append(self.messages.get())
        return out

def play_job(song, speed):
    def job(run):
        run.say("playing")
        finished = run.player.play(plan(at_speed(song, speed), run.s), lambda i, st: run.say("step", (i, st)))
        if not finished:
            return "Stopped"
        late = run.player.late
        avg = sum(late) / len(late) * 1000 if late else 0
        return f"Finished · notes landed {avg:.0f} ms late on average"
    return job


def wheel_test_job(run):
    run.say("playing")
    for d in guitar.DIRECTIONS:
        if run.player.stop.is_set():
            return "Stopped"
        run.player.game.strum(guitar.HOME_WHEEL, d)
        time.sleep(0.6)
    return "Wheel test done · did all six strums land?"

class Previewer:
    """Plays a song through the speakers; one at a time."""

    def __init__(self, window):
        self.window, self.timer = window, None

    def start(self, song, speed, on_end):
        self.stop()
        p = plan(at_speed(song, speed), settings.load())
        WAV.parent.mkdir(exist_ok=True)
        preview.save_wav(preview.render(p), WAV)
        preview.play(str(WAV))
        self.on_end = on_end
        self.timer = self.window.after(int(seconds(at_speed(song, speed)) * 1000) + 1500, self.stop)

    def stop(self):
        if self.timer:
            self.window.after_cancel(self.timer)
            self.timer = None
            preview.stop()
            self.on_end()

    @property
    def busy(self):
        return self.timer is not None