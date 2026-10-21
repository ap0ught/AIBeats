"""Small helpers for stage 7 experiments on a worker emulator (second pass). Not part of the solver.

    seq("R20 RA2 R30 RUB2 N5")  -> rows   (R Right, L Left, U Up, D Down, A, B, S Start, N nothing; number = frames)
    show(tr, every=1, types=(...))        print one line per frame
"""
from __future__ import annotations

LET = {"R": "Right", "L": "Left", "U": "Up", "D": "Down", "A": "A", "B": "B", "S": "Start"}


def seq(s):
    rows = []
    for tok in s.split():
        i = 0
        while i < len(tok) and not tok[i].isdigit():
            i += 1
        btn = tuple(LET[c] for c in tok[:i] if c != "N")
        n = int(tok[i:]) if i < len(tok) else 1
        rows.extend([btn] * n)
    return rows


def line(i, f, types=()):
    s = (f"{i:4d} wx {f.wx:4d} x {f['x']:3d} y {f['y']:3d} yv {f['yvel']:3d} j {f['jump']:02x} fl {f['fall']} "
         f"on {f['onen']} bar {f['barrier']:3d} fc {f['fc']:3d} lag {f['lagged']} nb {f.nbullets()}"
         f"{' DEAD' if f.dead else ''}")
    for e in f.enemies():
        if e["type"] in types:
            s += f" | t{e['type']:02x} s{e['slot']} ({e['x'] + f.cam},{e['y']}) hp {e['hp']} r {e['routine']} a {e['attr']:02x}"
    return s


def show(tr, every=1, types=(), start=0, only=None):
    for i, f in enumerate(tr):
        if (i % every == 0 or f.dead) and (only is None or only(f)):
            print(line(start + i, f, types))


def grounded(f):
    return (f["jump"] & 15) == 0 and f["fall"] == 0
