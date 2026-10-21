"""Offline runs of the third-pass room planner on recorded room traces (logs/s4t/rooms_<stage>.pkl).

    python tools/s4t_plan3.py <stage> <room> [free|fixed|nosteer] [beam] [keep]

fixed   = entry x as recorded, hop steering on;  free = entry x anywhere within reach of the previous room's exit
(+-70 px of the recorded x);  nosteer = entry as recorded, no steering (the first planner's situation).
"""
import pickle
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from contra.stages import base_plan3 as bp  # noqa: E402


def setup(d, t_rec=440):
    tr = d["tr"][:t_rec]
    ents = bp.entities_from_trace(tr)
    T_land = d["T_land"]
    px = tr[T_land]["x"]
    air_y = {T: min(tr[T - 1]["y"], 152) - 40 for T in range(2, T_land + 1) if tr[T - 1]["jump"]}
    plated = [e.eid for e in ents if e.kind == "core" and e.attr & 4]
    jump_y = None
    for e in ents:
        if e.kind == "core" and not (e.attr & 4):
            x0, y0, _ = e.track[min(e.track)]
            if not any(bp.in_box(x0, yy, x0, y0, 5) for yy in (bp.STAND_Y, bp.CROUCH_Y)):
                jump_y = d["jump_y"]
    hp_over = {eid: 23 for eid in plated}
    return dict(ents=ents, T_land=T_land, px=px, air_y=air_y, plated=plated, jump_y=jump_y, hp_over=hp_over,
                face0=1 if tr[T_land]["aim"] >= 5 else 0, tr=tr)


def run(stage, room, mode="fixed", beam=12000, keep=3, verbose=True, first_room=None):
    d = pickle.load(open(ROOT / "logs" / "s4t" / f"rooms_{stage}.pkl", "rb"))[room]
    res = None
    for t_rec, t_max in ((440, 430), (600, 580)):
        k = setup(d, t_rec)
        px = k["px"]
        if mode == "free" and room != 1:
            m = bp.mask_range(px - 70, px + 70)
            entry = (m, m)
        else:
            m = bp.mask_range(px, px)
            entry = (0, m) if k["face0"] else (m, 0)
        t0 = time.time()
        plans = bp.plan_room(k["ents"], k["T_land"] + 1, entry, k["air_y"], hp_over=k["hp_over"], t_max=t_max, beam=beam,
                             ntop=6, plated=k["plated"], jump_y=k["jump_y"], keep=keep, steer=mode != "nosteer")
        secs = time.time() - t0
        if plans:
            break
    if not plans:
        print(f"stage {stage} room {room} {mode}: NO PLAN")
        return None
    p = plans[0]
    t1 = time.time()
    ent = [(x, f) for f in (0, 1) for x in bp.mask_list(entry[f])]
    dpad, pos = bp.walk_rows(p.presses, k["T_land"] + 1, ent, jump_len=len(k["jump_y"]) if k["jump_y"] else 0,
                             steer=mode != "nosteer", prefer=px)
    if verbose:
        print(f"stage {stage} room {room} {mode} beam {beam} keep {keep}: finish {[q.finish for q in plans]} in {secs:.1f} s; "
              f"walk {time.time() - t1:.1f} s; recorded px {px}; entry {pos.get('entry') if dpad else None} "
              f"{'NO WALK at press ' + str(pos) if dpad is None else ''}")
        print("  ", p)
        if dpad:
            print("   positions:", [(q[0], pos[i]) for i, q in enumerate(p.presses)])
            mv = sorted(t for t, b in dpad.items() if b)
            print("   d-pad rows:", " ".join(f"{t}{dpad[t][0]}" for t in mv))
    return p.finish, secs


if __name__ == "__main__":
    stage, room = int(sys.argv[1]), int(sys.argv[2])
    mode = sys.argv[3] if len(sys.argv) > 3 else "fixed"
    beam = int(sys.argv[4]) if len(sys.argv) > 4 else 12000
    keep = int(sys.argv[5]) if len(sys.argv) > 5 else 3
    run(stage, room, mode, beam, keep)
