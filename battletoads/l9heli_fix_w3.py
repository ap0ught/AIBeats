"""Is x = 915 (camera 772 + 143) a hard limit on the right side of the shaft?  From L9heli_AB0 hold Right for 160 frames (fall along the right
side to the pool floor and keep walking right); print x, H, anim, camera every 8 frames.  Then the same with a jump at the bottom."""
from l9heli_fix_lib import *
e = BizHawk(log_name="l9heli_fix_w3.log"); e.load("L9heli_AB0"); root = e.msave()
for name, seq in [("Right 200", ["Right"] * 200), ("Right 70, Right+A 8, Right", ["Right"] * 70 + ["Right+A"] * 8 + ["Right"] * 120)]:
    e.mload(root); out = []
    for i, b in enumerate(seq):
        e.step(bt(b), 1)
        if i % 10 == 9:
            m = e.ram(0, 0x800); s = toad(m); out.append((i + 1, s["x"], s["H"], s["z"], s["an"], s["hp"], s["camx"], s["camy"]))
            if s["hp"] < 47: break
    print(name, out, flush=True)
e.close()
