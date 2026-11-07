import json
from dataclasses import dataclass
from pathlib import Path

DATA = Path(__file__).parent / "data" / "chords.json"

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

def note_to_number(name):
    pitch, octave = name[:-1], int(name[-1])
    return NOTE_NAMES.index(pitch.upper()) + 12 * (octave + 1)

def number_to_note(number):
    return f"{NOTE_NAMES[number % 12]}{number // 12 - 1}"

DIRECTIONS = {"top": 90, "topright": 30, "bottomright": -30,
              "bottom": -90, "bottomleft": -150, "topleft": 150}


@dataclass(frozen=True)
class Place:
    wheel: int          # 0 to 4, in key_order
    direction: str      # one of DIRECTIONS
    key: int            # the string's key in the game, 1 to 6

def _load():
    data = json.loads(DATA.read_text())
    wheels = data["key_order"]
    note_places, chord_places = {}, {}
    for w, wheel in enumerate(wheels):
        for direction, info in data["chord_data"][wheel].items():
            chord_places[info["chord"]] = (w, direction)
            for i, note in enumerate(info["strings"]):
                n = note_to_number(note)
                note_places.setdefault(n, []).append(Place(w, direction, 6 - i))
    return wheels, note_places, chord_places

WHEELS, NOTE_PLACES, CHORD_PLACES = _load()
HOME_WHEEL = WHEELS.index("C")
LOWEST, HIGHEST = min(NOTE_PLACES), max(NOTE_PLACES)

def places_for(note):
    return NOTE_PLACES.get(note, [])

def place_of_chord(name):
    return CHORD_PLACES.get(name)