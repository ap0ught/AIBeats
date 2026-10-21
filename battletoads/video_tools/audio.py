"""Sound for the video, all synthesised here (no third-party audio): NES-flavoured sound effects for the graphics
(slam, whoosh, blip, tick, riser, ding, glitch, crash) and an original chiptune beat for the montage and the slams.
Everything is 48 kHz stereo float32 numpy arrays; write with `save(path, x)`."""
from __future__ import annotations

import json
import subprocess
import wave
from pathlib import Path

import numpy as np

SR = 48000
HERE = Path(__file__).resolve().parent
SFX_DIR = HERE / "sfx"
SFX_DIR.mkdir(exist_ok=True)
rng = np.random.default_rng(7)


def t_(dur):
    return np.arange(int(dur * SR)) / SR


def env(n, a=0.005, d=0.2, shape=3.0):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / max(d, 1e-4) * shape / 3)
    return e


def square(freq, dur, duty=0.5):
    t = t_(dur)
    f = np.broadcast_to(freq, t.shape) if np.ndim(freq) else np.full(t.shape, freq)
    ph = np.cumsum(f) / SR
    return np.where((ph % 1) < duty, 1.0, -1.0)


def tri(freq, dur):
    t = t_(dur)
    f = np.broadcast_to(freq, t.shape) if np.ndim(freq) else np.full(t.shape, freq)
    ph = np.cumsum(f) / SR
    return 2 * np.abs(2 * (ph % 1) - 1) - 1


def noise(dur, step=1):
    n = int(dur * SR)
    x = rng.uniform(-1, 1, n // step + 1).repeat(step)[:n]
    return x


def lowpass(x, cut):
    a = np.exp(-2 * np.pi * cut / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):            # short sounds only
        acc = (1 - a) * v + a * acc
        y[i] = acc
    return y


def stereo(x, pan=0.0):
    l, r = np.sqrt(0.5 * (1 - pan)), np.sqrt(0.5 * (1 + pan))
    return np.stack([x * l, x * r], 1).astype(np.float32)


def norm(x, peak=0.9):
    m = np.abs(x).max() or 1
    return x / m * peak


# ---------------------------------------------------------------- effects
def sfx_slam():
    d = 0.9
    t = t_(d)
    boom = np.sin(2 * np.pi * np.cumsum(40 + 110 * np.exp(-t * 18)) / SR) * env(len(t), 0.002, 0.45)
    crack = lowpass(noise(d), 5000) * env(len(t), 0.001, 0.06)
    crunch = square(55 * np.exp(-t * 3) + 30, d, 0.25) * env(len(t), 0.001, 0.12) * 0.35
    return stereo(norm(boom * 1.0 + crack * 0.8 + crunch))


def sfx_whoosh():
    d = 0.45
    t = t_(d)
    n = noise(d)
    sweep = lowpass(n, 2500) * np.sin(np.pi * t / d) ** 2
    return np.stack([sweep * (1 - t / d) + sweep * 0.3, sweep * (t / d) + sweep * 0.3], 1).astype(np.float32) * 0.8 / (np.abs(sweep).max() or 1)


def sfx_blip(f=880):
    d = 0.09
    x = square(np.where(t_(d) < 0.03, f, f * 1.5), d, 0.25) * env(int(d * SR), 0.001, 0.05)
    return stereo(x * 0.5)


def sfx_tick():
    d = 0.03
    return stereo(square(2400, d, 0.125) * env(int(d * SR), 0.0005, 0.01) * 0.35)


def sfx_ding():
    d = 0.8
    t = t_(d)
    x = (square(1318.5, d, 0.5) * 0.5 + square(1975.5, d, 0.25) * 0.3) * env(len(t), 0.002, 0.35)
    x[int(0.08 * SR):] += (square(2637, d - 0.08, 0.5) * env(len(t) - int(0.08 * SR), 0.002, 0.3) * 0.35)
    return stereo(x * 0.5)


def sfx_riser(d=1.6):
    t = t_(d)
    f = 200 * (8 ** (t / d))
    x = square(f, d, 0.25) * (t / d) ** 2 * 0.35 + lowpass(noise(d), 4000) * (t / d) ** 3 * 0.4
    return stereo(x)


def sfx_glitch():
    d = 0.5
    x = noise(d, 37) * 0.5 + square(np.repeat(rng.uniform(80, 1200, 25), int(d * SR / 25) + 1)[:int(d * SR)], d, 0.5) * 0.3
    return stereo(x * env(int(d * SR), 0.001, 0.4))


def sfx_crash():
    d = 1.0
    t = t_(d)
    x = noise(d, 3) * env(len(t), 0.001, 0.5) * 0.8 + np.sin(2 * np.pi * np.cumsum(60 + 80 * np.exp(-t * 10)) / SR) * env(len(t), 0.001, 0.4)
    return stereo(norm(x, 0.8))


SFX = dict(slam=sfx_slam, whoosh=sfx_whoosh, blip=sfx_blip, tick=sfx_tick, ding=sfx_ding, riser=sfx_riser,
           glitch=sfx_glitch, crash=sfx_crash)


def sfx(name):
    p = SFX_DIR / f"{name}.wav"
    if not p.exists():
        save(p, SFX[name]())
    return p


# ---------------------------------------------------------------- an original chiptune loop
NOTE = {n: 440 * 2 ** ((i - 9) / 12) for i, n in enumerate("C C# D D# E F F# G G# A A# B".split())}


def hz(n):
    name, octv = n[:-1], int(n[-1])
    return NOTE[name] * 2 ** (octv - 4)


def chiptune(bars=8, bpm=150, seed=0, intensity=1.0):
    """driving minor-key NES-style loop: triangle kick+bass, noise snare/hats, square arpeggio lead"""
    beat = 60 / bpm
    step = beat / 4
    n = int(bars * 16 * step * SR)
    out = np.zeros(n)
    prog = [("A2", "A3 C4 E4"), ("F2", "F3 A3 C4"), ("G2", "G3 B3 D4"), ("E2", "E3 G#3 B3")]
    for bar in range(bars):
        root, chord = prog[bar % 4]
        chord = [hz(c) for c in chord.split()]
        for s in range(16):
            i0 = int((bar * 16 + s) * step * SR)
            # kick on 1 and 3 (+ the "and" of 4)
            if s in (0, 8) or (s == 14 and bar % 2):
                d = 0.18
                tt = t_(d)
                k = np.sin(2 * np.pi * np.cumsum(50 + 180 * np.exp(-tt * 40)) / SR) * env(len(tt), 0.001, 0.12)
                out[i0:i0 + len(k)] += k[:max(0, n - i0)] * 0.9
            # snare on 2 and 4
            if s in (4, 12):
                d = 0.16
                sn = noise(d, 2) * env(int(d * SR), 0.001, 0.08) * 0.5
                out[i0:i0 + len(sn)] += sn[:max(0, n - i0)]
            # hats on 8ths
            if s % 2 == 0 and intensity > 0.5:
                d = 0.04
                hh = noise(d, 1) * env(int(d * SR), 0.0005, 0.015) * 0.18
                out[i0:i0 + len(hh)] += hh[:max(0, n - i0)]
            # bass: octave-bouncing 8ths on the triangle
            if s % 2 == 0:
                f = hz(root) * (2 if s % 4 == 2 else 1)
                d = step * 2 * 0.9
                b = tri(f, d) * env(int(d * SR), 0.002, 0.5) * 0.55
                out[i0:i0 + len(b)] += b[:max(0, n - i0)]
            # lead: 16th arpeggio on a 25% square, one octave up
            if intensity > 0.3:
                f = chord[s % 3] * 2
                d = step * 0.95
                ld = square(f, d, 0.25) * env(int(d * SR), 0.002, 0.12) * 0.16 * intensity
                out[i0:i0 + len(ld)] += ld[:max(0, n - i0)]
    out = np.tanh(out * 1.1) * 0.8
    return np.stack([out, out], 1).astype(np.float32)


# ---------------------------------------------------------------- io + mixing
def save(path, x):
    x = np.clip(x, -1, 1)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x * 32767).astype("<i2").tobytes())
    return path


