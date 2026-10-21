"""Stage A variants, part 3: start the AB0 + b4 inputs EARLIER than L9c 7819 (the old route idles 7816-7819 on the step): roots 7816/7817/7818,
A-window n = 1..9.  Survivors: landing frame (as L9c index), x.sub, speed, landing $466."""
import json, sys
from l9heli_fix_lib import *
import l9heli_fix_tail as T
AB = T.AB["inputs"]; B4 = T.B4["inputs"]; ins = up14_inputs()
WANT = {87: 1, 159: 2, 205: 3, 60: 4, 180: 5, 59: 6, 219: 7, 152: 8}
e = BizHawk(log_name="l9heli_fix_stA3.log", fields=T.FLD)
dirs = [x.replace("+A", "").replace("A", "") for x in AB]
for r0 in (7816, 7817, 7818, 7819):
    e.load("L9heli_7800")
    for f in range(OFF + 7800, OFF + r0): s = e.step(bt(ins[f]), 1)
    root = e.msave(); print("root", r0, "x", s.x | s.xh << 8, s.sub, "spd", s.spd, "$466", s.sh, flush=True)
    for n in range(1, 10):
        seq = [((dd + "+A").strip("+") if 17 <= i < 17 + n else dd) for i, dd in enumerate(dirs)] + B4 + ["Left"] * 3
        e.mload(root); dead = None; land = None
        for i, b in enumerate(seq):
            s = e.step(bt(b), 1)
            if s.hp < 47 or s.an in CARRIED: dead = (i + 1, s.x | s.xh << 8, s.an); break
            if i > 100 and s.z == 0 and (s.h | s.hh << 8) == 6182: land = (r0 + i + 1, s.x | s.xh << 8, s.sub, s.spd, s.sh); break
        print(f"  root {r0} n {n}: dead {dead} land {land}", "<== k%d" % WANT[land[4]] if (land and land[4] in WANT) else "", flush=True)
e.close()
