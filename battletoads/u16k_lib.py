"""Track K (2026-10-10): shared helpers for the Karnath warp-room probes (u16k_*.py).  No memory writes."""
import json
from toads.emulator import BizHawk, LOGS_DIR

ROOT, UP14_PORTAL = 11910, 372
bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
COLS = [0x3B5, 0x3C1, 0x3D0, 0x3DF, 0x3EE, 0x3FD, 0x40C, 0x41B, 0x42A, 0x439, 0x448, 0x457, 0x466, 0x475, 0x484, 0x493, 0x4A2,
        0x4B1, 0x4C0, 0x4CF, 0x4DE, 0x4ED, 0x4FC, 0x50B, 0x51A, 0x529, 0x538, 0x547, 0x556, 0x565, 0x574, 0x583]


def rd(e):
    m = e.ram_all()
    hd = None
    hq = None
    for q in range(1, 15):
        if m[0x3C1 + q] == 0x4C:
            hd = (m[0x3FD + q] | m[0x3EE + q] << 8, m[0x439 + q] | m[0x42A + q] << 8)
            hq = q
    return dict(x=m[0x3FD] | m[0x3EE] << 8, H=m[0x439] | m[0x42A] << 8, z=m[0x475], an=m[0x3B5], hp=m[0x51A], lives=m[0x11],
                spd=m[0x565], face=m[0x4A2] & 0x40, lift=m[0x484], rtn=m[0x23] | m[0x24] << 8, head=hd, hq=hq, m=m,
                v=(m[0x448], m[0x457], m[0x466], m[0x4C0], m[0x4CF]), lvl=m[0x0D] if False else None)


def open_room(log):
    lines = [l for l in open(LOGS_DIR / "up14.inputs.txt").read().splitlines() if not l.startswith("#")]
    e = BizHawk(log_name=log)
    e.load("cap14_f11000")
    for i in range(11000, ROOT):
        e.step(bt(lines[i]), 1)
    return e, lines


def rle(ins):
    out, p, n = [], None, 0
    for b in ins:
        if b != p:
            if p is not None:
                out.append((p, n))
            p, n = b, 0
        n += 1
    if p is not None:
        out.append((p, n))
    return out
