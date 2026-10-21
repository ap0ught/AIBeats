"""Job: how early can the jump from the floor to the step 800 start (claw at 758 overhead), and where does it
land? Then: wall-top jump with no (or less) pull-back from an earlier landing."""
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
print("lab:", line(700, f, (0x10,)))
c = Ctl(sim, (), f)
c.stop_on_death = False
base = c.snap()
for jx in range(756, 770, 1):
    c.restore(base)
    try:
        while c.f.wx < jx or not grounded(c.f):
            _fr(c, ("Right",))
        _fr(c, ("Right", "A"))
        _fr(c, ("Right", "A"))
        n = 0
        while not grounded(c.f) or n < 4:
            _fr(c, ("Right",))
            n += 1
        land = (len(c.rows), c.f.wx, c.f["y"])
        out = []
        for (lf, ln) in ((12, 0), (12, 1), (12, 2), (12, 3), (12, 4)):
            sn = c.snap()
            try:
                _fr(c, ("Right", "A"))
                _fr(c, ("Right", "A"))
                air = 2
                while True:
                    air += 1
                    _fr(c, ("Left",) if lf <= air < lf + ln else ("Right",))
                    if air > 6 and grounded(c.f):
                        break
                out.append((ln, len(c.rows), c.f.wx, c.f["y"]))
            except Fail:
                out.append((ln, "dead", c.f.wx, c.f["y"]))
            c.restore(sn)
            c.free(sn)
        print("floor jump at", jx, "lands", land, "| wall-top jump at once with ln Left frames ->", out)
    except Fail as ex:
        print("floor jump at", jx, "FAIL", ex, "row", len(c.rows), "wx", c.f.wx, "y", c.f["y"])
