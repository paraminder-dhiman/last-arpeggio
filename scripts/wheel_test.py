import sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from arpeggio import guitar, settings
from arpeggio.game import Game

def run(game, wheel, wait=0.8):
    print(f"\nWheel {guitar.WHEELS[wheel]}")
    for direction in guitar.DIRECTIONS:
        print(f"  {direction:<12} should be {guitar.chord_at(wheel, direction)}")
        game.strum(wheel, direction)
        time.sleep(wait)

if __name__ == "__main__":
    game = Game(settings.load())
    print("Sit at the guitar on the C wheel · switching to the game in 3 seconds")
    time.sleep(3)
    game.focus()
    time.sleep(2)
    for wheel in (guitar.HOME_WHEEL, 3, 1):
        run(game, wheel)
    game.go_home()
    print("\nDone · back on the C wheel")