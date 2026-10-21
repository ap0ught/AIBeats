"""Can bug 1 (slot 4) be made to let go quickly?  Get grabbed on the ledge (L9c 7819 + Right x22), then steer: Left / Left+A / Left+Down ...
for 140 frames.  Print x, H, z, anim, hp and whether slot 4 still holds the bug, every 6 frames and at every anim change."""
from l9heli_fix_lib import *
e = BizHawk(log_name="l9heli_fix_t17.log"); e.load("L9heli_7819")
for i in range(22): e.step(("Right",), 1)
m = e.ram(0, 0x800); print("grabbed:", tstr(m), "|", ostr(m), flush=True); root = e.msave()
for name, pat in [("Left", ["Left"]), ("Left+A", ["Left+A"]), ("Left, A mash", ["Left+A", "Left"]), ("Left+B", ["Left+B", "Left"]), ("Left+Down", ["Left+Down"]), ("Left+Up", ["Left+Up"])]:
    e.mload(root); out = []; pan = None; rel = None
    for i in range(170):
        e.step(bt(pat[i % len(pat)]), 1); m = e.ram(0, 0x800); s = toad(m)
        bug = m[0x3C1 + 4] == 0x74
        if rel is None and s["an"] not in CARRIED: rel = (i + 1, s["x"], s["H"], s["an"], s["hp"])
        if i % 10 == 9 or s["an"] != pan and s["an"] not in CARRIED:
            out.append((i + 1, s["x"], s["H"], s["z"], s["an"], s["hp"], "bug" if bug else "nobug"))
        pan = s["an"]
        if s["hp"] < 47: break
    print(name, "released:", rel, out[:26], flush=True)
e.close()
