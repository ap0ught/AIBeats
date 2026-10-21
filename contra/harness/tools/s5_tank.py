"""Stage 5 tank experiments from a saved state (the frame a tank is created).

    python tools/s5_tank.py <state> probe [gap]      # run right until the tank is `gap` px ahead, then back off; log
    python tools/s5_tank.py <state> beam [width]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages import s5  # noqa: E402
from contra.stages.s1_common import Game, fire, log  # noqa: E402

state, mode = sys.argv[1], sys.argv[2]
g = Game(name="s5_tank")
try:
    g.load_file(state)
    if mode == "probe":
        gap = int(sys.argv[3]) if len(sys.argv) > 3 else 52
        phase = 0
        for i in range(420):
            r = g.r
            t = s5.tank(r)
            if t is None:
                w = fire(g.pad, {"Right"})
            else:
                tx = t[4]
                stopped = t[3] != 0xF0
                if phase == 0 and tx - r.x <= gap:
                    phase = 1
                if phase == 0:
                    w = fire(g.pad, {"Right"})
                elif not stopped:
                    w = {"Left"} if tx - r.x < 50 else set()
                else:
                    if r.x < tx - 46:
                        w = fire(g.pad, {"Right"})
                    else:
                        w = fire(g.pad, set())
            r = g.step(w)
            t = s5.tank(r)
            if i % 3 == 0 or r.dead or (t and t[3] not in (0xF0,) and t[3] < 71):
                log(f"row {len(g.rows):4d} in={'+'.join(g.rows[-1]):10s} scr {r.scr} x={r.x} y={r.y} tank {t[2:7] if t else None} "
                    f"$77={r.tank_scroll} fc={r.fc} lag={r.lagged} dead={r.dead} "
                    f"other={[(hex(e[1]), e[4], e[5]) for e in r.enemies() if e[1] not in (0x12, 0x13)]}")
            if r.dead or (t is None and i > 200):
                break
    elif mode == "script":
        sj = None if sys.argv[3] == "-" else int(sys.argv[3])
        sl = int(sys.argv[4])
        n0 = len(g.rows)
        orig = g.step

        def step(w=()):
            r = orig(w)
            k = len(g.rows) - n0
            if k % 4 == 0 or r.dead:
                log(f"k {k:3d} in={'+'.join(g.rows[-1]):10s} x={r.x} y={r.y} aim={r.aim} tank {s5.tank_state(r)} dead={r.dead}")
            return r
        g.step = step
        log("result:", s5.tank_script(g, sj, sl))
    elif mode == "grid":
        from contra.stages.s1_common import Farm
        g.close()
        farm = Farm(3, name="s5_tankgrid")
        try:
            g = farm.g0
            g.load_file(state)
            rows = s5.tank_fight2(farm, g, tag="s5_tank_t")
            log("rows:", None if rows is None else len(rows), g.r.summary())
        finally:
            farm.close()
        g = None
    else:
        w = int(sys.argv[3]) if len(sys.argv) > 3 else 8
        res = s5.tank_fight(g, width=w)
        log("result:", None if res is None else (len(res[0]), res[1]))
        if res:
            from contra.stages.s1_engine import beam
            log("actions:", ",".join(beam.last_hist))
finally:
    if g is not None:
        g.close()
