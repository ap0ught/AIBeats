"""Track K2 (2026-10-10): shared helpers for the Karnath room-1 re-timing (u17k_*.py).  No memory writes anywhere."""
import json
from toads.emulator import BizHawk, LOGS_DIR

bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
FIX = LOGS_DIR / "fix"


def seg(name):
    return json.load(open(LOGS_DIR / f"pbeam_{name}.json"))["inputs"]


def info(m):
    """toad + snake heads from a 2 KB RAM image"""
    heads = [(q, m[0x3FD + q] | m[0x3EE + q] << 8, m[0x439 + q] | m[0x42A + q] << 8) for q in range(1, 15) if m[0x3C1 + q] == 0x4C]
    vy = (m[0x4C0] if m[0x4C0] < 128 else m[0x4C0] - 256) + m[0x4CF] / 256
    return dict(x=m[0x3FD] | m[0x3EE] << 8, H=m[0x439] | m[0x42A] << 8, z=m[0x475], an=m[0x3B5], hp=m[0x51A], lives=m[0x11],
                spd=m[0x565], face=m[0x4A2] & 0x40, vy=vy, heads=heads, lvl=m[0x10],
                score="".join(str(d) for d in m[0x5F4:0x5FA]))


def rle(ins):
    out, p, n, s = [], None, 0, 0
    for i, b in enumerate(ins):
        if b != p:
            if p is not None:
                out.append((s, p, n))
            p, n, s = b, 0, i
        n += 1
    if p is not None:
        out.append((s, p, n))
    return out


def rle_str(ins, base=0):
    return " ".join(f"{s + base}:{b or '-'}x{n}" for s, b, n in rle(ins))


def parse(spec):
    """'38:;89:Right;...' -> list of inputs ('-' or '' = nothing)"""
    ins = []
    for part in spec.split(";"):
        if not part:
            continue
        n, b = part.split(":")
        ins += [("" if b == "-" else b)] * int(n)
    return ins


def banned(ins):
    return [i for i, b in enumerate(ins) if "Start" in b or ("Left" in b and "Right" in b) or ("Up" in b and "Down" in b)]
