import json
from dataclasses import dataclass, field
from pathlib import Path

from . import guitar

FORMAT, VERSION = "last-arpeggio-song", 1

@dataclass
class Event:
    kind: str               # "note" (pluck one string) or "strum" (a whole chord)
    beat: float             # when it starts
    length: float           # how long it lasts, in beats
    pitch: int = None       # for notes · the note number
    chord: str = None       # for strums · the chord name, like "Am"

@dataclass
class Song:
    title: str
    artist: str = ""
    tempo: list = field(default_factory=lambda: [(0.0, 120.0)])    # (from beat, beats per minute)
    events: list = field(default_factory=list)
    meter: tuple = (4, 4)        # time signature
    mode: str = "melody"         # melody, chords or both
    source: str = ""             # where it came from, like the MIDI file's name
    shift: int = 0               # semitones the song was moved to fit the guitar

    def seconds_at(self, beat):
        """Where a beat falls in time, following every tempo change before it."""
        seconds, (last_beat, bpm) = 0.0, self.tempo[0]
        for change_beat, change_bpm in self.tempo[1:]:
            if change_beat >= beat:
                break
            seconds += (change_beat - last_beat) * 60 / bpm
            last_beat, bpm = change_beat, change_bpm
        return seconds + (beat - last_beat) * 60 / bpm

    def duration(self):
        end = max((e.beat + e.length for e in self.events), default=0)
        return self.seconds_at(end)

    def to_dict(self):
        return {
            "format": FORMAT, "version": VERSION,
            "title": self.title, "artist": self.artist, "mode": self.mode,
            "source": self.source, "shift": self.shift, "meter": list(self.meter),
            "tempo": [list(t) for t in self.tempo],
            "events": [{"kind": e.kind, "beat": e.beat, "length": e.length,
                        **({"note": guitar.number_to_note(e.pitch)} if e.kind == "note" else {"chord": e.chord})}
                       for e in self.events],
        }

    @classmethod
    def from_dict(cls, d):
        if d.get("format") != FORMAT:
            raise ValueError("Not a Last Arpeggio song file")
        if d.get("version", 0) > VERSION:
            raise ValueError("This song was saved by a newer version of the app")
        events = [Event(e["kind"], e["beat"], e["length"],
                        pitch=guitar.note_to_number(e["note"]) if e["kind"] == "note" else None,
                        chord=e.get("chord"))
                  for e in d["events"]]
        return cls(d["title"], d.get("artist", ""), [tuple(t) for t in d["tempo"]], events,
                   tuple(d.get("meter", (4, 4))), d.get("mode", "melody"), d.get("source", ""), d.get("shift", 0))

    def save(self, path):
        Path(path).write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path):
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))