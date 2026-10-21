"""Level 4 spike-pit damage boost: scan what the toad does after getting up (bookmark-free: L4r_edge + creep/hit/get up)
and log where the wall ejection (+64 px per frame once the height wraps into the next screen) drops it.

    python l4eject.py  -> prints one line per distinct outcome
"""
import itertools
import json

from toads.emulator import BizHawk


def tx(m):
    return m[0x3FD] | m[0x3EE] << 8


def h16(m):
    return m[0x42A] << 8 | m[0x439]


def prefix(e, target=189):
    """from L4r_edge: creep to `target`, take the ice ball's hit, wait until the toad is up again"""
    seq0 = []
    hit = None
    cool = 0
    for k in range(400):
        m = e.ram(0, 0x800)
        x = tx(m)
        if hit is None and m[0x51A] < 47:
            hit = k
        if hit is None:
            if cool > 0 or m[0x475] != 0 or m[0x565] != 0:
                b = ""
                cool = max(0, cool - 1)
            elif x < target:
                b = "Right"
                cool = 4
            else:
                b = ""
        else:
            b = ""
            if k > hit + 60 and m[0x475] == 0 and m[0x3B5] not in (48, 19, 20, 21):
                break
        e.step((b,) if b else (), 1)
        seq0.append(b)
    return seq0


def main():
    e = BizHawk(log_name="l4fall.log")
    e.load("L4r_edge")
    lives0 = e.byte(0x11)
    seq0 = prefix(e)
    m = e.ram(0, 0x800)
    print("up at", len(seq0), "toad", tx(m), hex(h16(m)), "hp", m[0x51A], flush=True)
    U = e.msave()
    json.dump(seq0, open("knowledge/l4_boost_up.json", "w"))
    res = {}
    for b1, n1, b2, n2, b3 in itertools.product(("Right", "Right+A"), (2, 4, 6, 10, 16, 24), ("", "Left", "Right"), (4, 10, 18), ("", "Left", "Right")):
        e.mload(U)
        xs = []
        out = ("none",)
        wrapk = None
        plan = [b1] * n1 + [b2] * n2 + [b3] * 240
        for k, b in enumerate(plan):
            e.step(tuple(v for v in b.split("+") if v), 1)
            m = e.ram(0, 0x800)
            if wrapk is None and h16(m) < 0x1900:
                wrapk = k
            if wrapk is not None and k < wrapk + 8:
                xs.append(tx(m))
            if m[0x51A] == 0 or m[0x11] < lives0:
                out = ("dead", k, tx(m), hex(h16(m)))
                break
            if wrapk is not None and k > wrapk + 8 and m[0x475] == 0:
                out = ("LAND", k, tx(m), hex(h16(m)), "cam", m[0x87] | m[0x88] << 8, m[0x89] | m[0x8A] << 8)
                break
        key = (tuple(xs), out[0], out[2:4])
        if key not in res:
            res[key] = (b1, n1, b2, n2, b3)
            print((b1, n1, b2, n2, b3), "wrap", wrapk, xs, out, flush=True)
    e.close()


if __name__ == "__main__":
    main()
