"""Probe (snapshot, debug pokes): water/hazard map with the camera in place.  Root = L9heli_AB0 + Right x N (the toad falling right); poke x,H
to grid points inside the visible screen, step 2 idle frames, read the state.
Legend: W water (swim), . air, # standing, = stuck/slow, X dead/hurt, c carried.   python l9heli_fix_w2.py <N> <x0> <x1> <H top> <H bottom>"""
import sys
from l9heli_fix_lib import *
N, X0, X1, HT, HB = (int(v) for v in sys.argv[1:6])
e = BizHawk(log_name="l9heli_fix_w2.log"); e.load("L9heli_AB0")
for i in range(N): e.step(("Right",) if len(sys.argv) < 7 else bt(sys.argv[6]), 1)
m = e.ram(0, 0x800); print("root", tstr(m)); root = e.msave()
xs = list(range(X0, X1, 6)); Hs = list(range(HT, HB, -6))
print("     " + "".join(f"{x % 1000:4d}" for x in xs))
for H in Hs:
    row = ""
    for x in xs:
        e.mload(root)
        e.poke(0x3FD, x & 255); e.poke(0x3EE, x >> 8); e.poke(0x439, H & 255); e.poke(0x42A, H >> 8)
        e.step((), 2); m = e.ram(0, 0x800); s = toad(m)
        if s["hp"] < 47: c = "X"
        elif s["an"] in (98, 99): c = "W"
        elif s["an"] in CARRIED: c = "c"
        elif s["z"] == 0: c = "#"
        elif abs(s["H"] - H) < 4: c = "="
        else: c = "."
        row += "   " + c
    print(f"{H:5d}" + row, flush=True)
e.close()
