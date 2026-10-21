"""Karnath's Lair room 2 (the warp to Level 8), the record's way (its run 164.9-168.7): climb the snake's body the
moment it comes out of the floor (alternating Left+A / Right+A at its left side), and at a height of ~170-200 jump
off to the RIGHT over the spike block onto the portal's ledge (x >= 340, h 94) - instead of climbing all the way
to the top run (old l6.room2 406 f, l6room2.py 370 f).

    python l6room2b.py   -> knowledge/l6_room2_fast.json (inputs from L6r_room2 until the warp engages)
"""
import itertools
import json

from toads.emulator import BizHawk
from l6 import Unwrap, toad, head


def main():
    e = BizHawk(log_name="l6room2.log")
    old = json.load(open("knowledge/l6_room2_fast.json"))
    e.load("L6r_room2")
    lives0 = e.byte(0x11)
    pre = old[:79]                                        # to x 104 beside the hole, one Right tap to FACE the column (the climb needs it)
    for b in pre:
        e.step(tuple(v for v in b.split("+") if v), 1)
    root = e.msave()
    best = None
    seen = 0
    for fc, J, var, n in itertools.product(range(80, 108, 3), range(140, 260, 8), ("RA", "dash", "LRA", "R"), (4, 12, 20, 32)):
        e.mload(root)
        tu = Unwrap()
        seq = list(pre)

        def st(b):
            e.step(tuple(v for v in b.split("+") if v), 1)
            seq.append(b)
            r = e.ram_all()
            t = toad(r)
            t["H"] = tu(t["h"], 30 if tu.prev is None else None)
            return r, t

        r, t = st("")
        while len(seq) < fc:
            r, t = st("")
        k = 0
        ok = True
        while t["H"] < J:
            r, t = st(("Left+A", "Right+A")[(k // 4) % 2])
            k += 1
            if k > 140 or t["lives"] < lives0 or t["hp"] < 47:
                ok = False
                break
        if not ok:
            continue
        if var == "RA":
            for _ in range(n):
                r, t = st("Right+A")
        elif var == "dash":
            st("Right")
            st("")
            for _ in range(n):
                r, t = st("Right+A")
        elif var == "LRA":
            for _ in range(4):
                st("Left+A")
            for _ in range(n):
                r, t = st("Right+A")
        got = None
        for _ in range(170):
            r, t = st("Right")
            if (r[0x23], r[0x24]) == (0x0D, 0xE5):
                got = len(seq)
                break
            if t["lives"] < lives0 or t["hp"] == 0:
                break
        seen += 1
        if got and (best is None or got < len(best)):
            best = list(seq)
            json.dump(best, open("knowledge/l6_room2_fast2.json", "w"))
            print("warp at", got, "climb from", fc, "jump at H", J, var, n, flush=True)
    print("best", best and len(best), "of", seen, "(old 370)")
    e.close()


if __name__ == "__main__":
    main()
