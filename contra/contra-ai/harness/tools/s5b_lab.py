"""Second-pass lab for stage 5 (tanks, UFO). Experiments only; nothing here is part of a run.

    python tools/s5b_lab.py trace_tank <state> [sj sl]
    python tools/s5b_lab.py tank2 <state> <grid name>
    python tools/s5b_lab.py tank2one <state> sj sl hj xs [trace]
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages import s5  # noqa: E402
from contra.stages.s1_common import Farm, Game, Pad, fire, log  # noqa: E402


def tline(g, k):
    r = g.r
    st, x, hp = s5.tank_state(r)
    e = s5.tank(r)
    bl = [(b[1], b[2], b[3]) for b in r.bullets()]
    return (f"k={k:3d} fc={r.fc:3d} sub={r.m[0x94]:02x} scr={r.scr} bx={r.x:3d} by={r.y:3d} jmp={r.m[0xA0]:02x} aim={r.aim} tank={st[:4]} tx={x:3d} hp={hp:3d} "
            f"st=${(e[6] if e else 0):02x} rt={(e[2] if e else 0)} ts={r.tank_scroll} row={'+'.join(g.rows[-1]) if g.rows else ''} "
            f"nb={len(bl)} {bl[:10]}")


def trace_tank(state, sj=None, sl=88):
    g = Game(name="s5b_lab")
    try:
        g.load_file(state)
        n0 = len(g.rows)
        print(tline(g, 0))
        orig = g.step

        def step(w=()):
            r = orig(w)
            print(tline(g, len(g.rows) - n0))
            return r
        g.step = step
        n = s5.tank_script(g, sj, sl)
        print("rows", n)
        for _ in range(60):
            g.step({"Right"})
    finally:
        g.close()


def tank2_eval(g, state, job, trace=False):
    from contra.stages.s5 import tank_script2
    g.load_file(state)
    scr0 = g.r.scr
    n0 = len(g.rows)
    if trace:
        orig = g.step

        def step(w=()):
            r = orig(w)
            print(tline(g, len(g.rows) - n0))
            return r
        g.step = step
    try:
        n = tank_script2(g, *job)
        if n is None:
            return None
        k = n
        if len(job) > 7 and job[7] is not None:
            return (k, n)
        while g.r.scr < scr0 + 145 + 60 and k < 400:
            g.step({"Right"})
            k += 1
            if g.r.dead:
                return None
        return (k, n)
    finally:
        if trace:
            del g.step


def tank2(state, grid):
    jobs = []
    if grid == "kill":
        jobs = [(None, 0, hj, dl, yf, xk) for hj in range(27, 37) for dl in (0, 1, 2) for yf in (114, 116) for xk in (112, 113, 114)]
    elif grid == "kill2":
        jobs = [(61, 91, hj, dl, yf, 112) for hj in range(26, 40) for dl in (0, 1, 2) for yf in (114, 116)]
    elif grid == "jump":
        jobs = [(sj, sj + d, 0, 0, 114, 112, 330, 40) for sj in range(58, 72) for d in range(24, 36)]
    t0 = time.time()
    with Farm(3, name="s5b_lab") as farm:
        res = farm.map(lambda g, job: tank2_eval(g, state, job), jobs)
    ok = sorted((r, j) for r, j in zip(res, jobs) if r is not None)
    print(f"{len(ok)}/{len(jobs)} survive, {time.time() - t0:.0f} s")
    for r, j in ok[:25]:
        print(r, j)


def uline(g, k):
    r = g.r
    e = s5.ufo(r)
    bl = [(b[0], b[1], b[2], b[3]) for b in r.bullets()]
    en = [(x[0], x[1], x[4], x[5]) for x in r.enemies() if x[1] != 0x14]
    return (f"k={k:3d} fc={r.fc:3d} sub={r.m[0x94]:02x} bx={r.x:3d} by={r.y:3d} jmp={r.m[0xA0]:02x} aim={r.aim} "
            f"ufo=({e[4]},{e[5]}) hp={e[3]} st=${e[6]:02x} rt={e[2]} " if e else f"k={k} no ufo bossdef={r.bossdef} ") +            f"row={'+'.join(g.rows[-1]) if g.rows else ''} nb={len(bl)} {bl} en={en}"


def ufo_trace(state, job):
    g = Game(name="s5b_lab")
    try:
        g.load_file(state)
        n0 = len(g.rows)
        orig = g.step

        def step(w=()):
            r = orig(w)
            print(uline(g, len(g.rows) - n0))
            return r
        g.step = step
        print(s5.ufo_script(g, 102, *job))
    finally:
        g.close()


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "trace_tank":
        trace_tank(a[1], None if len(a) < 3 or a[2] == "None" else int(a[2]), int(a[3]) if len(a) > 3 else 88)
    elif a[0] == "tank2":
        tank2(a[1], a[2])
    elif a[0] == "tank2one":
        g = Game(name="s5b_lab")
        try:
            job = tuple(None if x == "None" else int(x) for x in a[2:] if x != "trace")
            print(tank2_eval(g, a[1], job, trace="trace" in a))
        finally:
            g.close()
    elif a[0] == "ufo_trace":
        ufo_trace(a[1], tuple(int(x) for x in a[2:6]))
    elif a[0] == "ufo3":
        with Farm(3, name="s5b_lab") as farm:
            t0 = time.time()
            farm.g0.load_file(a[1])
            rows = s5.ufo_fight3(farm, farm.g0)
            print("rows", None if rows is None else len(rows), f"{time.time() - t0:.0f} s")
    elif a[0] == "ufo4":
        with Farm(3, name="s5b_lab") as farm:
            t0 = time.time()
            farm.g0.load_file(a[1])
            rows = s5.ufo_fight4(farm, farm.g0)
            print("rows", None if rows is None else len(rows), f"{time.time() - t0:.0f} s")
    elif a[0] == "ufo3t":
        g = Game(name="s5b_lab")
        try:
            g.load_file(a[1])
            n = s5.ufo_script3(g, 102, *[int(x) for x in a[2:]])
            rows = list(g.rows)
            print("rows", n)
            g.load_file(a[1])
            for i, row in enumerate(rows):
                r = g.step_raw(row)
                e = s5.ufo(r)
                if i >= 60:
                    print(f"k={i+1:3d} by={r.y:3d} hp={e[3] if e else -1:2d} nb={r.nbullets():2d} {'+'.join(row):8s} "
                          f"{[(b[0], b[1], b[2], b[3]) for b in r.bullets()]} en={[(x[0], x[1], x[4], x[5]) for x in r.enemies() if x[1] != 0x14]}")
        finally:
            g.close()
    elif a[0] == "tank3":
        with Farm(3, name="s5b_lab") as farm:
            t0 = time.time()
            g = farm.g0
            g.load_file(a[1])
            scr0 = g.r.scr
            rows = s5.tank_fight3(farm, g)
            n = None if rows is None else len(rows)
            k = n
            while rows is not None and g.r.scr < scr0 + 205:
                g.step({"Right"})
                k += 1
            print("rows to dead", n, "rows to scroll +60", k, f"{time.time() - t0:.0f} s")
