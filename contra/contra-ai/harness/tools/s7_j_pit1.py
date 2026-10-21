"""Job: the pit 2320..2367 and the cart 2376 with the Barrier on (from s7/n3_ph90_cart3)."""
from contra.stages.s6ctl import Ctl
from contra.stages.s7b import _fr, grounded, Fail
from contra.stages.s7lab import line

f0 = sim.load("s7/n3_ph90_cart3")
c = Ctl(sim, (), f0)
c.stop_on_death = False
print("start", line(0, f0, (0x15, 0x14)))
while c.f.wx < 2290:
    _fr(c, ("Right",))
print("at 2290:", line(len(c.rows), c.f, (0x15, 0x14, 0x06, 0x05)))
base = c.snap()
nb = len(c.rows)
for jx in (2318, 2312, 2306, 2300):
    c.restore(base)
    jumped = False
    try:
        for i in range(260):
            want = {"Right"}
            if not jumped and c.f.wx >= jx and grounded(c.f) and c.can("A"):
                want.add("A")
                jumped = True
            _fr(c, want)
            if c.f.wx >= 2470 and grounded(c.f):
                break
        print("jx", jx, "rows", len(c.rows) - nb, line(len(c.rows) - nb, c.f, (0x15,)))
    except Fail as ex:
        print("jx", jx, "FAIL", ex, line(len(c.rows) - nb, c.f, (0x15,)))
    if jx in (2318, 2306):
        for i in range(nb + 20, len(c.rows), 6):
            print("    ", line(i - nb, c.tr[i], (0x15, 0x14, 0x12, 0x10)), "+".join(c.rows[i]))
