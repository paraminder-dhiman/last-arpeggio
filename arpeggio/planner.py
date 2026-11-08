from dataclasses import dataclass

from . import guitar
from .song import Song, Event

@dataclass
class Step:
    time: float             # when the sound should happen (seconds)
    lead: float             # how long before that the moving has to start
    place: guitar.Place     # where to play it · key is None for a strum
    event: Event

@dataclass
class Plan:
    steps: list
    problems: list          # (time in seconds, message)
    switches: int           # wheel switches across the whole song

def wheel_steps(a, b):
    n = len(guitar.WHEELS)
    return min((b - a) % n, (a - b) % n)

def move_time(frm, to, s):
    """Seconds to get from one place to the next: wheel taps, then flicks."""
    t = wheel_steps(frm.wheel, to.wheel) * (s["tap"] + s["settle"])
    if frm.direction != to.direction:
        t += s["settle"] * (2 if frm.direction else 1)      # back to the centre (if aimed), then out
    return t

def candidates(event):
    if event.kind == "note":
        return guitar.places_for(event.pitch)
    return [guitar.Place(w, d, None) for w, d in guitar.places_of_chord(event.chord)]

def plan(song: Song, s) -> Plan:
    events = sorted(song.events, key=lambda e: e.beat)
    problems = []
    playable = []
    for e in events:
        if candidates(e):
            playable.append(e)
        else:
            what = guitar.number_to_note(e.pitch) if e.kind == "note" else e.chord
            problems.append((song.seconds_at(e.beat), f"{what} isn't on the guitar · skipped"))

    start = guitar.Place(guitar.HOME_WHEEL, None, None)        # the C wheel, mouse at the centre
    best = [{start: (0.0, None)}]                              # per event: place -> (total time, previous place)
    for e in playable:
        layer = {}
        for c in candidates(e):
            layer[c] = min(((cost + move_time(p, c, s), p) for p, (cost, _) in best[-1].items()),
                           key=lambda t: t[0])
        best.append(layer)

    route, place = [], min(best[-1], key=lambda c: best[-1][c][0])
    for layer in reversed(best[1:]):
        route.append(place)
        place = layer[place][1]
    route.reverse()

    steps, prev, prev_time, switches = [], start, None, 0
    for e, place in zip(playable, route):
        t = song.seconds_at(e.beat)
        lead = move_time(prev, place, s)
        if prev_time is not None and t - lead < prev_time + s["tap"]:
            need, have = lead + s["tap"], t - prev_time
            problems.append((t, f"too fast · needs {need:.2f}s, has {have:.2f}s"))
        switches += wheel_steps(prev.wheel, place.wheel)
        steps.append(Step(t, lead, place, e))
        prev, prev_time = place, t
    return Plan(steps, sorted(problems), switches)