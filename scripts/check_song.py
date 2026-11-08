import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from arpeggio import guitar
from arpeggio.song import Song

song = Song.load("examples/test-song.json")
print(f"{song.title} · {len(song.events)} events · {song.duration():.2f} seconds")
for e in song.events:
    what = guitar.number_to_note(e.pitch) if e.kind == "note" else e.chord
    print(f"  beat {e.beat:>5}  at {song.seconds_at(e.beat):6.2f}s  {e.kind:<5} {what}")

song.save("examples/test-song-copy.json")
same = Song.load("examples/test-song-copy.json").to_dict() == song.to_dict()
print("Saved and reloaded identically:", same)
Path("examples/test-song-copy.json").unlink()