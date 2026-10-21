"""Slow walk vs normal: experiments from the OLD route's own state at L9c 8279 (running left at 96 on the floor, slow mode).
(i) keep running Left 60 frames: speeds;  (ii) Left+A x k then Left: air speeds/flags;  (iii) tap/sprint tests after 20 more frames."""
from l9heli_fix_lib import *
ins = up14_inputs()
e = BizHawk(log_name="l9heli_fix_t6.log"); goto(e, OFF + 8279, ins); e.save("L9heli_8279"); root0 = e.msave()
def run(seq, every=2):
    e.mload(root0); out = []
    for i, b in enumerate(seq):
        e.step(bt(b), 1)
        if i % every == every - 1:
            m = e.ram(0, 0x800); s = toad(m); out.append((s["x"], s["H"] - 6182, s["spd"], m[0x4A2], s["z"]))
    return out
print("(i) run Left 60:", run(["Left"] * 60, 4), flush=True)
print("(i') run Left 20, idle 2, Left 6:", run(["Left"] * 20 + [""] * 2 + ["Left"] * 6, 1)[18:], flush=True)
for k in (1, 2, 3, 4, 6, 10):
    print(f"(ii) Left+A x{k} then Left:", run(["Left+A"] * k + ["Left"] * (44 - k), 2), flush=True)
print("(iii) old jump but idle instead of Left after the A frames:", run(["Left+A"] * 4 + [""] * 40, 2), flush=True)
e.close()
