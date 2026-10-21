"""Is bit 0x20 of $4A2 a function of the toad's screen x ($484 = x - camera)?  From the b1 path at frame 248 (760.160, running left,
flag set): idle 40 frames, then Left 40 frames; print per frame x, cam, $484, spd, $4A2."""
import json
from l9heli_fix_lib import *
g = json.load(open(LOGS_DIR / "fix" / "heli_beam_b1.json"))[0]
e = BizHawk(log_name="l9heli_fix_t8.log"); e.load(g["root"])
for b in g["inputs"][:248]: e.step(bt(b), 1)
for i, b in enumerate([""] * 40 + ["Left"] * 44 + ["Right"] * 30):
    e.step(bt(b), 1); m = e.ram(0, 0x800); s = toad(m)
    print(i + 1, repr(b).ljust(7), "x", s["x"], "cam", s["camx"], "s484", m[0x484], "spd", s["spd"], "f", m[0x4A2], flush=True)
e.close()
