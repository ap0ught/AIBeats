"""Shared helpers for the Terra Tubes 'helicopter' investigation (2026-10-09, l9heli_fix_*.py).

up14 frame f (1-based input count) = L9c index f - 17366.  cap14.ram row f-1 = RAM after input f.
Object tables are 15 wide: id $3C1+q, anim $3B5+q, x $3FD+q | $3EE+q<<8, h $439+q | $42A+q<<8, sub-x $448+q,
air $475+q, facing $4A2+q, hp $51A+q, speed $565+q.  Slot 0 = the toad.
"""
import json
import numpy as np
from toads.emulator import BizHawk, LOGS_DIR

OFF = 17366                      # up14 frame = L9c index + OFF
CARRIED = (36, 37)


def up14_inputs():
    return [l.strip() for l in open(LOGS_DIR / "up14.inputs.txt") if not l.startswith("#")]


def bt(l):
    return tuple(x for x in l.replace(",", "+").split("+") if x)


def cap():
    return np.memmap(LOGS_DIR / "cap14.ram", dtype=np.uint8, mode="r").reshape(-1, 2048)


def toad(m):
    return dict(x=m[0x3FD] | m[0x3EE] << 8, H=m[0x439] | m[0x42A] << 8, h=m[0x439], z=m[0x475], an=m[0x3B5], spd=m[0x565],
                sub=m[0x448], face=m[0x4A2] & 0x40, hp=m[0x51A], lives=m[0x11], camx=m[0x87] | m[0x88] << 8,
                camy=m[0x89] | m[0x8A] << 8, cp=m[0x585], t=m[0x0B], t2=m[0x0C], lvl=m[0x10])


def tstr(m):
    s = toad(m)
    return (f"x {s['x']} H {s['H']} z {s['z']} an {s['an']} spd {s['spd']} sub {s['sub']} hp {s['hp']} cam {s['camx']},{s['camy']} "
            f"t {s['t']},{s['t2']} cp {s['cp']}")


def objs(m, lo=1, hi=15):
    out = []
    for q in range(lo, hi):
        i = m[0x3C1 + q]
        if i:
            out.append((q, i, m[0x3FD + q] | m[0x3EE + q] << 8, m[0x439 + q] | m[0x42A + q] << 8, m[0x51A + q], m[0x3B5 + q]))
    return out


def ostr(m):
    return " ".join(f"{i:02x}@{q}:{x},{H & 255}/{H >> 8},{hp}" for q, i, x, H, hp, an in objs(m))


def goto(e, frame, ins=None, check=True):
    """Load the nearest cap14 bookmark at or below `frame` and replay up14 inputs up to (and including) input `frame`."""
    ins = ins or up14_inputs()
    base = frame // 1000 * 1000
    e.load(f"cap14_f{base}")
    for i in range(base, frame):
        e.step(bt(ins[i]), 1)
    m = e.ram(0, 0x800)
    if check:
        R = cap()
        ref = bytes(R[frame - 1])
        d = [a for a in range(0x800) if m[a] != ref[a]]
        if d:
            raise RuntimeError(f"replay to {frame} differs from cap14 in {len(d)} bytes: {d[:20]}")
    return m


def run(e, seq):
    """Step a list of input strings; returns the last RAM."""
    m = None
    for b in seq:
        e.step(bt(b), 1)
    return e.ram(0, 0x800)


def banned(b):
    s = set(bt(b))
    return ("Left" in s and "Right" in s) or ("Up" in s and "Down" in s)