def load(path):
    """any audio file -> 48k stereo float32 via ffmpeg"""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
                         capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).copy()


def game_audio(src, start_frame, n_frames, fps=60.0988):
    """the capture's own sound for capture frames [start, start+n)"""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{start_frame / fps:.5f}", "-t", f"{n_frames / fps:.5f}",
                          "-i", str(src), "-vn", "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"], capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).copy()


class Mix:
    """place clips on a timeline (seconds) and render one stereo track"""

    def __init__(self, dur):
        self.buf = np.zeros((int(dur * SR) + SR, 2), np.float32)

    def add(self, t, x, gain=1.0):
        i = int(t * SR)
        if i >= len(self.buf):
            return
        x = x[:len(self.buf) - i]
        self.buf[i:i + len(x)] += x * gain

    def add_sfx(self, t, name, gain=1.0):
        self.add(t, load(sfx(name)), gain)

    def add_cues(self, t0, cue_file, gain=0.8):
        p = Path(cue_file)
        if p.exists():
            for c in json.loads(p.read_text()):
                self.add_sfx(t0 + c["t"], c["sfx"], gain)

    def duck(self, t0, t1, k=0.35):
        a, b = int(t0 * SR), int(t1 * SR)
        self.buf[a:b] *= k

    def write(self, path, dur=None):
        x = self.buf if dur is None else self.buf[:int(dur * SR)]
        peak = np.abs(x).max()
        if peak > 0.98:
            x = np.tanh(x / peak * 1.5) * 0.95
        return save(path, x)


if __name__ == "__main__":
    for k in SFX:
        sfx(k)
    save(SFX_DIR / "loop150.wav", chiptune(8))
    print("ok", sorted(p.name for p in SFX_DIR.iterdir()))
