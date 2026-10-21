"""Service map for the merged helmets (model only): one full spray from (x, jump frame) with a given aim -> hits per helmet.
    python tools/s4_map.py <cannon dead 0|1>"""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages import base_bsim as bs
R = np.load("logs/s4/x_cap_p0.npy")
dead = int(sys.argv[1])
base = bs.Sim.from_ram(R[290])           # helmets merged and vulnerable (A = 286), 28 frames left
for e in base.en:
    if e[0] == bs.T_CANNON and dead:
        e[bs.E_R], e[bs.E_COL] = 7, 0
    if e[0] == bs.T_HELMET:
        e[bs.E_D] = 200; e[bs.E_V4] = 99        # keep them open and alive for the measurement
base.br = [0] * 10; base.nlive = 0
base.jump, base.py, base.pvy, base.pdir = 0, 201, 0, 0
def shot(x, jf, dpad):
    s = base.copy(); s.px = x
    if jf >= 0:
        s.step(0, 1, 0)
        for _ in range(jf):
            s.step(0, 0, 0)
    s.step(dpad, 0, 1)
    y = s.py
    n = 0
    busy = 0
    while (s.nlive or 2 in s.br) and n < 80:
        s.step(0, 0, 0); n += 1; busy += 10 - s.br.count(0)
    hl = 99 - [e for e in s.en if e[0] == bs.T_HELMET and e[bs.E_V1] == 104][0][bs.E_V4]
    hr = 99 - [e for e in s.en if e[0] == bs.T_HELMET and e[bs.E_V1] == 152][0][bs.E_V4]
    return hl, hr, busy, y
print("aim up (no d-pad); rows = jump frame (-1 = ground), columns = x; cell = hitsL,hitsR")
xs = list(range(96, 164, 4))
print("jf   y  " + " ".join(f"{x:4d}" for x in xs))
for jf in [-1] + list(range(0, 60, 3)):
    cells = []
    for x in xs:
        hl, hr, busy, y = shot(x, jf, 0)
        cells.append(f" {hl}{hr} " if hl + hr else "  . ")
    print(f"{jf:3d} {y:3d}  " + " ".join(cells))
for nm, dp in (("up-right", 9), ("up-left", 10)):
    print("aim", nm)
    xs2 = list(range(32, 224, 8))
    print("jf   y  " + " ".join(f"{x:4d}" for x in xs2))
    for jf in [-1] + list(range(0, 60, 4)):
        cells = []
        for x in xs2:
            hl, hr, busy, y = shot(x, jf, dp)
            cells.append(f" {hl}{hr} " if hl + hr else "  . ")
        print(f"{jf:3d} {y:3d}  " + " ".join(cells))
