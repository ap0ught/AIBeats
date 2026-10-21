"""Replay a piece json {a, b, inputs} from L9c index a and print the toad + mine every k frames (and every air/ground transition)."""
import json, sys
from l9heli_fix_lib import *
import l9heli_fix_tail as T
p = json.load(open(sys.argv[1])); k = int(sys.argv[2]) if len(sys.argv) > 2 else 4; ins = up14_inputs()
e = BizHawk(log_name="l9heli_fix_showp.log", fields=T.FLD); e.load("L9heli_7800")
for f in range(OFF + 7800, OFF + p["a"]): e.step(bt(ins[f]), 1)
pz = 0
for i, b in enumerate(p["inputs"]):
    s = e.step(bt(b), 1); idx = p["a"] + i + 1
    if (i + 1) % k == 0 or s.z != pz or i == len(p["inputs"]) - 1:
        print(idx, repr(b).ljust(9), f"x {s.x | s.xh << 8}.{s.sub:3d} dH {(s.h | s.hh << 8) - 6182:4d} z {s.z} an {s.an:2d} spd {s.spd:3d} sh {s.sh:3d} f {s.f:3d} mine {T.mine(e)}", flush=True)
    pz = s.z
e.close()
