"""Third pass, Eye experiments on the offline boss model (base_bsim).

    python tools/s2t_eye1.py speed          sim speed
    python tools/s2t_eye1.py exits          when the pellets of one spray free their slots, by aim / pose
"""
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from contra.stages import base_bsim as bs, base_bplan as bp  # noqa: E402

E_R, E_HP, E_D, E_X, E_V1, E_COL = bs.E_R, bs.E_HP, bs.E_D, bs.E_X, bs.E_V1, bs.E_COL


def cap_state(name="f0", plates=4):
    """(sim, row index) at the first frame of the capture on which `plates` platings are destroyed."""
    ram = np.load(ROOT / "logs" / "s2" / f"x_cap_{name}.npy")
    for i in range(len(ram)):
        if ram[i][0x87] >= plates and ram[i][0x40] & 0x80:
            return bs.Sim.from_ram(bytes(ram[i])), i
    raise SystemExit("no such frame")


def eye(s):
    return next(e for e in s.en if e[0] == bs.T_EYE)


if __name__ == "__main__":
    cmd = sys.argv[1]
    s0, i0 = cap_state()
    e = eye(s0)
    print("capture f0 frame", i0, s0.describe()[:300])
    if cmd == "speed":
        t = time.time()
        n = 0
        s = s0.copy()
        for k in range(20000):
            s.step(0, 0, 1 if k % 5 == 0 else 0)
            n += 1
        print("steps/s", round(n / (time.time() - t)))
    if cmd == "exits":
        # clear all bullets, put Bill on the ground at x, fire one spray with a d-pad, list the frames the slots free
        for x in (100, 128, 160):
            for name, dp in (("up", 0), ("up+right", bs.U | bs.R), ("up+left", bs.U | bs.L), ("right", bs.R), ("left", bs.L)):
                s = s0.copy()
                s.br = [0] * 10
                s.nlive = 0
                s.px, s.py, s.jump = x, bs.GROUND_Y, 0
                for en in s.en:
                    en[E_COL] = 0 if en[0] == bs.T_EYE else en[E_COL]
                    if en[0] == bs.T_EYE:
                        en[E_D] = 200          # keep it shut
                s.step(dp, 0, 1)
                free = {}
                for t in range(1, 90):
                    s.step(0, 0, 0)
                    for sl in range(5):
                        if s.br[sl] == 0 and sl not in free:
                            free[sl] = t
                print(f"ground x{x} {name:9s}: slots free after {[free.get(sl) for sl in range(5)]} frames (centre, +1, -1, +2, -2)")
