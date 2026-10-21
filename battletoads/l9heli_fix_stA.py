"""Stage A variants and the vertical sub-pixel of the long fall ($466 is constant at terminal velocity): mutate the AB0 path's jump
(start s, A frames n, directional hiccups) and report for the survivors: frames to H <= 6440, x there, $466, and whether the b4 fall
inputs still reach the floor (landing frame, x, $466)."""
import json, sys
from l9heli_fix_lib import *
import l9heli_fix_tail as T
AB = T.AB["inputs"]; B4 = T.B4["inputs"]
print("AB0:", " ".join(x or "-" for x in AB))
e = BizHawk(log_name="l9heli_fix_stA.log", fields=T.FLD); e.load("L9heli_7819"); root = e.msave()
def run(seq):
    e.mload(root); top = None
    for i, b in enumerate(seq + ["Left"] * 0):
        s = e.step(bt(b), 1)
        if s.hp < 47 or s.an in CARRIED: return ("dead", i + 1)
        H = s.h | s.hh << 8
        if top is None and H <= 6440: top = (i + 1, s.x | s.xh << 8, s.sh, s.vyh, s.vyl)
    return top, (len(seq), s.x | s.xh << 8, s.sub, H, s.z, s.spd, s.sh)
base = run(AB + B4); print("base:", base, flush=True)
seen = {}
dirs = [x.replace("+A", "").replace("A", "") for x in AB]
for s0 in range(14, 24):
    for n in range(1, 10):
        for drop in (None, 6, 16, 31, 32):
            seq = []
            for i, d in enumerate(dirs):
                on = s0 <= i < s0 + n
                seq.append((d + "+A").strip("+") if on else d)
            if drop is not None: seq[drop] = "Right"
            r = run(seq + B4)
            if r[0] == "dead": continue
            key = (r[0][2] if r[0] else None, r[1][6], r[1][4], r[1][3])
            if key not in seen:
                seen[key] = (s0, n, drop); print(f"A window [{s0},{s0 + n}) drop {drop}: top {r[0]} end {r[1]}", flush=True)
print(len(seen), "distinct outcomes")
e.close()
