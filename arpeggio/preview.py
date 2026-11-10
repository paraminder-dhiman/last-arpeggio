import math
import wave
import winsound
from functools import lru_cache
import numpy as np
from .guitar import NOTE_NAMES

RATE  = 44100

def freq(pitch):
    return 440.0 * 2 ** ((pitch - 69) / 12)

@lru_cache(maxsize=None)
def pluck(pitch, seconds=1.5):
    t = np.arange(int(RATE * seconds)) / RATE
    f = freq(pitch)
    tone = np.zeros_like(t)
    for h in range(1, 7):
        tone += np.sin(2 * np.pi * f * h * t) * np.exp(-t * (2 + 1.5 * h)) / h
    return tone * np.minimum(t / 0.004, 1)

def chord_pitches(name):
    minor = name.endswith("m")
    root = NOTE_NAMES.index(name[:-1] if minor else name)
    low = 40 + (root - 4) % 12
    third = 3 if minor else 4
    return [low, low + 7, low + 12, low + 12 + third, low + 19, low + 24]

def render(plan, ring=1.5):
    if not plan.steps:
        return np.zeros(1)
    out = np.zeros(int((plan.steps[-1].time + ring + 0.5) * RATE))
    for step in plan.steps:
        e = step.event
        if e.chord:
            hits, gain = [(p, i * 0.015) for i, p in enumerate(chord_pitches(e.chord))], 0.25
        else:
            hits, gain = [(e.pitch, 0.0)], 0.6
        for pitch, delay in hits:
            start = int((step.time + delay) * RATE)
            tone = pluck(pitch, ring)[: len(out) - start] * gain
            out[start:start + len(tone)] += tone
    return out / (np.abs(out).max() or 1) * 0.8

def save_wav(samples, path):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes((samples * 32767).astype("<i2").tobytes())

def play(path):
    winsound.PlaySound(str(path), winsound.SND_FILENAME | winsound.SND_ASYNC)

def stop():
    winsound.PlaySound(None, 0)