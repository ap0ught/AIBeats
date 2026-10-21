"""Sprint arming in the NORMAL zone (x < ~750): from the b1 path at frame 248 (760.160, running left at 96) run on to x <= K0 holding
Left, then: idle g1, Left p, idle g2, [Right g3], Left x4 -> speeds on the last four frames + x."""
import json
from l9heli_fix_lib import *
g = json.load(open(LOGS_DIR / "fix" / "heli_beam_b1.json"))[0]
e = BizHawk(log_name="l9heli_fix_t3.log"); e.load(g["root"])
for b in g["inputs"][:248]: e.step(bt(b), 1)
root0 = e.msave()
def test(pre, seq):
    e.mload(root0)
    for b in ["Left"] * pre + seq: e.step(bt(b), 1)
    m = e.ram(0, 0x800); return (m[0x565], m[0x3FD] | m[0x3EE] << 8, m[0x4A2])
for pre in (0, 8, 16, 24):
    e.mload(root0)
    for b in ["Left"] * pre: e.step(bt(b), 1)
    m = e.ram(0, 0x800); print("pre", pre, tstr(m), "f", m[0x4A2], flush=True)
    for (g1, p, g2, g3) in [(4, 4, 4, 4), (4, 4, 4, 0), (4, 4, 8, 0), (1, 4, 4, 0), (1, 1, 1, 0), (1, 2, 2, 0), (2, 2, 2, 0), (1, 4, 1, 0), (1, 8, 2, 0), (1, 0, 0, 0), (4, 0, 0, 0), (0, 0, 2, 4)]:
        seq = [""] * g1 + ["Left"] * p + [""] * g2 + ["Right"] * g3 + ["Left"]
        print(f"   idle {g1}, Left {p}, idle {g2}, Right {g3}, Left -> (spd, x, f) {test(pre, seq)}", flush=True)
e.close()
