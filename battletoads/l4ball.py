"""Level 4 after the spike-pit damage boost, the ice ball (2026-10-02). Bookmark L4r_adv = the toad on the bowl's
right side (x ~690) at the frame the object loader caught up: the checkpoint-6 barrier (0x3c at 392), the ice ball
(0x38, spawned at 480 and rolling right through the bowl) and the spiky ball (0x40, coming down from 799) exist.

Phase "lift": run back left, meet the ice ball as it rolls up the bowl's right side, punch it (stops AND lifts it).
    python l4ball.py lift      -> knowledge/l4_ball_lift.json (inputs from L4r_adv), bookmark L4r_carry
Phase "throw": from L4r_top (the toad carrying the ball on the pillar top, see l4s with L4S_ACTS=climb) scan the
    throw (facing, delay) for the fastest barrier kill.
    python l4ball.py throw     -> knowledge/l4_ball_throw.json (inputs from L4r_top), bookmark L4r_bardead
"""
import itertools
import json
import sys

from toads.emulator import BizHawk
from l4 import find, toad

CARRY = (16, 17, 18)


def dh(a, b):
    return ((a - b + 128) % 256) - 128


def lift(e):
    e.load("L4r_adv")
    root = e.msave()
    m = e.ram_all()
    lives0, hp0 = m[0x11], m[0x51A]
    best = None
    for xw, style, reach in itertools.product(range(590, 680, 10), ("dash", "walk"), (12, 16, 20, 24)):
        e.mload(root)
        seq = []

        def st(b, n=1):
            for _ in range(n):
                e.step(tuple(v for v in b.split("+") if v), 1)
                seq.append(b)
            return e.ram_all()

        k = 0
        punched = None
        ok = False
        for _ in range(260):
            r = e.ram_all()
            t, b = toad(r), find(r, 0x38)
            if t["hp"] < hp0 or t["lives"] < lives0:
                break
            if b and t["z"] == 0 and 0 < abs(b["x"] - t["x"]) <= reach and abs(dh(b["h"], t["h"])) <= 24:
                st(("Right" if b["x"] > t["x"] else "Left") + "+B", 2)
                punched = len(seq)
                for _ in range(60):
                    r = st("")
                    t, b = toad(r), find(r, 0x38)
                    if t["anim"] in CARRY and b and b["x"] == t["x"]:
                        ok = True
                        break
                break
            if t["x"] > xw:
                if style == "dash" and k < 2:
                    st(("Left", "")[k])
                    k += 1
                else:
                    st("Left")
            else:
                st("")
        r = e.ram_all()
        t = toad(r)
        if ok and t["hp"] == hp0:
            print("lifted:", (xw, style, reach), "punch at", punched, "carrying at", len(seq), "toad", t["x"], t["h"], "spiky", (find(r, 0x40) or {}).get("x"), flush=True)
            if best is None or len(seq) < len(best):
                best = list(seq)
                json.dump(best, open("knowledge/l4_ball_lift.json", "w"))
                e.save("L4r_carry")
    print("best", best and len(best))


def throw(e):
    e.load("L4r_top")
    root = e.msave()
    m = e.ram_all()
    lives0, hp0 = m[0x11], m[0x51A]
    best = None
    for face, nturn, wait in itertools.product(("Right", "Left", ""), (1, 3, 5, 8), (0, 2, 4, 8, 12)):
        e.mload(root)
        seq = []

        def st(b, n=1):
            for _ in range(n):
                e.step(tuple(v for v in b.split("+") if v), 1)
                seq.append(b)
            return e.ram_all()

        st("", wait)
        if face:
            st(face, nturn)
            st("")
        st("B", 2)
        dead = None
        for k in range(420):
            r = st("")
            t, w = toad(r), find(r, 0x3c)
            if t["hp"] < hp0 or t["lives"] < lives0:
                break
            if w is None or w["hp"] == 0:
                dead = len(seq)
                break
        r = e.ram_all()
        w = find(r, 0x3c)
        print((face, nturn, wait), "barrier dead at", dead, "hp left", w and w["hp"], "toad", toad(r)["x"], toad(r)["h"], "hp", toad(r)["hp"], flush=True)
        if dead and (best is None or dead < len(best)):
            best = list(seq)
            json.dump(best, open("knowledge/l4_ball_throw.json", "w"))
            e.save("L4r_bardead")
    print("best", best and len(best))


if __name__ == "__main__":
    e = BizHawk(log_name="l4ball.log")
    {"lift": lift, "throw": throw}[sys.argv[1]](e)
    e.close()
