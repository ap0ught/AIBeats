"""Karnath's Lair room 2 (the warp to Level 8), the record's way: jump onto the snake's HEAD while it is still low
(a toad on the floor is not lifted - the head passes through it; a toad that lands on the head rides it), ride
it up and jump off toward the portal (432,104) early, instead of climbing to the top run (old l6.room2, ~400 f).

Phase 1: (wait x, jump frame, A hold) that puts the toad on the rising head. Phase 2: (height J, A hold, dash)
of the jump off it. From bookmark L6r_room2 (replay-exact room-2 entry). Keeps the fastest warp.

    python l6room2.py  -> knowledge/l6_room2_fast.json (inputs from L6r_room2 until the warp engages)
"""
import itertools
import json

from toads.emulator import BizHawk
from l6 import Unwrap, toad, head


class Run:
    def __init__(self, e):
        self.e = e
        e.load("L6r_room2")
        self.tu, self.hu = Unwrap(), Unwrap()
        self.ins = []
        self.lives0 = e.byte(0x11)

    def st(self, b):
        self.e.step(tuple(v for v in b.split("+") if v), 1)
        self.ins.append(b)

    def rd(self):
        r = self.e.ram_all()
        t = toad(r)
        h = head(r)
        t["H"] = self.tu(t["h"], 62 if self.tu.prev is None else None)
        if h:
            h["H"] = self.hu(h["h"], 32 if self.hu.prev is None else None)
        return t, h, r


def mount(e, x0, fj, hold, side):
    """wait at x0, at frame fj jump (toward the column) with A held `hold`; True if the toad then rides the head"""
    q = Run(e)
    for k in range(fj):
        t, h, r = q.rd()
        q.st("Right" if t["x"] < x0 - 1 else "Left" if t["x"] > x0 + 1 else "")
    for _ in range(hold):
        q.st(side + "+A")
    prev = None
    rising = 0
    for _ in range(70):
        t, h, r = q.rd()
        if t["lives"] < q.lives0 or t["hp"] < 47:
            return None
        if t["z"] == 0 and h and t["H"] > 60 and prev is not None and t["H"] > prev:
            rising += 1
            if rising >= 8:
                return q
        else:
            rising = 0 if t["z"] else rising
        prev = t["H"]
        q.st(side if abs(t["x"] - 112) > 2 else "")
    return None


def main():
    e = BizHawk(log_name="l6room2.log")
    mounts = []
    for x0, fj, hold in itertools.product((92, 98, 104, 124, 130), range(66, 120, 4), (4, 8, 12, 16)):
        side = "Right" if x0 < 112 else "Left"
        q = mount(e, x0, fj, hold, side)
        if q:
            t, h, r = q.rd()
            mounts.append((len(q.ins), x0, fj, hold, side, t["H"]))
            print("on the head at", len(q.ins), "x0", x0, "jump frame", fj, "hold", hold, "H", t["H"], flush=True)
    mounts.sort()
    best = None
    for n0, x0, fj, hold, side, H0 in mounts[:3]:
        for J, h2, dash in itertools.product(range(int(H0) + 4, 340, 12), (4, 10, 16, 24), (0, 1)):
            q = mount(e, x0, fj, hold, side)
            if not q:
                continue
            ok = False
            for _ in range(300):
                t, h, r = q.rd()
                if t["H"] >= J:
                    ok = True
                    break
                if t["lives"] < q.lives0:
                    break
                q.st("")
            if not ok:
                continue
            if dash:
                q.st("Right"); q.st("")
            for _ in range(h2):
                q.st("Right+A")
            n = None
            for _ in range(260):
                t, h, r = q.rd()
                if (r[0x23], r[0x24]) == (0x0D, 0xE5):
                    n = len(q.ins)
                    break
                if t["lives"] < q.lives0 or t["hp"] == 0:
                    break
                q.st("Right")
            if n and (best is None or n < best[0]):
                best = (n, list(q.ins))
                json.dump(best[1], open("knowledge/l6_room2_fast.json", "w"))
                print("warp at", n, "mount", (x0, fj, hold), "J", J, "hold", h2, "dash", dash, flush=True)
    print("best", best[0] if best else None)
    e.close()


if __name__ == "__main__":
    main()
