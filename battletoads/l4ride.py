"""Level 4 damage boost, the record's way: hop onto floating platform 1 from the pit's edge (bookmark L4r_edge2 =
after hopping the shaft's ice ball), ride it STANDING so the hanging spike at x 288 hits the toad, and fall through
the spike pit during the hit's invulnerability. Scans the hop and what is held afterwards.

    python l4ride.py trace <hopx> <hold>     # frame-by-frame after the hop, no input
    python l4ride.py scan
"""
import itertools
import json
import sys

from toads.emulator import BizHawk
from l4eject import tx, h16
from l4plats import plats


class Ride:
    def __init__(self, e, root):
        self.e, self.root = e, root
        m = e.ram(0, 0x800)

    def hop(self, hopx, hold):
        e = self.e
        e.mload(self.root)
        self.seq = []
        last = None
        ok = False
        for _ in range(420):
            m = e.ram(0, 0x800)
            p = plats(m)
            if not p:
                self.st("")
                continue
            if last is not None and p[0][0] < last and p[0][0] <= hopx:
                ok = True
                break
            last = p[0][0]
            self.st("Right" if tx(m) < 174 else "Left" if tx(m) > 178 else "")
        if not ok:
            return False
        for _ in range(hold):
            self.st("Right+A")
        for _ in range(4):
            self.st("Right")
        for _ in range(60):
            m = self.st("")
            if m[0x4B1] & 16:
                return True
        return False

    def st(self, b):
        self.e.step(tuple(v for v in b.split("+") if v), 1)
        self.seq.append(b)
        return self.e.ram(0, 0x800)


def main():
    e = BizHawk(log_name="l4fall.log")
    e.load("L4r_edge2")
    root = e.msave()
    m = e.ram(0, 0x800)
    lives0, hp0 = m[0x11], m[0x51A]
    r = Ride(e, root)
    if sys.argv[1] == "trace":
        ok = r.hop(int(sys.argv[2]), int(sys.argv[3]))
        m = e.ram(0, 0x800)
        print("hop", ok, len(r.seq), "toad", tx(m), hex(h16(m)), "hp", m[0x51A])
        for k in range(300):
            m = r.st(sys.argv[4] if len(sys.argv) > 4 and m[0x51A] < hp0 else "")
            if m[0x51A] != hp0 or k % 10 == 0:
                print(len(r.seq), "x", tx(m), "h", hex(h16(m)), "z", m[0x475], "anim", m[0x3B5], "st", m[0x4B1], "hp", m[0x51A], "lives", m[0x11],
                      "cam", m[0x87] | m[0x88] << 8, m[0x89] | m[0x8A] << 8, "plats", plats(m)[:2], flush=True)
            if m[0x11] < lives0 or m[0x51A] == 0:
                break
    else:
        hops = []
        for hopx, hold in itertools.product(range(196, 240, 4), (6, 8, 10, 12)):
            if r.hop(hopx, hold):
                hops.append((len(r.seq), hopx, hold))
                print("hop ok", hopx, hold, "at", len(r.seq), flush=True)
        hops.sort()
        seen = set()
        best = None
        for n0, hopx, hold in hops[:6]:
            for pre, b1, n1, b2 in itertools.product(("", "Right", "Left"), ("", "Left", "Right", "Down", "Right+A", "Left+A", "A"), (4, 10, 20, 40), ("", "Left", "Right")):
                r.hop(hopx, hold)
                hit = None
                out = ("none",)
                k1 = 0
                xs = []
                for k in range(400):
                    m = e.ram(0, 0x800)
                    if hit is None and m[0x51A] < hp0:
                        hit = k
                    if hit is None:
                        b = pre
                    elif k1 < n1:
                        b = b1
                        k1 += 1
                    else:
                        b = b2
                    m = r.st(b)
                    if hit is not None and h16(m) < 0x1900 and len(xs) < 8:
                        xs.append(tx(m))
                    if m[0x11] < lives0 or m[0x51A] == 0:
                        out = ("dead", len(r.seq), tx(m), hex(h16(m)))
                        break
                    if hit is not None and m[0x475] == 0 and h16(m) < 0x18f0:
                        out = ("LAND", len(r.seq), tx(m), hex(h16(m)), "cam", m[0x87] | m[0x88] << 8, m[0x89] | m[0x8A] << 8, "hp", m[0x51A])
                        break
                key = (out[0], out[2:4], tuple(xs))
                if key not in seen:
                    seen.add(key)
                    print((hopx, hold, pre, b1, n1, b2), "hit", hit, xs, out, flush=True)
                if out[0] == "LAND" and out[3] == "0x185e" and 330 < out[2] < 520 and (best is None or out[1] < best[0]):
                    best = (out[1], list(r.seq))
                    json.dump(best[1], open("knowledge/l4_ride_boost.json", "w"))
                    e.save("L4r_mid")
                    print("  SAVED L4r_mid", out, flush=True)
    e.close()


if __name__ == "__main__":
    main()
