"""Replay a heli_beam result and print the toad + mine (0x72) every k frames.  python l9heli_fix_show.py <json> [idx] [k] [from] [to]"""
import json, sys
from l9heli_fix_lib import *
j = json.load(open(sys.argv[1])); g = j[int(sys.argv[2]) if len(sys.argv) > 2 else 0]
k = int(sys.argv[3]) if len(sys.argv) > 3 else 2; a = int(sys.argv[4]) if len(sys.argv) > 4 else 0; b = int(sys.argv[5]) if len(sys.argv) > 5 else 10 ** 9
e = BizHawk(log_name="l9heli_fix_show.log"); e.load(g["root"])
for i, bn in enumerate(g["inputs"]):
    e.step(bt(bn), 1)
    if a <= i + 1 <= b and (i + 1) % k == 0:
        m = e.ram(0, 0x800); s = toad(m)
        mines = [(q, m[0x3FD + q] | m[0x3EE + q] << 8, m[0x439 + q], m[0x565 + q]) for q in range(2, 15) if m[0x3C1 + q] == 0x72]
        print(i + 1, g["root_index"] + i + 1, repr(bn).ljust(10), f"x {s['x']}.{s['sub']:3d} H {s['H']} z {s['z']} an {s['an']:2d} spd {s['spd']:3d} vy {m[0x4C0]},{m[0x4CF]} f {m[0x4A2]} cam {s['camx']},{s['camy']}", "mine", mines, flush=True)
e.close()
