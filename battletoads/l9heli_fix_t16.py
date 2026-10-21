"""Hop 1 mechanics near the low-ceiling boundary: after the L0=67 water landing run Left g1 frames, jump A x4 (+Left), then idle.
Report takeoff x, apex, first anim-45 frame (bump), landing frame, $466, death."""
import json
from l9heli_fix_lib import *
import l9heli_fix_tail as T
ins = up14_inputs()
var = min([o for o in json.load(open(LOGS_DIR / "fix" / "heli_stA4.json")) if o["land"][4] == 67], key=lambda o: o["land"][0])
e = BizHawk(log_name="l9heli_fix_t16.log", fields=T.FLD); e.load("L9heli_7800")
for f in range(OFF + 7800, OFF + var["root"]): e.step(bt(ins[f]), 1)
for b in var["inputs"]: s = e.step(bt(b), 1)
S0 = e.msave()
for g1 in range(8, 34, 2):
    for air in ("", "Left", "Right"):
        e.mload(S0)
        for i in range(g1): s = e.step(("Left",), 1)
        x0 = s.x | s.xh << 8; top = 0; bump = None; res = None; tr = []
        for i in range(70):
            s = e.step(bt("Left+A") if i < 4 else bt(air), 1)
            H = (s.h | s.hh << 8) - 6182; top = max(top, H)
            if bump is None and s.an == 45: bump = (i + 1, s.x | s.xh << 8, H)
            if s.hp < 47: res = ("dead", i + 1, s.x | s.xh << 8, H, T.mine(e)); break
            if i > 2 and s.z == 0: res = ("land", i + 1, s.x | s.xh << 8, s.sh); break
        print(f"g1 {g1} takeoff x {x0} air {air!r:7s}: apex +{top} bump {bump} -> {res}", flush=True)
e.close()
