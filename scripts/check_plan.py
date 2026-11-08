import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from arpeggio import guitar, settings
from arpeggio.song import Song
from arpeggio.planner import plan

song = Song.load(sys.argv[1] if len(sys.argv) > 1 else "examples/test-song.json")
p = plan(song, settings.load())
print(f"{song.title} · {len(p.steps)} steps · {p.switches} wheel switches")
for st in p.steps:
    e, pl = st.event, st.place
    what = guitar.number_to_note(e.pitch) if e.kind == "note" else e.chord
    how = f"string key {pl.key}" if pl.key else "strum"
    print(f"  {st.time:6.2f}s  lead {st.lead:.2f}s  {what:<4} wheel {guitar.WHEELS[pl.wheel]:<3} {pl.direction:<12} {how}")
print("Problems:", p.problems or "none")