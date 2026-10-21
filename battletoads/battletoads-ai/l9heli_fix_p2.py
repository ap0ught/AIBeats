"""Probe 2: can the toad RUN under the bugs (0x74 at x 824/840) without being grabbed, like the 1-player TAS does (59328-59340)?
From L9c 7818 (standing on the step at (756,134)): idle d, then hold Right 70 frames. Report grab frame/position or the fall."""
from l9heli_fix_lib import *
ins = up14_inputs()
e = BizHawk(log_name="l9heli_fix_p2.log")
e.load("L9heli_7800")
for f in range(OFF + 7800, OFF + 7818): e.step(bt(ins[f]), 1)
m = e.ram(0, 0x800); print("7818", tstr(m), "|", ostr(m), flush=True)
base = e.msave()
for d in range(0, 24):
    e.mload(base); e.step((), d)
    grab = None; out = []; t = None
    for i in range(80):
        e.step(("Right",), 1); m = e.ram(0, 0x800); s = toad(m)
        if grab is None and s["an"] in CARRIED: grab = (i + 1, s["x"], s["H"], s["t"]); break
        if i % 4 == 3: out.append((s["x"], s["H"], s["z"], s["spd"]))
    print("d", d, "grab", grab, out[:20], flush=True)
e.close()
