import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from arpeggio import guitar, midi_import

f = midi_import.read(sys.argv[1])
melody = midi_import.suggest_melody(f.parts)
print(f"{f.name} · {len(f.parts)} parts · tempo {f.tempo[0][1]:.0f} bpm ({len(f.tempo)} tempo changes) · {f.meter[0]}/{f.meter[1]}")
for i, p in enumerate(f.parts):
    lo, hi = p.range()
    mark = "  <- suggested melody" if p is melody else ""
    print(f"  {i}: {p.name:<24} {p.instrument:<16} {len(p.notes):>5} notes  {guitar.number_to_note(lo)}–{guitar.number_to_note(hi)}{mark}")