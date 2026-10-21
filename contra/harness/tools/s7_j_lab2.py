"""Job: make a lab state just before the cart at 1424 with the cart intact (no shooting), from ph90_lower2."""
from contra.stages import s7
from contra.stages.s6run import Run, Mark
from contra.stages.s7lab import seq, show, line

f0 = sim.load("s7/ph90_lower2")
r = s7.make_runner(sim, route=s7.tag_route([Run(1396), Mark("x")]), name="lab2")
r.aim_mode = "off"
res = r.solve(max_deaths=40, back=110)
c = r.c
print(res, "rows", len(c.rows), "wx", c.f.wx, "y", c.f["y"], "fc", c.f["fc"], "remedies", r.remedies, "local", r.local_fixes)
print(line(len(c.rows), c.f, (0x14, 0x15, 0x02)))
sim.save("s7/lab_cart")
print("rows:", " ".join("+".join(x) or "-" for x in c.rows))
