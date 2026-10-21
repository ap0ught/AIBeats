"""Track K scan 2: fine-tune the launch height.  Sprint jump (Right, -, Right+A...) at rj, hold Right+A, but nR frames of
Right WITHOUT A (slower climb, Right stays held so the run flag should survive) starting d frames after the grab.
Outcome = frame the portal engages ($23/$24 == $E50D).  up14: r+372.  scan1 best: r+278 (rj 93).
    python u16k_scan2.py [tag] -> logs/fix/u16k_scan2<tag>.txt, best logs/fix/u16k_scan2<tag>_best.json"""
import itertools, json, sys
from u16k_lib import *

tag = sys.argv[1] if len(sys.argv) > 1 else ""
e, lines = open_room(f"u16k_scan2{tag}.log")
room = e.msave()
lives0 = rd(e)["lives"]
out, best = [], None
for rj, d, nR in itertools.product(range(84, 98), (1, 20, 40), range(0, 16)):
    if nR == 0 and d != 1:
        continue
    e.mload(room)
    ins, grab, over, res, land = [], None, None, None, None
    for r in range(300):
        if r < rj:
            b = ()
        elif r == rj:
            b = ("Right",)
        elif r == rj + 1:
            b = ()
        elif grab and over is None and grab[0] + d <= r + 1 < grab[0] + d + nR:
            b = ("Right",)
        else:
            b = ("Right", "A")
        e.step(b, 1)
        ins.append("+".join(b))
        t = rd(e)
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
    line = f"rj {rj} d {d} nR {nR}: grab {grab} over {over} land {land} -> {res}"
    out.append(line)
    print(line, flush=True)
    if res and res[0] == "PORTAL" and (best is None or res[1] < best[0]):
        best = (res[1], rj, d, nR, list(ins))
        json.dump({"from_frame": ROOT, "inputs": best[4], "portal_r": best[0], "up14_portal_r": UP14_PORTAL, "rj": rj, "d": d, "nR": nR},
                  open(LOGS_DIR / "fix" / f"u16k_scan2{tag}_best.json", "w"))
    open(LOGS_DIR / "fix" / f"u16k_scan2{tag}.txt", "w").write("\n".join(out) + "\n")
print("BEST", best[:4] if best else None, "up14", UP14_PORTAL)
e.close()
