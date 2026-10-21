"""Karnath's Lair room 2, the record's way, second try (2026-10-02): MASH the climb - Right+A / Left+A alternating
every frame from the moment the snake's body is there (frame ~84 after L6r_room2). The toad then climbs at
~2.9 px/frame, overtakes the head (2 px/frame) and ends up on its right side; at frame fj hold Right+A (n frames)
then Right: over the spike block onto the portal's ledge.

    python l6room2c.py   -> knowledge/l6_room2_fast3.json (inputs from L6r_room2 until the warp engages)
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
    pre = old[:79]
    for b in pre:
        e.step(tuple(v for v in b.split("+") if v), 1)
    root = e.msave()
    best = None
    n_ok = 0
    for fc, pat, fj, n in itertools.product(range(80, 96, 2), (("Right+A", "Left+A"), ("Left+A", "Right+A"), ("Right+A", "Right+A", "Left+A"), ("Right+A", "Left+A", "Left+A")),
                                           range(112, 190, 3), (4, 12, 20, 32)):
        e.mload(root)
        seq = list(pre)

        def st(b):
            e.step(tuple(v for v in b.split("+") if v), 1)
            seq.append(b)
            return e.ram_all()

        while len(seq) < fc:
            st("")
        k = 0
        while len(seq) < fj:
            st(pat[k % len(pat)])
            k += 1
        for _ in range(n):
            r = st("Right+A")
        got = None
        for _ in range(170):
            r = st("Right")
            t = toad(r)
            if (r[0x23], r[0x24]) == (0x0D, 0xE5):
                got = len(seq)
                break
            if t["lives"] < lives0 or t["hp"] == 0:
                break
        if got:
            n_ok += 1
            if best is None or got < len(best):
                best = list(seq)
                json.dump(best, open("knowledge/l6_room2_fast3.json", "w"))
                print("warp at", got, "climb from", fc, pat, "jump at", fj, "hold", n, flush=True)
    print("best", best and len(best), "of", n_ok, "warps (old 370)")
    e.close()


if __name__ == "__main__":
    main()
