<p align="center"><img src="arpeggio/data/icon.png" width="96" alt="The Last Arpeggio icon"></p>

<h1 align="center">The Last Arpeggio</h1>

<p align="center">Play songs on the guitar in <i>The Last of Us Part II</i>, from any MIDI file.</p>

<p align="center">
  <a href="https://github.com/paraminder-dhiman/last-arpeggio/releases/latest">Download for Windows</a> ·
  <a href="#getting-started">Getting started</a> ·
  <a href="#importing-a-song">Importing a song</a> ·
  <a href="#settings">Settings</a>
</p>

<!-- demo GIF goes here once it's recorded: docs/demo.gif -->

> A fan-made tool. Not affiliated with or endorsed by Naughty Dog or Sony Interactive Entertainment.

## What it does

The guitar in Part II is played with a wheel of chords and six strings. The Last Arpeggio reads a MIDI file, works out where every note and chord sits on that wheel, and then plays the song in the game for you, moving the mouse and pressing the keys in time.

- **Import any MIDI file** · pick the part to play, and the app suggests the melody for you
- **Three modes** · play the melody, the chords, or both together
- **Fits the song to the guitar** · moves it into the guitar's range (E2 to A4), keeps the key when it can, and folds stray notes into an octave that fits
- **Fixes spots that are too fast** · thins out the busiest notes, or slows the song down, or leaves it as it is · your choice
- **Plans the wheel moves** · picks the route round the wheel with the fewest switches, so fast passages stay playable
- **Preview through your speakers** before playing it in the game
- **Now playing screen** · the wheel, the note or chord and the bar as they're played, with how close to the beat the notes landed
- **Stop any time** with a key of your choice (F8 by default)
- **Light and dark themes**, following Windows or set by hand

## Getting started

1. Download `TheLastArpeggio-v0.1.0-windows.zip` from the [latest release](https://github.com/paraminder-dhiman/last-arpeggio/releases/latest) and unzip it anywhere.
2. Run `TheLastArpeggio.exe`.
   Windows may show a blue *Windows protected your PC* box, because the app isn't signed with a paid certificate. Click **More info**, then **Run anyway**.
3. Start the game and pick up a guitar, so the chord wheel is on screen.
4. In the app, open **Settings**:
   - **Game window** · click **Choose** and pick the game from the list (the app usually finds it by itself)
   - **Test the wheel** · it switches to the game, counts down, and strums all six directions. If any miss, raise **Flick distance** a little and test again
5. Open **Library**, pick a song and press **Play**. The app switches to the game and counts down from 5 · keep your hands off the mouse while it plays.

Two example songs come with the app, both in the public domain: **Greensleeves** (melody and chords) and **Ode to Joy** (melody only). Ode to Joy is the easier one to start with.

## Importing a song

1. Open **Import** and choose a `.mid` file.
2. **Pick a part.** Drums are hidden, and the part that looks most like the melody is marked *suggested*.
3. **Pick a mode** · Melody, Chords or Both.
4. **Check the fit.** The panel shows how the song was moved to fit the guitar. If some spots are too fast to play, pick a fix:
   - **Thin out** (recommended) · drops the fewest notes needed, one at a time, where it's busiest
   - **Slow down** · lowers the tempo in small steps until everything fits
   - **Keep** · plays it as it is · fast spots may come out late
5. Give it a title, **Preview** it if you like, and **Save to library**.

In the Library you can also play any song slower (50 to 100 percent) without changing the saved file.

**Tips**
- Piano MIDI files often put the tune in the right hand · try that part in Melody mode first
- Simple arrangements play best · the guitar plays one note at a time, and the wheel needs a moment to switch
- Only major and minor chords exist on the guitar · other chords are matched to the nearest one

## Songs from the game

The app doesn't ship any music from the game, but you can play the main theme, **The Last of Us** by Gustavo Santaolalla, with a MIDI file of it that you have:

1. Import it and pick the part with the guitar line (often called *Guitar*, *Lead* or *Right Hand*).
2. Use **Melody** mode · the theme is a single, slow line, which suits the guitar well.
3. If anything shows as too fast, **Thin out** usually costs only a note or two.
4. Play it at 100 percent, or a touch slower if the game misses notes on your machine.

## Settings

| Setting | What it does | Default |
|---|---|---|
| Flick distance | How far the mouse moves to pick a direction on the wheel | 400 |
| Settle | Seconds to wait after aiming, so the game registers it | 0.05 |
| Tap | Seconds a key is held down | 0.03 |
| Countdown | Seconds before playing starts, after the app switches to the game | 5 |
| Stop key | Press it in the game to stop · click the button, then press any key or combo | F8 |
| Game window | The game's window, picked from a list of open windows | found by name |
| Theme | System, Light or Dark | System |

If notes are missed, raise **Settle** a little (0.06 to 0.08). If the wheel picks the wrong direction, adjust **Flick distance** · it depends on your mouse sensitivity in the game.

Your songs are kept in the `songs` folder and your settings in `settings.json`, both next to the app, so you can move or back up the whole folder.

## Known limits

- Windows only, and the game has to be in front while a song plays · clicking anything else stops the keys reaching it
- The guitar covers E2 to A4 and major and minor chords only
- Very fast passages can't be played as written · the app tells you where, and offers to thin them out or slow the song down
- Some antivirus programs are wary of apps that press keys and move the mouse, which is exactly what this one does. The full source is here if you'd rather run it yourself

## Running from source

Needs Python 3.12 on Windows.

```
git clone https://github.com/paraminder-dhiman/last-arpeggio.git
cd last-arpeggio
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

To build the release yourself, run `python scripts/build_release.py`. The app lands in `dist/TheLastArpeggio`, and the zip in `release`.

## How it was made

Built by Paraminder Dhiman. I used Claude, Anthropic's AI assistant, throughout the project: to plan it, to write and review much of the code, and to design the interface. I tested and tuned everything in the game myself.

## Credits

- [IBM Plex Sans](https://github.com/IBM/plex), by IBM, under the SIL Open Font License (included in `arpeggio/data/fonts`)
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) (MIT) for the interface
- [mido](https://github.com/mido/mido) (MIT) for reading MIDI files
- [pynput](https://github.com/moses-palmer/pynput) (LGPL-3.0) for the stop key · used unmodified
- [PyDirectInput](https://github.com/learncodebygaming/pydirectinput) (MIT) and [PyGetWindow](https://github.com/asweigart/PyGetWindow) (BSD) for talking to the game
- [NumPy](https://numpy.org) (BSD) and [Pillow](https://python-pillow.org) (MIT-CMU) for the preview sound and the icons

## License

[MIT](LICENSE) · the code, the icon and the example songs. *The Last of Us* is a trademark of Sony Interactive Entertainment.
