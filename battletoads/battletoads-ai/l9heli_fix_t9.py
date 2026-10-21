"""The floor mine's (0x72) behaviour on the b1 path, every frame from 168 to 250 and then 60 more frames with the toad running on:
mine x, h, speed byte, flags, a few state bytes; toad x, H."""
import json
from l9heli_fix_lib import *
g = json.load(open(LOGS_DIR / "fix" / "heli_beam_b1.json"))[0]
e = BizHawk(log_name="l9heli_fix_t9.log"); e.load(g["root"])
seq = g["inputs"] + ["Left"] * 60
for i, b in enumerate(seq):
    e.step(bt(b), 1)
    if i + 1 >= 168:
        m = e.ram(0, 0x800); s = toad(m)
        q = [q for q in range(2, 15) if m[0x3C1 + q] == 0x72]
        if q:
            q = q[0]
            print(i + 1, repr(b).ljust(8), "toad", s["x"], s["H"] - 6182, s["spd"], "| mine x", m[0x3FD + q] | m[0x3EE + q] << 8, "h", m[0x439 + q], "spd", m[0x565 + q], "f", m[0x4A2 + q], "3df", m[0x3DF + q], "4de", m[0x4DE + q], "4ed", m[0x4ED + q], "4fc", m[0x4FC + q], "50b", m[0x50B + q], "5a1", m[0x5A1 + q], "5b0", m[0x5B0 + q], "5bf", m[0x5BF + q], flush=True)
e.close()
