from l9heli_fix_lib import *
e = BizHawk(log_name="l9heli_fix_t13.log")
for root in ("L9heli_s1end", "L9heli_s1end_b"):
    for act in ("Right", "", "Left", "Right+A"):
        e.load(root); out = []
        for i in range(12):
            e.step(bt(act), 1); m = e.ram(0, 0x800); s = toad(m); out.append((s["x"], s["H"] - 6400, s["an"], s["hp"]))
        print(root, repr(act), out, "|", ostr(m), flush=True)
e.close()
