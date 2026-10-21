from l9heli_fix_lib import *
e = BizHawk(log_name="l9heli_fix_t14.log")
for act in ("Right", "", "Left", "A", "Left+A"):
    e.load("L9heli_A0"); out = []
    for i in range(40):
        e.step(bt(act), 1); m = e.ram(0, 0x800); s = toad(m)
        if i % 3 == 2 or s["hp"] < 47 or s["an"] in CARRIED: out.append((i + 1, s["x"], s["H"] - 6400, s["spd"], s["an"], s["hp"]))
        if s["hp"] < 47 or s["an"] in CARRIED: break
    print(repr(act), out, flush=True)
e.close()
