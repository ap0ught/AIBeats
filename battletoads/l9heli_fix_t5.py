"""What ends the slow walk (cap 96, no sprint)?  From the b1 path at frame 248 (760.160, running left at 96, mine behind): jump with
Left+A held k frames, keep Left to the landing, then idle 2, Left x8.  Print the air speeds, flags, landing frame/x and the speeds after."""
import json
from l9heli_fix_lib import *
g = json.load(open(LOGS_DIR / "fix" / "heli_beam_b1.json"))[0]
e = BizHawk(log_name="l9heli_fix_t5.log"); e.load(g["root"])
for b in g["inputs"][:248]: e.step(bt(b), 1)
root0 = e.msave()
for k in (1, 2, 3, 4, 5, 6, 8, 12, 20):
    e.mload(root0); air = []; land = None
    for i in range(70):
        e.step(bt("Left+A" if i < k else "Left"), 1); m = e.ram(0, 0x800); s = toad(m)
        if i % 3 == 0: air.append((s["H"] - 6182, s["spd"], m[0x4A2]))
        if i > 2 and s["z"] == 0: land = (i + 1, s["x"], s["sub"], s["spd"], m[0x4A2], m[0x466], s["hp"]); break
    after = []
    for b in ["", ""] + ["Left"] * 8:
        e.step(bt(b), 1); m = e.ram(0, 0x800); after.append(m[0x565])
    print(f"A x{k}: land {land} air (dH, spd, f) {air} | after idle2+Left8: {after}", flush=True)
e.close()
