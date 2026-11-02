"""Print the TAS line in a frame range: frame room wpos y anim rflags hp input; marks L+R / U+D frames.
    python work/r5/tasview.py <f0> <f1> [step]"""
import csv, sys
from pathlib import Path
P = Path(__file__).resolve().parent.parent.parent
f0, f1 = int(sys.argv[1]), int(sys.argv[2]); st = int(sys.argv[3]) if len(sys.argv) > 3 else 5
T = {int(r["frame"]): r for r in csv.DictReader(open(P / "logs/tas4751.trace.csv"))}
def wp(d):
    sc = int(d["scroll_scr"]); sc = sc - 256 if sc >= 128 else sc
    return sc * 256 + int(d["scroll"]) + int(d["x"])
def btn(m):
    return "".join(c for c, b in zip("UDLRsSBA", (8, 4, 2, 1, 32, 16, 64, 128)) if m & b) or "."
for f in range(f0, f1):
    R = T[f]; p = int(R["pad"]); bad = ((p & 3) == 3) or ((p & 12) == 12)
    if (f - f0) % st == 0 or bad:
        print(f, R["room"], wp(R), R["y"], "anim", R["anim"], "rf", R["rflags"], "hp", R["hp"], "coll", R["coll"], btn(p), "BAD" if bad else "")
