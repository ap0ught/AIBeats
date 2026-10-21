"""Track K scan 3: fine-tune the launch height by the START POSITION.  Walk Right for wR frames from r=30 (or Left for wL and
turn back), idle, then the sprint jump at rj (Right, -, Right+A held to the end).  Right+A must stay held from the jump
on: one frame without A or without Right on the snake drops the run speed (scan 2).
    python u16k_scan3.py [tag] -> logs/fix/u16k_scan3<tag>.txt, best logs/fix/u16k_scan3<tag>_best.json"""
import itertools, json, sys
from u16k_lib import *

tag = sys.argv[1] if len(sys.argv) > 1 else ""
e, lines = open_room(f"u16k_scan3{tag}.log")
room = e.msave()
lives0 = rd(e)["lives"]
out, best = [], None
WALKS = [("R", w) for w in (4, 8, 10, 12, 14, 16, 18, 20, 22, 24)] + [("L", w) for w in (4, 8, 12, 16)]
for (wd, w), rj in itertools.product(WALKS, range(84, 95)):
    e.mload(room)
    ins, grab, over, res, land, x_tap = [], None, None, None, None, None
    for r in range(300):
        if r < rj:
            if 30 <= r < 30 + w:
                b = ("Right",) if wd == "R" else ("Left",)
            elif wd == "L" and 30 + w + 2 <= r < 30 + w + 4:
                b = ("Right",)          # face right again
            else:
                b = ()
        elif r == rj:
            b = ("Right",)
        elif r == rj + 1:
            b = ()
        else:
            b = ("Right", "A")
        e.step(b, 1)
        ins.append("+".join(b))
        t = rd(e)
        if r == rj - 1:
            x_tap = (t["x"], t["spd"], t["face"])
        if t["hp"] < 47 or t["lives"] < lives0:
            res = ("HURT", r + 1, t["x"], t["H"])
            break
        if grab is None and t["an"] in (88, 89):
            grab = (r + 1, t["H"], (t["H"] - t["head"][1]) if t["head"] else None)
        if over is None and grab and t["x"] >= 126:
            over = (r + 1, t["x"], t["H"], t["spd"])
        if land is None and over and t["z"] == 0:
            land = (r + 1, t["x"], t["H"], t["spd"])
        if t["rtn"] == 0xE50D:
            res = ("PORTAL", r + 1, t["x"], t["H"])
            break
    line = f"walk {wd}{w} rj {rj}: at tap {x_tap} grab {grab} over {over} land {land} -> {res}"
    out.append(line)
    print(line, flush=True)
    if res and res[0] == "PORTAL" and (best is None or res[1] < best[0]):
        best = (res[1], wd, w, rj, list(ins))
        json.dump({"from_frame": ROOT, "inputs": best[4], "portal_r": best[0], "up14_portal_r": UP14_PORTAL, "walk": wd + str(w), "rj": rj},
                  open(LOGS_DIR / "fix" / f"u16k_scan3{tag}_best.json", "w"))
    open(LOGS_DIR / "fix" / f"u16k_scan3{tag}.txt", "w").write("\n".join(out) + "\n")
print("BEST", best[:4] if best else None, "up14", UP14_PORTAL)
e.close()
