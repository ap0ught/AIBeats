"""Job: from the top of wall 1, can the second jump reach the ledge 928 directly (no landing on the step)?"""
from contra.stages.s6ctl import Ctl
from contra.stages.s7b import _fr, grounded, Fail
from contra.stages.s7lab import line

f0 = sim.load("s7/lab_step2")
c = Ctl(sim, (), f0)
c.stop_on_death = False
base = c.snap()
for (lf, ln) in ((12, 4), (12, 3), (12, 2), (13, 3), (14, 2), (20, 3), (30, 3), (40, 3)):
    for e in (0, 1, 2, 3, 4, 5, 6, 8):
        c.restore(base)
        try:
            while not (grounded(c.f) and c.f["y"] == 164 and c.f.wx >= 817):
                _fr(c, ("Right",))
            _fr(c, ("Right", "A"))
            _fr(c, ("Right", "A"))
            air = 2
            while True:
                air += 1
                _fr(c, ("Left",) if lf <= air < lf + ln else ("Right",))
                if air > 6 and grounded(c.f):
                    break
            top = (len(c.rows), c.f.wx, c.f["y"])
            if c.f["y"] != 132:
                print("lf", lf, "ln", ln, "landed", top)
                break
            for _ in range(e):
                _fr(c, ("Right",))
            if not grounded(c.f):
                print("lf", lf, "ln", ln, "top", top, "extra", e, "fell off at", c.f.wx)
                continue
            j2 = (len(c.rows), c.f.wx)
            _fr(c, ("Right", "A"))
            _fr(c, ("Right", "A"))
            n = 0
            while not grounded(c.f) or n < 4:
                _fr(c, ("Right",))
                n += 1
            land = (len(c.rows), c.f.wx, c.f["y"])
            while c.f.wx < 959 and c.f["y"] == 132:
                _fr(c, ("Right",))
            print("lf", lf, "ln", ln, "top", top, "extra", e, "jump2", j2, "land", land, "row at 959:", len(c.rows) if c.f["y"] == 132 else None)
        except Fail as ex:
            print("lf", lf, "ln", ln, "extra", e, "FAIL", ex, "row", len(c.rows), "wx", c.f.wx, "y", c.f["y"])
