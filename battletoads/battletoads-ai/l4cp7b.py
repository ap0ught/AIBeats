"""Level 4, barrier 7 with a running start (2026-10-02). l4cp7.py's closed loop crouches at x 646 until the snowmen's
shots have broken the barrier, then starts from a standstill on ice. The record's runner is already running when
it breaks: here the closed loop is replayed until the barrier has one shot left, then the toad backs off to x0,
crouches until the LAST fast snowball has passed overhead and dashes right behind it (same 3 px/frame), so it
reaches the barrier's spot at speed just after the ball has broken it.

    python l4cp7b.py [root bookmark, default L4r_plats]  -> knowledge/l4_cp7_inputs.json, bookmark <prefix>_cp7
"""
import itertools
import json
import sys

from toads.emulator import BizHawk
from l4 import find, toad

ROOT = sys.argv[1] if len(sys.argv) > 1 else "L4r_plats"
OUT = ROOT.rsplit("_", 1)[0] + "_cp7"


def balls(r):
    return [(r[0x3FD + s] + 256 * r[0x3EE + s], r[0x439 + s], r[0x565 + s]) for s in range(2, 15) if r[0x3C1 + s] == 0x3a]


def main():
    e = BizHawk(log_name="l4cp7.log")
    old = json.load(open("knowledge/l4_cp7_inputs.json"))
    e.load(ROOT)
    lives0, hp0 = e.byte(0x11), e.byte(0x51A)
    cut = None
    for k, b in enumerate(old):                             # the old loop until one shot is left
        e.step(tuple(v for v in b.split("+") if v), 1)
        w = find(e.ram_all(), 0x3c)
        if w and 0 < w["hp"] <= 8:
            cut = k + 1
            break
    if cut is None:
        print("the old inputs never bring the barrier to its last shot from", ROOT)
        e.close()
        return
    root = e.msave()
    r = e.ram_all()
    print("one shot left at input", cut, "toad", toad(r)["x"], "balls", balls(r), flush=True)
    best = None
    for nl, go in itertools.product(range(0, 44, 2), range(cut + 14, cut + 50)):
        e.mload(root)
        seq = list(old[:cut])

        def st(b, n=1):
            for _ in range(n):
                e.step(tuple(v for v in b.split("+") if v), 1)
                seq.append(b)
            return e.ram_all()

        st("Left", nl)                                      # back off for a run-up...
        while len(seq) < go:
            st("Down")                                      # ...crouch while the last ball passes overhead...
        st("Right")                                         # ...and dash after it
        st("")
        dead = None
        ok = True
        for _ in range(90):
            r = st("Right")
            t = toad(r)
            w = find(r, 0x3c)
            if t["hp"] < hp0 or t["lives"] < lives0:
                ok = False
                break
            if dead is None and (w is None or w["hp"] == 0):
                dead = len(seq)
            if dead is not None and t["x"] >= 690:
                break
        if ok and dead is not None and t["x"] >= 690 and t["z"] == 0:
            if best is None or len(seq) < best[0]:
                best = (len(seq), list(seq), dead)
                print("left", nl, "go at", go, "barrier dead at", dead, "x 690 at", len(seq), "spd", t["spd"], flush=True)
    if best:
        e.load(ROOT)
        for b in best[1]:
            e.step(tuple(v for v in b.split("+") if v), 1)
        r = e.ram_all()
        print("best: x 690 at", best[0], "(barrier dead at", best[2], ") toad", toad(r))
        json.dump(best[1], open("knowledge/l4_cp7b_inputs.json", "w"))
        e.save(OUT + "b")
    e.close()


if __name__ == "__main__":
    main()
