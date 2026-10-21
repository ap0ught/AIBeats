"""Track K THROWAWAY PROBE (debug pokes on a snapshot; nothing from here goes into a route): is the RISING head standable?
Root: sprint line rj 80 to r+127 (toad free above the head top, x 114, rel 19).  Poke the toad's x and vertical speed
(0x4C0/0x4CF) to 'falling', step idle, report z / anim / rel.     python u16k_pokeprobe.py -> logs/fix/u16k_pokeprobe.txt"""
from u16k_lib import *

e, lines = open_room("u16k_pokeprobe.log")
pre = [""] * 80 + ["Right", ""] + ["Right+A"] * 31 + [""] * 5 + ["A"] * 9
for b in pre:
    e.step(bt(b), 1)
base = e.msave()
out = []
for x in (100, 104, 108, 112, 116, 120, 124):
    for vy in (0, -1, -2):
        e.mload(base)
        e.poke(0x3FD, x)
        e.poke(0x4C0, vy & 0xFF)
        e.poke(0x4CF, 0)
        tr = []
        for j in range(14):
            e.step((), 1)
            t = rd(e)
            rel = (t["H"] - t["head"][1]) if t["head"] else None
            tr.append(f"{t['x']}/{rel}/z{t['z']}/a{t['an']}")
        out.append(f"poke x {x} vy {vy}: " + " ".join(tr))
        print(out[-1][:230], flush=True)
open(LOGS_DIR / "fix" / "u16k_pokeprobe.txt", "w").write("\n".join(out) + "\n")
e.close()
