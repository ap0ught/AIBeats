"""probe: what the level timers and the toad do around the Terra Tubes placement, old run vs the new Level 8 variants"""
import json, sys
from u16a_lib import *
old = seg("L8c"); l9 = seg("L9heli_c2")
fj = json.load(open(FIX.parent / "fix" / "early_l8fight_e.json"))
pre = old[:3113] + list(fj["arrival_prefix"]) + list(fj["inputs"])
e = BizHawk(log_name="u16a_p1.log")
def row(m): 
    t = toad(m); return f"lv {t['level']:3d} x {t['x']:3d} h {t['h']:3d} hp {t['hp']:2d} t {t['t0b']:3d}/{t['t0c']} an {m[0x3B5]} st {m[0x4B1]} rng {t['rng']}"
print("== L8c + first 12 of L9heli_c2")
e.load("L6c_end0")
for n, b in enumerate(old + l9[:12], 1):
    e.step(bt(b), 1)
    if n >= len(old) - 12: print(n, repr(b), row(e.ram(0, 0x800)), "<- L8c end" if n == len(old) else "")
for st, first in ((300, "A"), (100, "A"), (0, "A"), (100, "B")):
    print(f"== new, mash +{st} {first} first")
    e.load("L6c_end0")
    for b in pre: e.step(bt(b), 1)
    pat = ("A", "B") if first == "A" else ("B", "A")
    for k in range(500):
        b = "" if k < st else pat[(k - st) % 2]
        e.step(bt(b), 1); n = len(pre) + k + 1
        if n >= 4456: print(n, repr(b), row(e.ram(0, 0x800)))
e.close()
