"""Vertical hop scan under the shaft (high ceiling): after the trunk landing (frame 134) wait G ground frames (Left), jump with A held k frames,
then a second A window [c, c+b) during the flight; no direction in the air.  Landing: duration D (frames after takeoff input), $466, apex.
    python l9heli_fix_hopv.py <G> <target $466>"""
import json, sys
from l9heli_fix_lib import *
import l9heli_fix_tail as T
G = int(sys.argv[1]) if len(sys.argv) > 1 else 2
TG = int(sys.argv[2]) if len(sys.argv) > 2 else 60
e = BizHawk(log_name="l9heli_fix_hopv.log", fields=T.FLD); e.load("L9heli_7819")
for b in T.TRUNK + ["Left"] * G: s = e.step(bt(b), 1)
print("takeoff state", s.x | s.xh << 8, s.sub, "spd", s.spd, "$466", s.sh, flush=True)
root = e.msave(); res = {}; good = []
for k in range(1, 25):
    for c in [0] + list(range(k + 1, 46, 2)):
        for b in ([0] if c == 0 else [1, 2, 3, 4, 6, 8, 12]):
            e.mload(root); land = None; top = 0
            for i in range(90):
                on = i < k or (c and c <= i < c + b)
                s = e.step(("A",) if on else (), 1)
                if s.hp < 47: land = ("dead", i + 1); break
                H = s.h | s.hh << 8; top = max(top, H - 6182)
                if i >= 2 and s.z == 0 and H == 6182: land = (i + 1, s.sh, top); break
            res[(k, c, b)] = land
            if land and land[0] != "dead" and land[1] == TG: good.append((k, c, b, land)); print("k", k, "c", c, "b", b, "-> (D, $466, apex)", land, flush=True)
vals = {}
for v in res.values():
    if v and v[0] != "dead": vals.setdefault(v[1], []).append(v[0])
print(len(res), "patterns,", len(vals), "distinct landing $466; durations:", sorted(set(d for v in vals.values() for d in v)), "dead:", sum(1 for v in res.values() if v and v[0] == "dead"), flush=True)
print("base (no 2nd window):", {k: res[(k, 0, 0)] for k in range(1, 25)}, flush=True)
json.dump([list(g) for g in good], open(LOGS_DIR / "fix" / f"heli_hopv_{TG}.json", "w"))
e.close()
