"""Track K: can the EARLIER launch slot (over the head at r+152..156, launch height 7637..7641, 12-16 frames sooner) work
by going UNDER the first star?  Holding Right+A it flies into the star at (233..236, 7646).  Here: after the crossing,
release A from frame fa on (Right stays held), optionally press A again later.  Outcome per run.
    python u16k_under.py -> logs/fix/u16k_under.txt"""
import json
from u16k_lib import *

e, lines = open_room("u16k_under.log")
room = e.msave()
lives0 = rd(e)["lives"]
out, good = [], []
for rj in (88, 90, 92, 83, 86):
    e.mload(room)
    base_ins = [""] * rj + ["Right", ""] + ["Right+A"] * 400
    over = None
    for r, b in enumerate(base_ins[:200]):
        e.step(bt(b), 1)
        t = rd(e)
        if t["x"] >= 126 and r > rj + 5:
            over = r + 1
            break
    base = e.msave()
    for fa in range(0, 44, 2):
        for back in (0, 6, 14):
            e.mload(base)
            res, land, tr = None, None, []
            for j in range(160):
                b = "Right+A" if (j < fa or (back and j >= fa + back)) else "Right"
                e.step(bt(b), 1)
                t = rd(e)
                if j in (fa + 1, fa + 4, 32, 42, 55):
                    tr.append(f"{j}:{t['x']},{t['H']},s{t['spd']}")
                if t["hp"] < 47 or t["lives"] < lives0:
                    res = ("HURT", over + j + 1, t["x"], t["H"])
                    break
                if land is None and t["z"] == 0:
                    land = (over + j + 1, t["x"], t["H"], t["spd"])
                if t["rtn"] == 0xE50D:
                    res = ("PORTAL", over + j + 1, t["x"], t["H"])
                    break
            line = f"rj {rj} over {over} A released at +{fa} back +{back}: land {land} -> {res} | {' '.join(tr)}"
            out.append(line)
            if res and res[0] == "PORTAL":
                good.append(line)
                print(line, flush=True)
    e.mfree(base)
    open(LOGS_DIR / "fix" / "u16k_under.txt", "w").write("\n".join(out) + "\n")
print(len(out), "runs;", len(good), "reach the portal")
e.close()
