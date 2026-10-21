"""Test: hand-built join into old 8300 from the b1 path (frame 243: 768.32 spd 96): Right x3, Left x4 (sprint), idle x2."""
import json
from l9heli_fix_lib import *
R = cap(); ins = up14_inputs()
g = json.load(open(LOGS_DIR / "fix" / "heli_beam_b1.json"))[0]
e = BizHawk(log_name="l9heli_fix_t1.log"); e.load(g["root"])
for b in g["inputs"][:243]: e.step(bt(b), 1)
def col(m): return [m[a] for a in range(0x3C1, 0x5E0, 15)]
for i, b in enumerate(["Right"] * 3 + ["Left"] * 4 + [""] * 2 + [""] * 3):
    e.step(bt(b), 1); m = e.ram(0, 0x800); print(i + 1, repr(b), tstr(m), "f", m[0x4A2], flush=True)
    if i == 8:
        ref = bytes(R[OFF + 8300 - 1]); print("old 8300:", tstr(ref), "f", ref[0x4A2])
        print("toad column diffs (addr ours old):", [(hex(0x3C1 + 15 * k), a, b2) for k, (a, b2) in enumerate(zip(col(m), col(ref))) if a != b2])
e.close()
