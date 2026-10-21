"""Probe 1: bookmarks on the up14 line around the helicopter (bug 0x74) and a first look at when the bug grabs.
Saves L9heli_7800/7852/8198/8402 (L9c indices; up14 frame = index + 17366)."""
import sys
from l9heli_fix_lib import *
ins = up14_inputs()
e = BizHawk(log_name="l9heli_fix_p1.log")
m = goto(e, OFF + 7800, ins); e.save("L9heli_7800"); print("7800", tstr(m), "|", ostr(m), flush=True)
R = cap()
for f in range(OFF + 7800, OFF + 8402):
    e.step(bt(ins[f]), 1)
    idx = f + 1 - OFF
    if idx in (7852, 8198, 8264, 8402):
        m = e.ram(0, 0x800); ref = bytes(R[f])
        print(idx, "diff vs cap14:", sum(1 for a in range(0x800) if m[a] != ref[a]), tstr(m), "|", ostr(m), flush=True)
        e.save(f"L9heli_{idx}")
# walking test from 7852: hold Right for 40 frames after k idle frames
e.load("L9heli_7852"); base = None
for k in (0, 1, 2, 3, 4, 6, 8, 12, 16, 20, 24, 28):
    e.load("L9heli_7852"); e.step((), k)
    grab = None; out = []
    for i in range(60):
        e.step(("Right",), 1); m = e.ram(0, 0x800); s = toad(m)
        if grab is None and s["an"] in CARRIED: grab = (i + 1, s["x"], s["H"])
        if i % 6 == 5: out.append((s["x"], s["H"] & 255, s["z"], s["an"]))
    print("idle", k, "then Right: grab", grab, out, flush=True)
e.close()
