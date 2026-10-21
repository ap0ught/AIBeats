"""Carried by the propeller bug to the right: does the toad reach the water of the x-938 column and get released there?
From L9c 7819: Right x22 (grabbed at 822), then hold Right (or Right+A, Right with A mash) for 260 frames.  Print every 8 frames."""
from l9heli_fix_lib import *
e = BizHawk(log_name="l9heli_fix_t19.log"); e.load("L9heli_7819")
for i in range(22): e.step(("Right",), 1)
root = e.msave()
for name, pat in [("Right", ["Right"]), ("Right+A", ["Right+A"]), ("Right, Down", ["Right+Down"])]:
    e.mload(root); out = []; rel = None
    for i in range(300):
        e.step(bt(pat[i % len(pat)]), 1); m = e.ram(0, 0x800); s = toad(m)
        if rel is None and s["an"] not in CARRIED: rel = (i + 1, 7841 + i + 1, s["x"], s["H"], s["an"], s["hp"]); 
        if i % 10 == 9 or (rel and i < rel[0] + 3): out.append((i + 1, s["x"], s["H"], s["an"], s["hp"], s["camx"], s["camy"]))
        if s["hp"] < 47: break
        if rel and i > rel[0] + 60: break
    print(name, "released:", rel, out, flush=True)
e.close()
