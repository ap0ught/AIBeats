"""Job: trio_try grid from the s7/part_alley checkpoint (Barrier on, as in the partial solve)."""
from contra.stages.s6ctl import Ctl
from contra.stages import s7b
from contra.stages.s7b import _fr, grounded, Fail
from contra.stages.s7lab import line

f0 = sim.load("s7/part_alley")
c = Ctl(sim, (), f0)
c.stop_on_death = False
while c.f.wx < 2562 or not grounded(c.f) or not c.can("A"):
    _fr(c, ("Right",))
_fr(c, ("Right", "A"))
_fr(c, ("Right", "A"))
n = 0
while not grounded(c.f) or n < 3:
    _fr(c, ("Right",))
    n += 1
print("on the step:", line(len(c.rows), c.f), "(row", 2347 + len(c.rows), ")")
base = c.snap()
nb = len(c.rows)
out = []
for jx in (2612, 2618):
    for stop_d in (17, 22, 27, 32, 38, 44):
        row = []
        for phase in range(5):
            c.restore(base)
            try:
                n = s7b.trio_try(c, 2800, phase, jx, stop_d)
                row.append(n)
                out.append((n, jx, phase, stop_d, c.f.wx))
            except Fail as ex:
                row.append(str(ex)[:8] + f"@{c.f.wx}")
        print("jx", jx, "stop_d", stop_d, row)
out.sort()
print("best", out[:4], "(walking: ", 2800 - base["f"].wx, "rows)")
