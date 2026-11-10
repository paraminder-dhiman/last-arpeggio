from dataclasses import dataclass, field
from pathlib import Path
import mido

from .song import Song, Event
from .guitar import NOTE_NAMES

FAMILIES = ["Piano", "Chromatic percussion", "Organ", "Guitar", "Bass", "Strings", "Ensemble", "Brass",
            "Reed", "Pipe", "Synth lead", "Synth pad", "Synth effects", "Ethnic", "Percussive", "Sound effects"]
MELODY_WORDS = ("melody", "lead", "vocal", "voice", "sing", "solo")

CHORD_SHAPES = {"": (0, 4, 7), "m": (0, 3, 7)}   # major · minor, as semitones above the root

@dataclass
class Note:
    beat: float
    length: float
    pitch: int

@dataclass
class Part:
    name: str
    instrument: str
    channel: int
    notes: list = field(default_factory=list)

    @property
    def is_drums(self):
        return self.channel == 9

    def range(self):
        return (min(n.pitch for n in self.notes), max(n.pitch for n in self.notes)) if self.notes else (0, 0)

@dataclass
class MidiFile:
    name: str
    parts: list
    tempo: list
    meter: tuple

def read(path):
    mid = mido.MidiFile(path)
    tpb = mid.ticks_per_beat
    tempo, meter, parts = [], (4, 4), {}
    for t, track in enumerate(mid.tracks):
        tick, programs, open_notes = 0, {}, {}
        for msg in track:
            tick += msg.time
            beat = tick / tpb
            if msg.type == "set_tempo":
                tempo.append((beat, round(mido.tempo2bpm(msg.tempo), 3)))
            elif msg.type == "time_signature" and tick == 0:
                meter = (msg.numerator, msg.denominator)
            elif msg.type == "program_change":
                programs[msg.channel] = msg.program
            elif msg.type == "note_on" and msg.velocity > 0:
                open_notes[(msg.channel, msg.note)] = beat
            elif msg.type in ("note_off", "note_on"):
                start = open_notes.pop((msg.channel, msg.note), None)
                if start is not None:
                    key = (t, msg.channel)
                    if key not in parts:
                        group = FAMILIES[programs.get(msg.channel, 0) // 8]
                        parts[key] = Part(track.name.strip() or f"Track {t + 1}", "Drums" if msg.channel == 9 else group, msg.channel)
                    parts[key].notes.append(Note(start, beat - start, msg.note))

    tempo = sorted(set(tempo)) or [(0.0, 120.0)]
    if tempo[0][0] > 0:
        tempo.insert(0, (0.0, tempo[0][1]))
    for p in parts.values():
        p.notes.sort(key=lambda n: (n.beat, -n.pitch))
    return MidiFile(Path(path).stem, [p for p in parts.values() if p.notes], tempo, meter)

def suggest_melody(parts):
    def score(p):
        if p.is_drums or len(p.notes) < 16:
            return -1
        starts = {round(n.beat, 2) for n in p.notes}
        single = len(starts) / len(p.notes)                  # 1.0 = never two notes at once
        high = sum(n.pitch for n in p.notes) / len(p.notes)  # average pitch
        named = 30 if any(w in p.name.lower() for w in MELODY_WORDS) else 0
        return single * 40 + high * 0.5 + named
    best = max(parts, key=score, default=None)
    return best if best and score(best) >= 0 else None

def quantize(x, grid):
    return round(x / grid) * grid

def melody_events(part, grid=0.25):
    by_start = {}
    for n in part.notes:
        start = quantize(n.beat, grid)
        if start not in by_start or n.pitch > by_start[start].pitch:
            by_start[start] = Note(start, max(grid, quantize(n.length, grid)), n.pitch)
    notes = sorted(by_start.values(), key=lambda n: n.beat)
    for a, b in zip(notes, notes[1:]):
        a.length = min(a.length, b.beat - a.beat)
    return [Event("note", n.beat, n.length, pitch=n.pitch) for n in notes]

def to_song(f, part, mode="melody", grid=0.25):
    events, dropped = [], 0
    if mode in ("melody", "both"):
        events = melody_events(part, grid)
    if mode in ("chords", "both"):
        chords = chord_events(f.parts, f.meter[0] if mode == "both" else 1.0)
        if mode == "both":
            busy = {c.beat for c in chords}
            dropped = sum(1 for e in events if e.beat in busy)
            events = [e for e in events if e.beat not in busy]
        events = sorted(events + chords, key=lambda e: e.beat)
    return Song(title=f.name, tempo=f.tempo, events=events, meter=f.meter, mode=mode, source=f"{f.name}.mid"), dropped

def name_chord(pitches):
    classes = {p % 12 for p in pitches}
    if len(classes) < 2:
        return None
    bass = min(pitches) % 12
    best, best_score = None, 0
    for root in range(12):
        for suffix, shape in CHORD_SHAPES.items():
            tones = {(root + i) % 12 for i in shape}
            score = len(classes & tones) * 2 - len(classes - tones) + (1 if root == bass else 0)
            if score > best_score:
                best, best_score = NOTE_NAMES[root] + suffix, score
    return best if best_score >= 4 else None

def chord_events(parts, step=1.0):
    notes = [n for p in parts if not p.is_drums for n in p.notes]
    if not notes:
        return []
    end = max(n.beat + n.length for n in notes)
    events, current, beat = [], None, 0.0
    while beat < end:
        sounding = [n.pitch for n in notes if n.beat < beat + step and n.beat + n.length > beat]
        name = name_chord(sounding)
        if name and name != current:
            if events:
                events[-1].length = beat - events[-1].beat
            events.append(Event("strum", beat, step, chord=name))
            current = name
        beat += step
    if events:
        events[-1].length = end - events[-1].beat
    return events