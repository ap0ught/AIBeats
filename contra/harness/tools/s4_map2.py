"""Service map for the three open platings (model only): one full spray from (x, jump frame) per aim -> hits L C R (+cannon)."""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages import base_bsim as bs
st = sys.argv[1] if len(sys.argv) > 1 else "4"
R = np.load(f"logs/s{st}/x_cap_{'p0' if st == '4' else 'f0'}.npy")
base = bs.Sim.from_ram(R[100])
for e in base.en:
    if e[0] == bs.T_PLATE:
        e[bs.E_R], e[bs.E_HP] = 3, 99
    if e[0] == bs.T_CANNON:
        e[bs.E_R], e[bs.E_HP], e[bs.E_D] = 3, 99, 250
base.br = [0] * 10; base.nlive = 0
base.jump, base.py, base.pvy, base.pdir = 0, 201, 0, 0
plates = [e for e in base.en if e[0] in (bs.T_PLATE, bs.T_CANNON)]
plates.sort(key=lambda e: (e[0] != bs.T_PLATE, e[bs.E_Y], e[bs.E_X]))
print("targets:", [(hex(e[0]), e[bs.E_X], e[bs.E_Y]) for e in plates])
def shot(x, jf, dpad):
    s = base.copy(); s.px = x
    if jf >= 0:
        s.step(0, 1, 0)
        for _ in range(jf):
            s.step(0, 0, 0)
    s.step(dpad, 0, 1)
    y = s.py
    n = 0
    while (s.nlive or 2 in s.br) and n < 80:
        s.step(0, 0, 0); n += 1
    es = {e[bs.E_SLOT]: e for e in s.en}
    return "".join(str(99 - es[p[bs.E_SLOT]][bs.E_HP]) for p in plates), y
xs = list(range(32, 228, 8))
for nm, dp in (("up", 0), ("up-right", 9), ("up-left", 10), ("right", 1), ("left", 2)):
    print("aim", nm, " cell = hits per target in the order above")
    print("jf   y  " + " ".join(f"{x:>{len(plates)}d}" for x in xs))
    for jf in [-1] + list(range(0, 60, 4)):
        cells = []
        for x in xs:
            h, y = shot(x, jf, dp)
            cells.append(h if h.strip("0") else "." * len(h))
        print(f"{jf:3d} {y:3d}  " + " ".join(cells))
