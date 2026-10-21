"""Hop scan: after the trunk's floor landing (trunk frame 134, L9c 7953, x 837, $466 220) run Left a frames, jump Left+A x k, hold Left to the
landing.  Which (a, k) land with $466 == 118 (the old route's value at its jump, T')?  Also where/when, and the mine at that time."""
import json, sys
from l9heli_fix_lib import *
import l9heli_fix_tail as T
e = BizHawk(log_name="l9heli_fix_hop.log", fields=T.FLD); e.load("L9heli_7819")
for b in T.TRUNK: s = e.step(bt(b), 1)
print("landing", s.x | s.xh << 8, s.sub, "spd", s.spd, "$466", s.sh, flush=True)
root = e.msave(); hist = {}; good = []
for a in range(0, 30):
    for k in range(1, 33):
        e.mload(root); seq = ["Left"] * a + ["Left+A"] * k; land = None; top = 0
        for i in range(a + 80):
            b = seq[i] if i < len(seq) else "Left"
            s = e.step(bt(b), 1)
            if s.hp < 47: land = ("dead", i + 1, s.x | s.xh << 8); break
            H = s.h | s.hh << 8; top = max(top, H - 6182)
            if i >= a + 2 and s.z == 0 and H == 6182: land = (i + 1, s.x | s.xh << 8, s.sub, s.spd, s.sh, top); break
        if land and land[0] != "dead":
            hist[land[4]] = hist.get(land[4], 0) + 1
            if land[4] == 118: good.append((a, k, land)); print("a", a, "k", k, "-> lands at trunk frame", 134 + land[0], "x", land[1], land[2], "spd", land[3], "$466", land[4], "apex +", land[5], "mine", T.mine(e), flush=True)
        elif a % 6 == 0 and k in (1, 4, 12): print("a", a, "k", k, land, flush=True)
print("landing $466 histogram:", sorted(hist.items()), flush=True)
json.dump(good, open(LOGS_DIR / "fix" / "heli_hop.json", "w"))
e.close()
