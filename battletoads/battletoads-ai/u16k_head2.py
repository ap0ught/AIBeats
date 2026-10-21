"""Track K: stage 2 of the head jump.  From a 'standing on the head' line (u16k_beam_*_stand*.json): wait w frames, dash
jump (Right, -, Right+A), hold Right, A released after `a` frames -> touch / portal frame.  Then on the ledge Right stays
held (the run continues).
    python u16k_head2.py <stand json> [wmax=45] -> logs/fix/<stand json name>_jump.txt, best line <...>_jump_best.json"""
import json, sys
from pathlib import Path
from u16k_lib import *

src = Path(sys.argv[1])
wmax = int(sys.argv[2]) if len(sys.argv) > 2 else 45
pre = json.load(open(src))["inputs"]
e, lines = open_room(f"u16k_head2_{src.stem}.log")
lives0 = rd(e)["lives"]
for b in pre:
    e.step(bt(b), 1)
t = rd(e)
out = [f"{src.name}: standing at r+{len(pre)}: x {t['x']} rel {t['H'] - t['head'][1]} z {t['z']} anim {t['an']} facing {t['face']}"]
print(out[0], flush=True)
base = e.msave()
best = None
for w in range(0, wmax):
    for a in (99, 22, 14, 8):
        for tap in ("RxR", "R"):
            e.mload(base)
            seq = [""] * w + (["Right", ""] if tap == "RxR" else []) + ["Right+A"] * 230
            j0 = w + (2 if tap == "RxR" else 0)
            tail, res, land, touch, tr = [], None, None, None, []
            for j, b in enumerate(seq[:240]):
                if j >= j0 + a:
                    b = "Right"
                e.step(bt(b), 1)
                tail.append(b)
                t = rd(e)
                if j in (j0 + 2, j0 + 38, j0 + 48):
                    tr.append(f"{j - j0}:{t['x']},{t['H']},s{t['spd']}")
                if t["hp"] < 47 or t["lives"] < lives0:
                    res = ("HURT", len(pre) + j + 1, t["x"], t["H"])
                    break
                if land is None and j > j0 + 4 and t["z"] == 0:
                    land = (len(pre) + j + 1, t["x"], t["H"])
                if touch is None and land and t["spd"] == 0 and t["x"] >= 408:
                    touch = (len(pre) + j + 1, t["x"])
                if t["rtn"] == 0xE50D:
                    res = ("PORTAL", len(pre) + j + 1, t["x"])
                    break
            line = f"  wait {w} A {a} {tap}: jump at r+{len(pre) + j0 + 1} land {land} touch {touch} -> {res} | {' '.join(tr)}"
            out.append(line)
            if res and res[0] == "PORTAL" and touch and (best is None or touch[0] < best[0]):
                best = (touch[0], w, a, tap, pre + tail[:touch[0] - len(pre)])
                print(line[:250], flush=True)
                json.dump({"from_frame": ROOT, "inputs": best[4], "touch_r": best[0], "touch_x": touch[1], "wait": w, "a": a, "tap": tap},
                          open(LOGS_DIR / "fix" / f"{src.stem}_jump_best.json", "w"))
    open(LOGS_DIR / "fix" / f"{src.stem}_jump.txt", "w").write("\n".join(out) + "\n")
print(f"BEST touch r+{best[0]} (wait {best[1]}, A {best[2]}, {best[3]})" if best else "no portal")
e.close()
