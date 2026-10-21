"""Offline test of Eye planner settings on the captured phase-B start states (logs/s2t/eye_caps.pkl).

    python tools/s2t_eye2.py <tag|all> [--show] ["E,alpha,k,width,xb,jb,lead,blockers" | "a,k,w,g,xb,jb" ...]

Prints, per start state and setting: frames from the platings' end to the flag (second pass executed: L2 132,
L0 134, g0 137, g37 153; the Eye can be hit 64 frames after the platings' end).
"""
import pickle
import sys
import time
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from contra.stages import base_bsim as bs, base_bplan as bp, base_bfight as bf  # noqa: E402


def parse(c):
    out = []
    for x in c.split(","):
        out.append(x if x.isalpha() else (float(x) if "." in x else int(x)))
    return tuple(out)


def show(sim0, pad, acts):
    s = sim0.copy()
    line = []
    hp = 16
    for i, a in enumerate(acts):
        dpad, a_new, b_new, pad = bp.sim_inputs(pad, a)
        s.step(dpad, a_new, b_new)
        e = next(x for x in s.en if x[0] == bs.T_EYE)
        h = 0 if e[bs.E_R] >= 5 else (16 if e[bs.E_R] < 3 else e[bs.E_V1] - (1 if e[bs.E_R] == 4 else 0))
        r = "".join(b[0] for b in bp.act_row(a)) or "."
        line.append(f"{i + 1}:{r}" + (f"[{h}]" if h != hp else "") + (f"(x{s.px}{'^' if s.jump else ''})" if (a_new or b_new) else ""))
        hp = h
    print("   ", " ".join(line))


if __name__ == "__main__":
    a = sys.argv[1:]
    showit = "--show" in a
    a = [x for x in a if x != "--show"]
    caps = pickle.load(open(ROOT / "logs" / "s2t" / "eye_caps.pkl", "rb"))
    tags = list(caps) if a[0] == "all" else [a[0]]
    cfgs = [parse(c) for c in a[1:]] or bf.PORTFOLIO_E
    jobs = []
    for tag in tags:
        c = caps[tag]
        pad = bp.pad_from_rows(c["rows"])
        prev_act = bp.act_of_row(c["rows"][-1])
        for cfg in cfgs:
            jobs.append((tag, dict(ram=c["ram"], pad=pad, prev_act=prev_act, cfg=cfg, opts={"hz_margin": 2})))
    t = time.time()
    with Pool(6) as pool:
        res = pool.map(bf.plan_job, [j for _, j in jobs])
    best = {}
    for (tag, j), r in zip(jobs, res):
        print(f"{tag:4s} {str(r['cfg']):46s} frames {r['n']} {r['stats']}", flush=True)
        if r["n"] is not None and (tag not in best or r["n"] < best[tag][0]["n"]):
            best[tag] = (r, j)
    print("total", round(time.time() - t), "s; best per state:", {k: v[0]["n"] for k, v in best.items()},
          "second pass executed:", {k: caps[k]["flag"] - caps[k]["plates_done"] for k in tags})
    if showit:
        for tag, (r, j) in best.items():
            print(tag, r["cfg"], r["n"])
            show(bs.Sim.from_ram(j["ram"]), j["pad"], r["acts"])
