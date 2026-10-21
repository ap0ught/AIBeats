"""Print the timeline of an offline plan file (model only).  python tools/s4_show.py <stage> <capture tag> <plan json>"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from contra.stages import base_bsim as bs, base_bplan as bp  # noqa: E402

st, tag, plan = sys.argv[1], sys.argv[2], sys.argv[3]
R = np.load(ROOT / f"logs/s{st}/x_cap_{tag}.npy")
P = json.load(open(ROOT / f"logs/s{st}" / plan))
k0 = P["k0"]
s = bs.Sim.from_ram(R[k0])
pad = bp.pad_from_rows([])
prev = None
for i, r in enumerate(P["rows"]):
    act = bp.act_of_row(r)
    dpad, a_new, b_new, pad = bp.sim_inputs(pad, act)
    sh = s.shots
    s.step(dpad, a_new, b_new)
    parts = []
    for e in s.en:
        if e[0] == bs.T_PLATE:
            parts.append("--" if e[bs.E_R] >= 4 else ("cl" if e[bs.E_HP] >= 0xF0 else f"{e[bs.E_HP]:2d}"))
        elif e[0] == bs.T_CANNON:
            parts.append("c--" if e[bs.E_R] >= 5 else ("c.." if e[bs.E_HP] >= 0xF0 else f"c{e[bs.E_HP]:2d}"))
        elif e[0] == bs.T_HELMET:
            parts.append("h--" if e[bs.E_R] >= 5 else f"h{e[bs.E_V4]:2d}{'v' if e[bs.E_COL] else '.'}x{e[bs.E_X]}")
        elif e[0] == bs.T_EYE:
            parts.append("E--" if e[bs.E_R] >= 5 else f"E{e[bs.E_V1]:2d}{'v' if e[bs.E_COL] else '.'}x{e[bs.E_X]}")
    cur = " ".join(parts)
    if cur != prev or s.shots != sh or a_new:
        print(f"i={k0 + i + 1:3d} {'+'.join(r):14s} P({s.px:3d},{s.py:3d}) j{s.jump} free{s.free_slots():2d} "
              f"{'FIRE' if s.shots != sh else '    '} {'JUMP' if a_new else '    '} | {cur} | plates {s.plates}"
              + (" DEAD" if s.dead else "") + (" BOSSDEF" if s.bossdef else ""))
    prev = cur
print("end:", s.describe())
