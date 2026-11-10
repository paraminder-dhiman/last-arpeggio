import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from arpeggio import midi_import, settings, guitar
from arpeggio.planner import plan

f = midi_import.read(sys.argv[1])
part = f.parts[int(sys.argv[2])] if len(sys.argv) > 2 else midi_import.suggest_melody(f.parts)
mode = sys.argv[4] if len(sys.argv) > 4 else "melody"
song, dropped = midi_import.to_song(f, part, mode)
shift = int(sys.argv[3]) if len(sys.argv) > 3 else 0
for e in song.events:
    if e.pitch is not None:
        e.pitch += shift
    if e.chord is not None:
        e.chord = guitar.shift_chord(e.chord, shift)
song.shift = shift
Path("songs").mkdir(exist_ok=True)
out = Path("songs") / f"{f.name}.json"
song.save(out)

p = plan(song, settings.load())
skipped = sum(1 for _, m in p.problems if "isn't on" in m)
fast = sum(1 for _, m in p.problems if "too fast" in m)
print(f"Saved {out} · {len(song.events)} events · {song.duration():.0f}s · {p.switches} wheel switches")
print(f"Out of range (skipped for now): {skipped} · too fast: {fast}")
print(f"Mode: {mode} · melody notes dropped for chords: {dropped}")
print("First chords:", " · ".join(e.chord for e in song.events if e.chord)[:200])