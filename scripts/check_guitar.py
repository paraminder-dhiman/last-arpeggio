import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from arpeggio import guitar

low, high = guitar.LOWEST, guitar.HIGHEST
missing = [guitar.number_to_note(n) for n in range(low, high + 1) if not guitar.places_for(n)]
print("Wheels:", guitar.WHEELS, "· home:", guitar.WHEELS[guitar.HOME_WHEEL])
print("Range:", guitar.number_to_note(low), "to", guitar.number_to_note(high))
print("Missing notes:", missing or "none")
print("Chords:", len(guitar.CHORD_PLACES), sorted(guitar.CHORD_PLACES))
print("E4 can be played at:", guitar.places_for(guitar.note_to_number("E4")))
print("Am is at:", guitar.places_of_chord("Am"), "· G# is at:", guitar.places_of_chord("G#"))