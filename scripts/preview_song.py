import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from arpeggio import preview, settings
from arpeggio.song import Song
from arpeggio.planner import plan

song = Song.load(sys.argv[1])
p = plan(song, settings.load())
out = Path("build") / "preview.wav"
out.parent.mkdir(exist_ok=True)
preview.save_wav(preview.render(p), out)

print(f"{song.title} · {len(p.steps)} steps · {out} · press Enter to stop")
preview.play(out)
input()
preview.stop()