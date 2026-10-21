"""What does a mine hit do?  From the b1 path at frame 150: hold Left 120 frames (run into the mine); print toad x, H, spd, anim, hp, mine x every 2 frames around the hit."""
import json
from l9heli_fix_lib import *
g = json.load(open(LOGS_DIR / "fix" / "heli_beam_b1.json"))[0]
e = BizHawk(log_name="l9heli_fix_t12.log"); e.load(g["root"])
for b in g["inputs"][:150]: e.step(bt(b), 1)
hit = None
for i in range(130):
    e.step(("Left",), 1); m = e.ram(0, 0x800); s = toad(m)
    mi = [(m[0x3FD + q] | m[0x3EE + q] << 8, m[0x565 + q], m[0x51A + q]) for q in range(2, 15) if m[0x3C1 + q] == 0x72]
    if hit is None and s["hp"] < 47: hit = i
    if hit is not None and (i - hit) % 2 == 0 or (hit is None and i % 8 == 0):
        print(i + 1, "toad", s["x"], s["H"] - 6182, "spd", s["spd"], "an", s["an"], "hp", s["hp"], "z", s["z"], "f", m[0x4A2], "mine", mi, flush=True)
e.close()
