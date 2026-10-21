"""Offline planner runs on recorded room traces (logs/s4t/rooms_<stage>.pkl, made by tools/s4t_snip/dump.py).

    python tools/s4t_plan.py <stage> <room> [beam] [module]

module: base_plan (default) or another planner module name under contra.stages with the same plan_room signature.
"""
import importlib
import pickle
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def load(stage, room):
    d = pickle.load(open(ROOT / "logs" / "s4t" / f"rooms_{stage}.pkl", "rb"))[room]
    return d


def setup(bp, d, t_rec=440):
    tr = d["tr"][:t_rec]
    ents = bp.entities_from_trace(tr)
    T_land = d["T_land"]
    px = tr[T_land]["x"]
    air = {T: (tr[T - 1]["x"], min(tr[T - 1]["y"], 152) - 40) for T in range(2, T_land) if tr[T - 1]["jump"]}
    plated = [e.eid for e in ents if e.kind == "core" and e.attr & 4]
    jump_y = None
    for e in ents:
        if e.kind == "core" and not (e.attr & 4):
            x0, y0, _ = e.track[min(e.track)]
            if not any(bp.in_box(x0, yy, x0, y0, 5) for yy in (bp.STAND_Y, bp.CROUCH_Y)):
                jump_y = d["jump_y"]
    hp_over = {eid: 23 for eid in plated}
    return dict(ents=ents, T_land=T_land, px=px, air=air, plated=plated, jump_y=jump_y, hp_over=hp_over,
                face0=1 if tr[T_land]["aim"] >= 5 else 0, tr=tr)


def main():
    stage, room = int(sys.argv[1]), int(sys.argv[2])
    beam = int(sys.argv[3]) if len(sys.argv) > 3 else 12000
    mod = sys.argv[4] if len(sys.argv) > 4 else "base_plan"
    bp = importlib.import_module(f"contra.stages.{mod}")
    d = load(stage, room)
    for t_rec, t_max in ((440, 430), (560, 540)):
        k = setup(bp, d, t_rec)
        t0 = time.time()
        plans = bp.plan_room(k["ents"], k["T_land"] + 1, k["px"], k["px"], hp_over=k["hp_over"], t_max=t_max, beam=beam,
                             ntop=6, air=k["air"], plated=k["plated"], jump_y=k["jump_y"], face0=k["face0"])
        if plans:
            break
    print(f"stage {stage} room {room} beam {beam}: finish {[p.finish for p in plans]} in {time.time() - t0:.1f} s (t_max {t_max})")
    if plans:
        print(plans[0])


if __name__ == "__main__":
    main()
