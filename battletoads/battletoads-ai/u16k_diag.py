"""Track K: per-frame dump of the toad's object columns while replaying an input list from the room root (r+0 = up14 11910).
    python u16k_diag.py <inputs.json | up14> [n=230] [tag]"""
import json, sys
from u16k_lib import *

src = sys.argv[1]
n = int(sys.argv[2]) if len(sys.argv) > 2 else 230
tag = sys.argv[3] if len(sys.argv) > 3 else "a"
e, lines = open_room(f"u16k_diag_{tag}.log")
ins = lines[ROOT:ROOT + n] if src == "up14" else json.load(open(src))["inputs"][:n]
out = ["r inp | x H rel z an spd | cols " + " ".join(f"{c:03x}" for c in COLS) + " | head"]
for r, b in enumerate(ins):
    e.step(bt(b), 1)
    t = rd(e)
    m = t["m"]
    rel = (t["H"] - t["head"][1]) if t["head"] else None
    out.append(f"{r + 1:3d} {b or '-':8s} | {t['x']:3d} {t['H']} {rel} z{t['z']} an{t['an']} spd{t['spd']} hp{t['hp']} | " + " ".join(f"{m[c]:3d}" for c in COLS) + f" | {t['head']} q{t['hq']}"
               + (" " + " ".join(f"{m[c + t['hq']]:3d}" for c in COLS[1:]) if t["hq"] else ""))
open(LOGS_DIR / "fix" / f"u16k_diag_{tag}.txt", "w").write("\n".join(out) + "\n")
print("\n".join(out[:3]))
e.close()
