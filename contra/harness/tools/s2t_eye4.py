"""Offline test of contra/stages/base_eye.py on the captured phase-B start states (logs/s2t/eye_caps.pkl).

    python tools/s2t_eye4.py <tag|all> [stage1|full] [width of the stage-2 planner]

stage1: hits by opening + 20 for the best scripts. full: stage 1 + the generic planner for the rest (frames from the
platings' end to the flag; second pass executed: L2 132, L0 134, g0 137, g37 153).
"""
import pickle
import sys
import time
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from contra.stages import base_bsim as bs, base_bplan as bp, base_bfight as bf, base_eye as be  # noqa: E402

if __name__ == "__main__":
    a = sys.argv[1:]
    caps = pickle.load(open(ROOT / "logs" / "s2t" / "eye_caps.pkl", "rb"))
    tags = list(caps) if a[0] == "all" else [a[0]]
    mode = a[1] if len(a) > 1 else "stage1"
    width = int(a[2]) if len(a) > 2 else 600
    for tag in tags:
        c = caps[tag]
        sim0 = bs.Sim.from_ram(c["ram"])
        pad0 = bp.pad_from_rows(c["rows"])
        prev_act = bp.act_of_row(c["rows"][-1])
        t = time.time()
        res = be.stage1(sim0, pad0, prev_act, verbose=True, after=int(a[3]) if len(a) > 3 else 5,
                        n_exact=int(a[4]) if len(a) > 4 else 200)
        print(tag, f"Bill x{sim0.px} jump {sim0.jump}; stage 1 in {time.time() - t:.0f} s")
        for hp, nf, lane, t_A, blk, acts, s2, p2 in res:
            pr = [i + 1 for i, x in enumerate(acts) if x & 16 and (i == 0 or not acts[i - 1] & 16)]
            print(f"   HP {hp} free {nf} lane {lane} A at {t_A} blockers {blk} presses {pr}")
        if mode == "full" and res:
            t = time.time()
            gamma = float(a[5]) if len(a) > 5 else 1.5
            jobs = [dict(sim=r[6], ram=None, pad=r[7], prev_act=r[5][-1], cfg=(0.02, 2, width, gamma, 4, 3),
                         opts={"hz_margin": 2}) for r in res]
            with Pool(6) as pool:
                out = pool.map(bf.plan_job, jobs)
            tot = [(len(r[5]) + o["n"]) if o["n"] is not None else None for r, o in zip(res, out)]
            print(f"   stage 2 ({time.time() - t:.0f} s): frames to the flag per candidate {tot}; best "
                  f"{min(x for x in tot if x is not None) if any(tot) else None}; second pass executed "
                  f"{c['flag'] - c['plates_done']}")
