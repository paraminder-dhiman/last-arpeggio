import sys, time, winsound
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from arpeggio import settings
from arpeggio.song import Song
from arpeggio.planner import plan
from arpeggio.player import Player

s = settings.load()
song = Song.load(sys.argv[1] if len(sys.argv) > 1 else "examples/test-song.json")
p = plan(song, s)
print(f"{song.title} · {len(p.steps)} steps · {song.duration():.1f}s · problems: {p.problems or 'none'}")

player = Player(s)
player.game.focus()
for n in range(s["countdown"], 0, -1):
    print(f"  {n}", flush=True)
    winsound.Beep(880 if n > 1 else 1320, 80)
    time.sleep(0.92)

finished = player.play(p, on_step=lambda i, st: print(f"  {st.time:6.2f}s  step {i + 1}/{len(p.steps)}"))
late = player.late
print("Finished" if finished else "Stopped")
if late:
    print(f"Timing · average {sum(late) / len(late) * 1000:.1f} ms late · worst {max(late) * 1000:.1f} ms")