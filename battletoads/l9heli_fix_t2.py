"""Sprint (double-tap) rule on the Terra Tubes floor: from the b1 path at frame 243 (running left at 96, Left held 36 frames):
idle g1, Left p (tap), [idle | Right] g2, Left -> is the speed 192 on that frame?  Also: tap in the air, and Left+A (dash jump)."""
import json
from l9heli_fix_lib import *
g = json.load(open(LOGS_DIR / "fix" / "heli_beam_b1.json"))[0]
e = BizHawk(log_name="l9heli_fix_t2.log"); e.load(g["root"])
for b in g["inputs"][:243]: e.step(bt(b), 1)
root = e.msave()
def test(seq):
    e.mload(root)
    for b in seq: e.step(bt(b), 1)
    m = e.ram(0, 0x800); return m[0x565], m[0x3FD] | m[0x3EE] << 8, m[0x448], m[0x4A2], m[0x475]
print("gap kind = idle")
for g1 in (1, 2, 4):
    for p in (1, 2, 3, 4, 6, 8, 12):
        row = []
        for g2 in (1, 2, 3, 4, 6, 8, 10, 12, 14, 16, 20):
            s = test([""] * g1 + ["Left"] * p + [""] * g2 + ["Left"]); row.append(s[0])
        print(f"idle {g1}, Left {p}, idle g2 (1,2,3,4,6,8,10,12,14,16,20), Left -> spd", row, flush=True)
print("gap kind = Right")
for p in (1, 2, 4, 8):
    row = []
    for g2 in (1, 2, 3, 4, 6, 8, 12):
        s = test([""] * 1 + ["Left"] * p + ["Right"] * g2 + ["Left"]); row.append(s[0])
    print(f"idle 1, Left {p}, Right g2 (1,2,3,4,6,8,12), Left -> spd", row, flush=True)
print("no fresh tap: idle g, Left")
print([test([""] * gg + ["Left"])[0] for gg in (1, 2, 3, 4, 6, 8)])
print("dash jump: idle 1, Left p, idle g2, Left+A -> spd, z")
for p in (1, 2, 4):
    print(p, [test([""] * 1 + ["Left"] * p + [""] * g2 + ["Left+A"])[::4] for g2 in (1, 2, 4, 8)])
e.close()
