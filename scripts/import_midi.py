import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from arpeggio import midi_import, settings, fit
from arpeggio.planner import plan

f = midi_import.read(sys.argv[1])
part = f.parts[int(sys.argv[2])] if len(sys.argv) > 2 else midi_import.suggest_melody(f.parts)
mode = sys.argv[3] if len(sys.argv) > 3 else "melody"
s = settings.load()
song, dropped = midi_import.to_song(f, part, mode)
report = fit.fit(song, s)
if report.too_fast:
    answer = input(f"{report.too_fast} spots are too fast · [t]hin out · [s]low down · [k]eep? ").strip().lower()
    choice = {"t": "thin", "s":"slow"}.get(answer[:1], "keep")
    fit.fix_speed(song, s, report, choice)
Path("songs").mkdir(exist_ok=True)
out = Path("songs") / f"{f.name}.json"
song.save(out)

p = plan(song, s)
skipped = sum(1 for _, m in p.problems if "isn't on" in m)
fast = sum(1 for _, m in p.problems if "too fast" in m)
print(f"Saved {out} · {len(song.events)} events · {song.duration():.0f}s · {p.switches} wheel switches")
print(f"Out of range (skipped for now): {skipped} · too fast: {fast}")
print(f"Mode: {mode} · melody notes dropped for chords: {dropped}")
print("First chords:", " · ".join(e.chord for e in song.events if e.chord)[:200])
for line in report.lines():
    print(" " + line)