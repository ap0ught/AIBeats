"""Check the offline boss model (contra/stages/base_bsim.py) against a RAM capture of a real fight.

    python tools/s4_simcheck.py <stage> <tag> [start frame ...]

For every start frame: load the model from the captured RAM, step it with the inputs the game itself saw
($F1 / $F5) and compare player, bullets and boss parts after every frame. Prints the first mismatches.
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages import base_bsim as bs  # noqa: E402

st, tag = sys.argv[1], sys.argv[2]
R = np.load(f"logs/s{st}/x_cap_{tag}.npy")
J = json.load(open(f"logs/s{st}/x_cap_{tag}.json"))
lag = J["lag"]
starts = [int(x) for x in sys.argv[3:] if x != '-v'] or [9]
VERB = "-v" in sys.argv


def diff(sim, m):
    d = []
    for nm, a, b in (("px", sim.px, m[0x334]), ("py", sim.py, m[0x31A]), ("pys", sim.pys, m[0x94]),
                     ("jump", sim.jump, 1 if m[0xA0] else 0), ("plates", sim.plates, m[0x87]),
                     ("cores", sim.cores, m[0x86]), ("bossdef", sim.bossdef, m[0x3B] & 1), ("fc", sim.fc, m[0x1A])):
        if a != b:
            d.append(f"{nm} sim {a} ram {b}")
    for i in range(10):
        occ = 1 if m[0x388 + i] else 0
        r = m[0x438 + i]
        rr = 0 if not occ else (1 if r <= 1 else 2)
        if sim.br[i] != rr:
            d.append(f"b{i} routine sim {sim.br[i]} ram {rr}")
        elif rr and (sim.bx[i] >> 8 != m[0x3C8 + i] or sim.by[i] >> 8 != m[0x3B8 + i]):
            d.append(f"b{i} pos sim {sim.bx[i] >> 8},{sim.by[i] >> 8} ram {m[0x3C8 + i]},{m[0x3B8 + i]}")
    for e in sim.en:
        k = e[bs.E_SLOT]
        if m[0x528 + k] != e[0]:
            if e[bs.E_R] < 6:
                d.append(f"e{k} type gone in ram (sim r{e[bs.E_R]})")
            continue
        rt = m[0x4B8 + k]
        if (rt >= 6 or rt == 0) and e[bs.E_R] >= 6:
            continue
        for nm, a, b in (("r", e[bs.E_R], rt), ("hp", e[bs.E_HP], m[0x578 + k]), ("x", e[bs.E_X], m[0x33E + k]),
                         ("delay", e[bs.E_D], m[0x538 + k]),
                         ("col", e[bs.E_COL], 0 if (m[0x598 + k] & 0x80) or not m[0x30A + k] else 1)):
            if a != b:
                d.append(f"e{k}(t{e[0]:02x}) {nm} sim {a} ram {b}")
        if e[0] == bs.T_HELMET and e[bs.E_V4] != m[0x5E8 + k]:
            d.append(f"e{k} v4 sim {e[bs.E_V4]} ram {m[0x5E8 + k]}")
        if e[0] in (bs.T_EYE, bs.T_CANNON) and e[bs.E_V1] != m[0x5B8 + k]:
            d.append(f"e{k} v1 sim {e[bs.E_V1]} ram {m[0x5B8 + k]}")
    return d


for k0 in starts:
    while lag[k0]:
        k0 += 1
    sim = bs.Sim.from_ram(R[k0])
    bad = 0
    n = 0
    for i in range(k0 + 1, len(R)):
        if lag[i]:
            continue
        m = bytes(R[i])
        if m[0x2C] != 4:        # level routine left 04 (boss defeated): the model stops here
            break
        sim.step(int(m[0xF1]) & 0x0F, int(m[0xF5]) & 0x80, int(m[0xF5]) & 0x40)
        n += 1
        d = diff(sim, m)
        if d:
            bad += 1
            if bad <= 6:
                print(f"start {k0} frame {i}: " + "; ".join(d[:8]))
                if VERB:
                    print("   ", sim.describe())
            # resync so one error does not hide the rest
            sim = bs.Sim.from_ram(m)
    print(f"start {k0}: {n} frames compared, {bad} frames with a mismatch (model re-loaded after each)")
