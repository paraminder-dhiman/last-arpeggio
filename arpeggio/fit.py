import copy
from dataclasses import dataclass
from . import guitar
from .planner import plan

@dataclass
class Report:
    shift: int = 0
    octave_moves: int = 0
    thinned: int = 0
    speed: float = 1.0
    too_fast: int = 0

    def lines(self):
        out = [f"Shift: {self.shift:+d} semitones" + (" (same key)" if self.shift % 12 == 0 else ""),
               f"Moved an octave to fit: {self.octave_moves}"]
        if self.thinned: out.append(f"Thinned out: {self.thinned}")
        if self.speed < 1: out.append(f"Slowed to {self.speed:.0%}")
        if self.too_fast: out.append(f"Still too fast: {self.too_fast}")
        return out

def notes_of(song):
    return [e for e in song.events if e.pitch is not None]

def outside(pitch):
    return pitch < guitar.LOWEST or pitch > guitar.HIGHEST

def apply_shift(song, shift):
    for e in song.events:
        if e.pitch is not None:
            e.pitch += shift
        if e.chord is not None:
            e.chord = guitar.shift_chord(e.chord, shift)
    song.shift += shift

def best_shift(song, s):
    pitches = [e.pitch for e in notes_of(song)]
    if not pitches:
        return 0
    misses = {k: sum(outside(p + k) for p in pitches) for k in range(-24, 25)}
    fewest = min(misses.values())
    tied = [k for k, m in misses.items() if m == fewest]
    best_octave = min((k for k in misses if k % 12 == 0), key=lambda k: misses[k])
    if misses[best_octave] - fewest <= max(2, len(pitches) // 10):
        tied = [k for k in misses if k % 12 == 0 and misses[k] == misses[best_octave]]
    else:
        tied = sorted(tied, key=abs)[:6]

    def switches(k):
        trial = copy.deepcopy(song)
        apply_shift(trial, k)
        return plan(trial, s).switches

    return min(tied, key=lambda k: (switches(k), abs(k)))

def fold_octaves(song):
    moved = 0
    for e in notes_of(song):
        start = e.pitch
        while e.pitch < guitar.LOWEST:
            e.pitch += 12
        while e.pitch > guitar.HIGHEST:
            e.pitch -= 12
        moved += e.pitch != start
    return moved

def too_fast(song, s):
    return [t for t, m in plan(song, s).problems if "too fast" in m]

def thin(song, s):
    dropped = 0
    while True:
        times = too_fast(song, s)
        if not times:
            return dropped
        e = min(song.events, key=lambda e: abs(song.seconds_at(e.beat) - times[0]))
        song.events.remove(e)
        dropped += 1

def slow(song, s, lowest=0.5):
    original = list(song.tempo)
    speed = 1.0
    while too_fast(song, s) and speed > lowest + 1e-9:
        speed = round(speed - 0.05, 2)
        song.tempo = [(b, bpm * speed) for b, bpm in original]
    return speed

def fit(song, s):
    r = Report()
    r.shift = best_shift(song, s)
    apply_shift(song, r.shift)
    r.octave_moves = fold_octaves(song)
    r.too_fast = len(too_fast(song, s))
    return r

def fix_speed(song, s, r, choice):
    if choice == "thin":
        r.thinned = thin(song, s)
    elif choice == "slow":
        r.speed = slow(song, s)
    r.too_fast = len(too_fast(song, s))