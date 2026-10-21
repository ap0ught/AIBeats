"""Job: can the two rising walls on the step be shot down while running (aim down-forward)? HP timelines."""
from pathlib import Path
from contra.inputs import read_inputs
from contra.stages.s6ctl import Ctl
from contra.stages.s7b import _fr, grounded, Fail
from contra.stages.s7lab import line

ROOT = Path(r"")
rows = read_inputs(ROOT / "logs" / "s7" / "ph90.inputs.txt")
sim.load("s7/ph90_cart1")
tr = sim.run(rows[581:700])
f = tr[-1]
c = Ctl(sim, (), f)
c.stop_on_death = False
while c.f.wx < 762 or not grounded(c.f):
    _fr(c, ("Right",))
base = c.snap()
nb = len(c.rows)


def walls(f):
    out = {}
    for e in f.enemies():
        if e["type"] == 0x11:
            out[e["x"] + f.cam] = (e["hp"], e["routine"])
    return out


for name, aim_air, aim_gnd, stop in (("fwd/fwd", (), (), None), ("down/down", ("Down",), ("Down",), None),
                                     ("fwd air, down ground", (), ("Down",), None),
                                     ("down, stop at 836", ("Down",), ("Down",), 836),
                                     ("fwd, stop at 836", (), (), 836),
                                     ("down, stop at 820", ("Down",), ("Down",), 820)):
    for ph in (0, 2):
        c.restore(base)
        t = 0
        hist = []
        try:
            _fr(c, ("Right", "A"))
            _fr(c, ("Right", "A"))
            while t < 170:
                g = grounded(c.f)
                want = set()
                if stop is None or c.f.wx < stop or not g:
                    want.add("Right")
                if t % 5 == ph and c.can("B"):
                    want.add("B")
                want.update(aim_gnd if g else aim_air)
                if "Right" not in want and "Down" in want:
                    want.discard("Down")          # standing: Down alone would be prone
                _fr(c, want)
                t += 1
                w = walls(c.f)
                if t % 10 == 0:
                    hist.append((t, c.f.wx, w.get(852, ("-",))[0], w.get(884, ("-",))[0]))
            print(name, "ph", ph, "survived; (t, wx, hp1, hp2):", hist)
        except Fail as ex:
            print(name, "ph", ph, "DEAD at t", t, "wx", c.f.wx, "y", c.f["y"], "(t, wx, hp1, hp2):", hist)
