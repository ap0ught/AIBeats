"""L12h stage 2 probe: when does face 2's wind let go? From L12g's pole (grab 5454, face 5444): idle to D, drop (Left, Down+Left, then Left
held), print the track until 60 frames after the landing."""
import sys
from l12h_lib import *
G = seg("L12g")
e = BizHawk(log_name="fix_l12h_s2a.log"); e.load("L12h_g_f5250")
run(e, G[5250:5700]); base = e.msave()
for D in [int(a) for a in sys.argv[1:]]:
    e.mload(base); k = 5700; out = []
    while k < D: e.step((), 1); k += 1
    land = None
    for i in range(130):
        b = "Left" if i != 1 else "Down+Left"
        e.step(bt(b), 1); k += 1; s = rd(e)
        if land is None and s["z"] == 0: land = k
        out.append(f"{k}:{s['x']},{s['H']},a{s['an']},s{s['spd']}")
        if not alive(s): out.append("DEAD"); break
        if land and k > land + 50: break
    print("D", D, "land", land, " ".join(out[::3]), flush=True)
e.close()
