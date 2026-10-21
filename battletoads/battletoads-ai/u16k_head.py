"""Track K: STANDSTILL DASH JUMP FROM THE HEAD.  The rising head is standable in the warp room: a toad that falls free onto
its top lands (z 0, 14 px above the head's coordinate) and rides up (u16k_stand.py).  From there tap Right, let go,
Right+A = the long jump (4.7 px/f up, 3 px/f sideways), 44 px higher than the cling jump the record uses.
Stage 1: sprint jump at rj, Right+A to the crossing (x 128), then hold Left without A until the toad stands on the head.
Stage 2: from the standing state wait w frames, dash jump, hold Right+A (A released after `a` frames) -> portal frame.
    python u16k_head.py [rj=80] -> logs/fix/u16k_head_<rj>.txt, best line logs/fix/u16k_head_<rj>_best.json"""
import json, sys
from u16k_lib import *

rj = int(sys.argv[1]) if len(sys.argv) > 1 else 80
e, lines = open_room(f"u16k_head_{rj}.log")
lives0 = rd(e)["lives"]
out = []


def say(s):
    print(s[:260], flush=True)
    out.append(s)


ins, over, stand = [], None, None
for r in range(260):
    if r < rj:
        b = ""
    elif r == rj:
        b = "Right"
    elif r == rj + 1:
        b = ""
    elif over is None:
        b = "Right+A"
    else:
        b = "Left"
    e.step(bt(b), 1)
    ins.append(b)
    t = rd(e)
    if t["hp"] < 47 or (r > rj + 30 and not t["head"]):
        say(f"stage 1 failed at r+{r + 1}: {t['x']},{t['H']} hp {t['hp']}")
        break
    rel = (t["H"] - t["head"][1]) if t["head"] else -999
    if over is None and r > rj + 5 and t["x"] >= 126:
        over = r + 1
    if over and t["z"] == 0 and t["an"] not in (88, 89) and 10 <= rel <= 18:
        stand = (r + 1, t["x"], rel, t["an"], t["face"])
        break
say(f"rj {rj}: over the head at r+{over}; standing on the head at {stand}")
best = None
if stand:
    base = e.msave()
    for w in range(0, 40):
        for a in (99, 24, 16, 10):
            e.mload(base)
            seq = [""] * w + ["Right", ""] + ["Right+A"] * 200
            tail, res, land, touch, tr = [], None, None, None, []
            for j, b in enumerate(seq[:230]):
                if j >= w + 2 + a:
                    b = "Right"
                e.step(bt(b), 1)
                tail.append(b)
                t = rd(e)
                if j in (w + 3, w + 40, w + 50):
                    tr.append(f"{j}:{t['x']},{t['H']},s{t['spd']},z{t['z']}")
                if t["hp"] < 47 or t["lives"] < lives0:
                    res = ("HURT", stand[0] + j + 1, t["x"], t["H"])
                    break
                if land is None and j > w + 4 and t["z"] == 0:
                    land = (stand[0] + j + 1, t["x"], t["H"])
                if touch is None and land and t["spd"] == 0 and t["x"] >= 408:
                    touch = (stand[0] + j + 1, t["x"])
                if t["rtn"] == 0xE50D:
                    res = ("PORTAL", stand[0] + j + 1, t["x"])
                    break
            say(f"  wait {w} A {a}: jump at r+{stand[0] + w + 3} land {land} touch {touch} -> {res} | {' '.join(tr)}")
            if res and res[0] == "PORTAL" and (best is None or touch[0] < best[0]):
                best = (touch[0], w, a, ins + tail)
                json.dump({"from_frame": ROOT, "inputs": best[3], "touch_r": best[0], "wait": w, "a": a, "rj": rj},
                          open(LOGS_DIR / "fix" / f"u16k_head_{rj}_best.json", "w"))
    say(f"BEST touch r+{best[0]} (wait {best[1]}, A {best[2]})" if best else "no portal")
open(LOGS_DIR / "fix" / f"u16k_head_{rj}.txt", "w").write("\n".join(out) + "\n")
e.close()
