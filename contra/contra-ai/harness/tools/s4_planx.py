"""Plan one boss phase offline from a frame of a RAM capture, several planner settings in parallel (development).

    python tools/s4_planx.py <stage> <capture name> <frame> [--v] [--one N] [--opt key=value ...] ["a,k,w,g,xb,jb" ...]

<frame> = index into logs/s<stage>/x_cap_<name>.npy (RAM after that many rows). Without settings: the portfolio of
base_bfight for the phase the frame is in. Prints the frames each setting needs and the timeline of the best plan.
"""
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from contra.stages import base_bsim as bs, base_bplan as bp, base_bfight as bf  # noqa: E402


def job_v(job):
    """Like bf.plan_job but verbose (single setting, for looking at one search)."""
    sim0 = job.get("sim") or bs.Sim.from_ram(job["ram"])
    phase = bf.phase_of(sim0)
    pl = bf.make_planner(sim0, phase, job["cfg"], repeat=job.get("repeat", ()), **job.get("opts", {}))
    pl.verbose = True
    goals = pl.run(sim0, job["pad"], job.get("t_max", 420), extra_layers=1, prev_act=job.get("prev_act", 0))
    print("stats", pl.stats, "goals", len(goals))
    return goals


def timeline(sim0, pad, acts, k0):
    s = sim0.copy()
    prev = None
    for i, a in enumerate(acts):
        dpad, a_new, b_new, pad = bp.sim_inputs(pad, a)
        sh = s.shots
        s.step(dpad, a_new, b_new)
        parts = []
        for e in s.en:
            if e[0] == bs.T_PLATE:
                parts.append("--" if e[bs.E_R] >= 4 else ("cl" if e[bs.E_HP] >= 0xF0 else f"{e[bs.E_HP]:2d}"))
            elif e[0] == bs.T_CANNON:
                parts.append("c--" if e[bs.E_R] >= 5 else ("c.." if e[bs.E_HP] >= 0xF0 else f"c{e[bs.E_HP]:2d}"))
            elif e[0] == bs.T_HELMET:
                parts.append("h--" if e[bs.E_R] >= 5 else f"h{e[bs.E_V4]:2d}{'v' if e[bs.E_COL] else '.'}x{e[bs.E_X]:3d}d{e[bs.E_D]:2d}")
            elif e[0] == bs.T_EYE:
                parts.append("E--" if e[bs.E_R] >= 5 else f"E{e[bs.E_V1]:2d}{'v' if e[bs.E_COL] else '.'}x{e[bs.E_X]:3d}")
        cur = " ".join(parts) + (f" rings{[(g[0] >> 8, g[1] >> 8, g[4]) for g in s.rg]}" if s.rg else "")
        if cur != prev or s.shots != sh or a_new:
            print(f"row {k0 + i + 1:3d} {'+'.join(bp.act_row(a)):14s} P({s.px:3d},{s.py:3d}) j{s.jump} free{s.free_slots():2d} "
                  f"{'FIRE' if s.shots != sh else '    '} {'JUMP' if a_new else '    '} | {cur} | pl{s.plates}"
                  + (" DEAD" if s.dead else "") + (" BOSSDEF" if s.bossdef else ""))
        prev = cur


if __name__ == "__main__":
    a = sys.argv[1:]
    verbose = "--v" in a
    if verbose:
        a.remove("--v")
    one = None
    if "--one" in a:
        i = a.index("--one")
        one = int(a[i + 1])
        del a[i:i + 2]
    opts = {}
    while "--opt" in a:
        i = a.index("--opt")
        k, v = a[i + 1].split("=")
        opts[k] = float(v) if "." in v else int(v)
        del a[i:i + 2]
    after = None
    if "--after" in a:
        i = a.index("--after")
        after = a[i + 1]
        del a[i:i + 2]
    ground = None
    if "--ground" in a:
        i = a.index("--ground")
        ground = int(a[i + 1])
        del a[i:i + 2]
    hack = [x for x in a if x in ("--nocannon", "--nobullets")]
    a = [x for x in a if x not in hack]
    st, name, frame = a[0], a[1], int(a[2])
    a += hack
    R = np.load(ROOT / f"logs/s{st}/x_cap_{name}.npy")
    J = json.load(open(ROOT / f"logs/s{st}/x_cap_{name}.json"))
    rows = [tuple(r) for r in J["rows"]][:frame]
    ram = bytearray(bytes(R[frame]))
    if ground is not None:          # experiment: put Bill on the ground at this x (not a real state)
        ram[0x334], ram[0x31A], ram[0xA0], ram[0xC6], ram[0xC4] = ground, 201, 0, 0, 0
        rows = []
    if "--nocannon" in a:           # experiment: the wall cannon(s) removed (not a real state)
        a.remove("--nocannon")
        for k in range(16):
            if ram[0x528 + k] == 0x08:
                ram[0x4B8 + k] = 0
    if "--nobullets" in a:
        a.remove("--nobullets")
        for k in range(10):
            ram[0x388 + k] = 0
    ram = bytes(ram)
    sim0 = bs.Sim.from_ram(ram)
    pad = bp.pad_from_rows(rows)
    if after:                       # continue from the end of an earlier plan (played in the model)
        pr = [tuple(r) for r in json.load(open(ROOT / f"logs/s{st}" / after))["rows"]]
        sim0, pad = bp.play(sim0, pad, [bp.act_of_row(r) for r in pr])
        rows = rows + pr
        frame += len(pr)
    phase = bf.phase_of(sim0)
    cfgs = [tuple(float(x) if "." in x else int(x) for x in c.split(",")) for c in a[3:]] or \
        bf.portfolio_for(sim0)
    prev_act = bp.act_of_row(rows[-1]) if rows else 0
    print("phase", phase, "start:", sim0.describe()[:300])
    t = time.time()
    if one is not None:
        goals = job_v(dict(ram=ram, sim=sim0, pad=pad, prev_act=prev_act, cfg=cfgs[one], opts=opts))
        if goals:
            timeline(sim0, pad, goals[0].acts(), frame)
        sys.exit()
    jobs = [dict(ram=ram, sim=sim0, pad=pad, prev_act=prev_act, cfg=c, opts=opts) for c in cfgs]
    best = None
    with Pool(min(len(cfgs), 6)) as pool:
        for r in pool.imap_unordered(bf.plan_job, jobs):
            print(r["cfg"], "frames", r["n"], "cost", r.get("cost"), "end", r.get("end"), r["stats"], flush=True)
            if r["acts"] is not None and (best is None or r["cost"] < best["cost"]):
                best = r
    print("total", round(time.time() - t), "s; best", best["n"] if best else None, best["cfg"] if best else None)
    if best:
        json.dump({"k0": frame, "rows": [bp.act_row(x) for x in best["acts"]]},
                  open(ROOT / f"logs/s{st}/x_planx_{name}_{frame}.json", "w"))
        if verbose:
            timeline(sim0, pad, best["acts"], frame)
