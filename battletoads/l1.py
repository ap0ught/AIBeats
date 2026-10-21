"""Level 1 with a scripted policy and a random search over its timings.

Policy (from research + our own measurements): a running headbutt kills a Psyko-Pig in one hit (15 -> 0); punches do
2. So: go to the nearest pig, headbutt it when it is in reach on the same depth line, repeat, then dash right and
dash-jump onto the ledge where the portal is (world x 304, depth 72, 64 px up). The portal despawns ~466 frames
after control, so speed is everything.

Randomized: reach distance, depth tolerance, whether to walk toward the pig or wait, the depth line to run along,
the x at which to dash-jump, and small waits. Success = the level byte leaves 1. Best = fewest frames.

    python l1.py [attempts] [scouts]    -> logs/pbeam_L1.json (same shape as a beam result, for assemble.py)
"""
import json
import random
import sys
import threading
import time

from toads.emulator import BizHawk, LOGS_DIR
from toads import tokens

PIG_IDS = {0x0B, 0x20, 0x8B, 0xA0}


def rd(r):
    tx = r[0x3FD] + 256 * ((r[0x3EE] + 128) % 256 - 128)
    pigs = [(s, r[0x3FD + s] + 256 * ((r[0x3EE + s] + 128) % 256 - 128), r[0x41B + s], r[0x51A + s])
            for s in range(2, 15) if r[0x3C1 + s] in PIG_IDS and r[0x51A + s]]
    # ram_ok: standing on the floor ($475 <= 2, height 144), or already at running speed with the run's hop
    # (height 144-176). The sky drop and real jumps are excluded. Measured: a headbutt at speed >= ~180 kills a pig;
    # one launched point-blank at speed 56 does 4 damage.
    h, z, spd = r[0x439], r[0x475], r[0x565]
    ram_ok = z <= 2 and 140 <= h <= 150            # a ground frame: the run alternates hops (z 15-30) and ground
    # level "done" = the warp routine is engaged ($23/$24 -> $E50D); the level byte itself only changes after the
    # MEGA WARP screen waits on the global timer, which can be 250 frames later
    done = (r[0x23] == 0x0D and r[0x24] == 0xE5) or r[0x10] not in (1, 0, 255)
    return tx, r[0x41B], (99 if done else r[0x10]), pigs, spd, (0 if ram_ok else 1)


class Rec:
    def __init__(self, emu):
        self.emu, self.inputs = emu, []

    def step(self, btn=(), n=1):
        self.inputs += ["+".join(btn)] * n
        return self.emu.step(btn, n)


