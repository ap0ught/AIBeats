"""Does the model's cannon-bullet death test agree with a capture?  python tools/s4_hzcheck.py <stage> <name> ..."""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages import base_bsim as bs
st = sys.argv[1]
for name in sys.argv[2:]:
    R = np.load(f"logs/s{st}/x_cap_{name}.npy"); J = json.load(open(f"logs/s{st}/x_cap_{name}.json")); lag = J["lag"]
    k0 = 9
    sim = bs.Sim.from_ram(R[k0])
    sd = rd = None
    mind = 99
    for i in range(k0 + 1, len(R)):
        if lag[i]:
            continue
        m = bytes(R[i])
        if rd is None and m[0x90] == 2:
            rd = i
        if sd is None:
            sim.step(m[0xF1] & 15, m[0xF5] & 0x80, m[0xF5] & 0x40)
            if sim.dead:
                sd = i
            for h in sim.hz:
                hx, hy = h[0] >> 8, h[1] >> 8
                if sim.jump:
                    d = max(-2 - (hy - sim.py), (hy - sim.py) - 11, -6 - (hx - sim.px), (hx - sim.px) - 7)
                else:
                    d = max(-16 - (hy - sim.py), (hy - sim.py) - 18, -6 - (hx - sim.px), (hx - sim.px) - 7)
                mind = min(mind, d)
    print(name, "death: model", sd, "ram", rd, "closest miss (px outside the box)", mind)
