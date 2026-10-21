"""Where does a jump get the fast air speed (128)?  From the old route at L9c 8262 (809.160, spd 78, running left): run Left d frames,
then Left+A x4, Left to the landing.  Print takeoff x, the bump frame/x, max air speed, landing (frame, x.sub, spd, subH)."""
from l9heli_fix_lib import *
ins = up14_inputs()
e = BizHawk(log_name="l9heli_fix_t7.log"); goto(e, OFF + 8262, ins); root0 = e.msave()
for d in range(0, 44, 2):
    e.mload(root0)
    for i in range(d): e.step(("Left",), 1)
    m = e.ram(0, 0x800); x0 = toad(m)["x"]; sp0 = toad(m)["spd"]; f0 = m[0x4A2]
    bump = None; mx = 0; land = None; flip = None
    for i in range(70):
        e.step(bt("Left+A" if i < 4 else "Left"), 1); m = e.ram(0, 0x800); s = toad(m)
        if bump is None and s["an"] == 45: bump = (i + 1, s["x"], s["H"] - 6182, m[0x4A2])
        if flip is None and m[0x4A2] & 0x20: flip = (i + 1, s["x"], s["H"] - 6182)
        mx = max(mx, s["spd"])
        if i > 2 and s["z"] == 0: land = (i + 1, s["x"], s["sub"], s["spd"], m[0x466]); break
        if s["hp"] < 47: land = ("HURT", i + 1, s["x"]); break
    print(f"d {d}: takeoff x {x0} spd {sp0} f {f0}; bump {bump}; 0x20 set at {flip}; max air spd {mx}; land {land}", flush=True)
e.close()
