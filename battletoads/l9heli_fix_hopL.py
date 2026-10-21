"""Low-ceiling hop table: from the b1 path at frame 248 (760.160, slow mode, $466 22, mine behind): Left+A x k then Left.  Landing duration and
$466 shift (landing - takeoff) for k = 1..30.  Also a few release/re-press patterns."""
import json
from l9heli_fix_lib import *
import l9heli_fix_tail as T
g = json.load(open(LOGS_DIR / "fix" / "heli_beam_b1.json"))[0]
e = BizHawk(log_name="l9heli_fix_hopL.log", fields=T.FLD); e.load(g["root"])
for b in g["inputs"][:248]: s = e.step(bt(b), 1)
root = e.msave(); sh0 = s.sh; tab = {}
for k in range(1, 31):
    e.mload(root)
    for i in range(80):
        s = e.step(bt("Left+A" if i < k else "Left"), 1)
        if i > 2 and s.z == 0: tab[k] = (i + 1, (s.sh - sh0) % 256); break
print("low zone: k -> (duration, delta):", tab, flush=True)
json.dump(tab, open(LOGS_DIR / "fix" / "heli_hopL.json", "w"))
e.close()
