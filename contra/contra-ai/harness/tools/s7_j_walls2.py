"""Job: trace the wall-top jumps (walls2_try) from s7/lab_step2."""
from contra.stages import s7, s7b
from contra.stages.s7lab import line

f0 = sim.load("s7/lab_step2")
r = s7.make_runner(sim, route=[], name="w2lab")
r.user["spare_walls"] = True
c = r.c
c.stop_on_death = False
base = c.snap()
for par in ((817, 12, 4), (817, 12, 3)):
    c.restore(base)
    try:
        n, top = s7b.walls2_try(r, *par, True)
        print(par, "rows", n, "top", top, "end wx", c.f.wx)
    except s7b.Fail as ex:
        print(par, "FAIL", ex)
    last = None
    for i, f in enumerate(c.tr):
        key = (f.wx, )
        if i % 3 == 0 or f.wx == last:
            print("  ", line(i, f, (0x11,)), "+".join(c.rows[i]))
        last = f.wx
    break
