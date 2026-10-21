"""The memory hunt: find out what the 2 KB of RAM means by experiment, not by reading anyone's notes.

Every explore.py session leaves logs/<name>.ram.npy (frames x 2048 bytes) and the input held each frame.
These helpers ask the questions a person with a hex editor would ask:

    changed(arr, f)                  which bytes changed between frame f-1 and f
    stable(arr, lo, hi)              bytes that never change in [lo, hi)
    differs(a, fa, b, fb)            bytes that differ between two sessions' frames
    monotone(arr, lo, hi)            bytes that only ever go up (or only down) in [lo, hi)
    button_effect(arr, inputs, btn)  bytes whose per-frame delta differs when btn is held vs not
    counters(arr)                    bytes that tick +1 every frame (timers) - usually useless, good to exclude
    show(arr, addrs, lo, hi, step)   print a small table of those bytes over time
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

PROJECT = Path(__file__).resolve().parent.parent
LOGS = PROJECT / "logs"


def load(name: str):
    arr = np.load(LOGS / f"{name}.ram.npy")
    p = LOGS / f"{name}.ram_inputs.txt"
    inputs = p.read_text().split("\n") if p.exists() else [""] * len(arr)
    return arr, inputs


def changed(arr, f: int) -> np.ndarray:
    return np.nonzero(arr[f] != arr[f - 1])[0]


def stable(arr, lo: int = 0, hi: int | None = None) -> np.ndarray:
    seg = arr[lo:hi]
    return np.nonzero((seg == seg[0]).all(axis=0))[0]


def differs(a, fa: int, b, fb: int) -> np.ndarray:
    return np.nonzero(a[fa] != b[fb])[0]


def monotone(arr, lo: int = 0, hi: int | None = None, min_span: int = 8):
    seg = arr[lo:hi].astype(int)
    d = np.diff(seg, axis=0)
    up = (d >= 0).all(axis=0) & ((seg[-1] - seg[0]) >= min_span)
    down = (d <= 0).all(axis=0) & ((seg[0] - seg[-1]) >= min_span)
    return np.nonzero(up)[0], np.nonzero(down)[0]


def held(inputs, btn: str) -> np.ndarray:
    return np.array([btn in s.split("+") for s in inputs])


def button_effect(arr, inputs, btn: str, min_frames: int = 30):
    """Bytes whose mean per-frame delta while btn is held differs from while it is not.
    Returns list of (addr, mean delta held, mean delta not held) sorted by |difference|."""
    h = held(inputs, btn)[1:]
    d = np.diff(arr.astype(int), axis=0)
    # treat wraps as small moves
    d = np.where(d > 127, d - 256, np.where(d < -128, d + 256, d))
    if h.sum() < min_frames or (~h).sum() < min_frames:
        return []
    mh = d[h].mean(axis=0)
    mn = d[~h].mean(axis=0)
    out = [(int(a), float(mh[a]), float(mn[a])) for a in range(arr.shape[1]) if abs(mh[a] - mn[a]) > 0.05]
    return sorted(out, key=lambda t: -abs(t[1] - t[2]))


def counters(arr) -> np.ndarray:
    d = np.diff(arr.astype(int), axis=0) % 256
    return np.nonzero((d == 1).mean(axis=0) > 0.95)[0]


def activity(arr, lo: int = 0, hi: int | None = None) -> np.ndarray:
    """How many frames each byte changed in [lo, hi)."""
    seg = arr[lo:hi]
    return (np.diff(seg, axis=0) != 0).sum(axis=0)


def show(arr, addrs, lo: int = 0, hi: int | None = None, step: int = 1, inputs=None):
    hi = len(arr) if hi is None else hi
    print("frame  " + " ".join(f"{a:04x}" for a in addrs))
    for f in range(lo, hi, step):
        row = " ".join(f"{int(arr[f][a]):4d}" for a in addrs)
        tail = f"  {inputs[f]}" if inputs else ""
        print(f"{f:5d}  {row}{tail}")


if __name__ == "__main__":
    arr, inputs = load(sys.argv[1])
    print(arr.shape)
    print("counters:", [hex(a) for a in counters(arr)])
    act = activity(arr)
    busy = np.argsort(-act)[:30]
    print("busiest:", [(hex(a), int(act[a])) for a in busy])
