"""Track K: run a hand-written input script from the warp-room root and print a compact per-frame trace.
    python u16k_run.py "<n>:<buttons>;<n>:<buttons>;..." [from=0] [to=len] [tag]
e.g. "80:;1:Right;1:;40:Right+A;60:Left".  Trace: r:x/rel(H)/z/anim/spd/vy"""
import sys
from u16k_lib import *

spec = sys.argv[1]
ins = []
for part in spec.split(";"):
    n, b = part.split(":")
    ins += [b] * int(n)
f0 = int(sys.argv[2]) if len(sys.argv) > 2 else 0
f1 = int(sys.argv[3]) if len(sys.argv) > 3 else len(ins)
tag = sys.argv[4] if len(sys.argv) > 4 else "run"
e, lines = open_room(f"u16k_run_{tag}.log")
tr = []
for r, b in enumerate(ins):
    e.step(bt(b), 1)
    t = rd(e)
    if f0 <= r + 1 <= f1:
        m = t["m"]
        vy = (m[0x4C0] if m[0x4C0] < 128 else m[0x4C0] - 256) + m[0x4CF] / 256
        rel = (t["H"] - t["head"][1]) if t["head"] else None
        tr.append(f"{r + 1}{'[' + b + ']'}:{t['x']}/{rel}({t['H']})/z{t['z']}/a{t['an']}/s{t['spd']}/v{vy:.1f}" + ("" if t["hp"] == 47 else f"/HP{t['hp']}"))
    if t["hp"] < 47:
        break
print(" ".join(tr))
e.close()