def attempt(emu, seed):
    rng = random.Random(seed)
    reach = 0
    lo = rng.choice([32, 36, 40, 44])
    hi = rng.choice([50, 54, 58, 62])
    dash_p = rng.choice([0.5, 1.0])
    kspd = rng.choice([0.0, 0.08, 0.12, 0.16, 0.2])
    dash_min = rng.choice([100, 120, 140, 999])
    hold_dx = rng.choice([44, 48, 52, 56, 60])     # a 192 dash slides ~60 px after release: never dash into reach
    dy_tol = rng.choice([3, 4, 6])
    approach = True
    jump_x = rng.choice(range(200, 260, 4))
    turn_x = rng.choice([160, 200, 240, 280])
    use_up = True
    do_jump = True
    run_depth = rng.choice([64, 68, 70, 72, 74, 76, 80])
    settle = rng.choice([0, 2, 4, 8])
    rel = rng.choice([1, 2, 3])
    charge = rng.choice([2, 4, 6])
    order = rng.random() < 0.5
    backoff = rng.choice([0, 16, 24, 32])
    walk_cap = rng.choice([64, 96, 128, 160])
    hold_air = rng.choice([10, 20, 30, 40])
    hold_a = rng.choice([18, 20, 22, 24, 26, 30])
    order = True                        # leftmost pig first: its slide goes left, the second slide goes right toward the rock          # True: nearest pig first; False: the right-hand pig first
    emu.load("L1_go")
    rec = Rec(emu)
    f = 0
    prev_x = None
    spawn = {}                       # slot -> first seen (x, y); a pig that has not moved yet is not yet awake
    while f < 500:
        r = emu.ram_all()
        tx, ty, lvl, pigs, spd, z = rd(r)
        if lvl != 1:
            return True, rec.inputs, dict(reach=reach, dy=dy_tol, approach=approach, jump_x=jump_x, depth=run_depth, rel=rel, charge=charge, order=order, settle=settle, backoff=backoff, walk_cap=walk_cap, hold_air=hold_air, turn_x=turn_x, use_up=use_up, do_jump=do_jump, hold_a=hold_a, lo=lo, hi=hi, dash_p=dash_p, kspd=kspd, dash_min=dash_min, hold_dx=hold_dx)
        if pigs:
            for q in pigs:
                spawn.setdefault(q[0], (q[1], q[2]))
            s, px, py, hp = min(pigs, key=lambda p: p[1]) if order else min(pigs, key=lambda p: abs(p[1] - tx) + abs(p[2] - ty))
            awake = (px, py) != spawn[s]
            side = "Right" if px > tx else "Left"
            dx, dy = abs(px - tx), abs(py - ty)
            if not awake:
                # measured: headbutts on a pig that has not started walking do nothing. Take position on its
                # line at the near edge of the window and wait for it to wake.
                want = px + (hold_dx if px < tx else -hold_dx)
                h = ("Right",) if tx < want - 3 else ("Left",) if tx > want + 3 else ()
                v = ("Down",) if py > ty + 2 else ("Up",) if py < ty - 2 else ()
                rec.step(h + v, 2); f += 2
                continue
            dxe = dx - kspd * spd            # the sequence takes ~10 frames; a moving toad covers ground before B lands
            if lo <= dxe <= hi and dy <= dy_tol and z == 0:
                # measured: tap-release-tap, hold, B kills a pig when it is 40-55 px ahead on the same line,
                # whatever the toad's speed was. Too close (<25) it whiffs.
                rec.step((side,), 1); rec.step((), 1); rec.step((side,), charge); rec.step((side, "B"), 2); rec.step((side,), 6)
                f += 10 + charge
            elif dxe < lo and dy <= dy_tol:
                rec.step(("Left" if side == "Right" else "Right",), 2); f += 2      # too close: back off
            else:
                v = () if dy <= 2 else (("Down",) if py > ty else ("Up",))
                h = (side,) if dx > hi else ()
                if h and dx > dash_min and spd < 100 and z == 0 and rng.random() < dash_p:
                    rec.step(h + v, 1); rec.step(v, 1); rec.step(h + v, 4); f += 6
                else:
                    rec.step(h + v, 2); f += 2
        else:
            # arena clear: sprint right. The record warps from ground level beside the rock; what killed our earlier
            # attempts was arriving after the portal despawns (466 frames after control), not the jump.
            if prev_x is not None and tx < prev_x:          # still sliding left after a leftward headbutt: turn first
                prev_x = tx
                rec.step(("Right",), 2); f += 2
                continue
            prev_x = tx
            up = ("Up",) if (use_up and ty > run_depth) else ()
            if do_jump and tx >= jump_x and z == 0:
                # the rock top is 64 px up; a 2-frame A press jumps 40, A held 16-30 frames jumps 65-75 (measured)
                rec.step((), 1); rec.step(("Right",), 1); rec.step((), 1); rec.step(("Right", "A") + up, hold_a)
                rec.step(("Right",) + up, hold_air); f += 3 + hold_a + hold_air
            elif spd < 100 and z == 0:
                rec.step(("Right",) + up, 1); rec.step(up, 1); rec.step(("Right",) + up, 4); f += 6
            else:
                rec.step(("Right",) + up, 2); f += 2
    return False, rec.inputs, dict(reach=reach, dy=dy_tol, approach=approach, jump_x=jump_x, depth=run_depth, rel=rel, charge=charge, order=order, settle=settle, backoff=backoff, walk_cap=walk_cap, hold_air=hold_air, turn_x=turn_x, use_up=use_up, do_jump=do_jump, hold_a=hold_a, lo=lo, hi=hi, dash_p=dash_p, kspd=kspd, dash_min=dash_min, hold_dx=hold_dx)


def main(n=300, k=6):
    scouts = [BizHawk(log_name=f"l1_{i}.log") for i in range(k)]
    lock = threading.Lock()
    st = {"next": 0, "best": None, "wins": 0}
    t0 = time.time()

    def work(emu):
        while True:
            with lock:
                i = st["next"]
                if i >= n:
                    return
                st["next"] += 1
            ok, ins, params = attempt(emu, 500 + i)
            with lock:
                if ok:
                    st["wins"] += 1
                    if st["best"] is None or len(ins) < len(st["best"][0]):
                        st["best"] = (ins, params, i)
                        print(f"  attempt {i}: WARP in {len(ins)} frames {params}  ({time.time() - t0:.0f}s)", flush=True)
    th = [threading.Thread(target=work, args=(e,)) for e in scouts]
    for t in th:
        t.start()
    for t in th:
        t.join()
    for e in scouts:
        e.close()
    print(f"{st['wins']}/{n} reached the portal, {time.time() - t0:.0f}s")
    if st["best"]:
        ins, params, i = st["best"]
        (LOGS_DIR / "pbeam_L1.json").write_text(json.dumps({
            "bookmark": "L1_go", "inputs": ins, "info": params, "state": None, "history": [],
            "note": f"LEVEL 1: headbutt each pig (one hit each: measured 15 HP to 0), dash right, dash-jump to the ledge, "
                    f"into the portal. Scripted policy, timings picked by {n} random tries; attempt {i} won.||"
                    f"The portal lives 466 frames. Punching would take 8 hits a pig."}))
        print("best", len(ins), params)
    tokens.mark("L1 policy search", {"wins": st["wins"], "best": len(st["best"][0]) if st["best"] else None})


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 300, int(sys.argv[2]) if len(sys.argv) > 2 else 6)
