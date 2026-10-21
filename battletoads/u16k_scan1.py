"""Track K: the record's line found = SPRINT jump at the snake (Right, -, Right+A on the same frame keeps run speed 192 through
the grab), climb by holding Right+A, the toad crosses the rising head at 3 px/f and flies to the portal ledge.
Scan 1: tap frame rj x 'start holding Right at frame tR' (A only before = stay on the left side) -> portal frame.
    python u16k_scan1.py [tag]  -> logs/fix/u16k_scan1<tag>.txt, best logs/fix/u16k_scan1<tag>_best.json"""
import itertools, json, sys
from u16k_lib import *

tag = sys.argv[1] if len(sys.argv) > 1 else ""
e, lines = open_room(f"u16k_scan1{tag}.log")
room = e.msave()
lives0 = rd(e)["lives"]
out, best = [], None
RJ = range(78, 126)
for rj in RJ:
    for tR in (0, 150, 156, 162, 168, 174, 180, 186):
        if tR and tR < rj + 20:
            continue
        e.mload(room)
        ins, grab, over, res, land = [], None, None, None, None
        for r in range(330):
            if r < rj:
                b = ()
            elif r == rj:
                b = ("Right",)
            elif r == rj + 1:
                b = ()
            elif grab and tR and r < tR and over is None:
                b = ("A",)
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
        line = f"rj {rj} tR {tR}: grab {grab} over {over} land {land} -> {res}"
        out.append(line)
        print(line, flush=True)
        if res and res[0] == "PORTAL" and (best is None or res[1] < best[0]):
            best = (res[1], rj, tR, list(ins))
            json.dump({"from_frame": ROOT, "inputs": best[3], "portal_r": best[0], "up14_portal_r": UP14_PORTAL, "rj": rj, "tR": tR},
                      open(LOGS_DIR / "fix" / f"u16k_scan1{tag}_best.json", "w"))
    open(LOGS_DIR / "fix" / f"u16k_scan1{tag}.txt", "w").write("\n".join(out) + "\n")
print("BEST", best[:3] if best else None, "up14", UP14_PORTAL)
e.close()
