"""Stage 5 UFO experiments from a saved state (the frame the UFO is created).

    python tools/s5_ufo.py <state> grid          # scripted grid search (s5.ufo_fight2)
    python tools/s5_ufo.py <state> watch <dx> <j> <ph>   # one script, logged
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages import s5  # noqa: E402
from contra.stages.s1_common import Farm, Game, log  # noqa: E402

state, mode = sys.argv[1], sys.argv[2]
if mode == "grid":
    farm = Farm(3, name="s5_ufo")
    try:
        g = farm.g0
        g.load_file(state)
        rows = s5.ufo_fight2(farm, g, tag="s5_ufo_t")
        log("rows:", None if rows is None else len(rows), g.r.summary())
    finally:
        farm.close()
else:
    dx, j, ph = (int(x) for x in sys.argv[3:6])
    g = Game(name="s5_ufo")
    try:
        g.load_file(state)
        th = None
        tok = g.snap()
        for k in range(1, 260):
            g.step(set())
            e = s5.ufo(g.r)
            if e is not None and not (e[6] & 0x80):
                th = k
                break
        g.restore(tok)
        log("hittable after", th)
        n0 = len(g.rows)
        hp0 = 32
        # replay the script frame by frame with logging: reuse ufo_script logic through a wrapper on step
        orig = g.step

        def step(w=()):
            r = orig(w)
            e = s5.ufo(r)
            k = len(g.rows) - n0
            if e is not None and (k >= th - 30) and (k % 4 == 0 or e[3] != step.hp):
                log(f"k {k:3d} in={'+'.join(g.rows[-1]):10s} x={r.x} y={r.y} ufo x={e[4]} y={e[5]} hp {e[3]} st ${e[6]:02x} "
                    f"bullets {[(b[1], b[2]) for b in r.bullets()]} others {[(hex(o[1]), o[4], o[5]) for o in r.enemies() if o[1] not in (0x14, 0x13)]}")
            step.hp = e[3] if e else -1
            return r
        step.hp = 32
        g.step = step
        log("result:", s5.ufo_script(g, th, dx, j, ph))
    finally:
        g.close()
