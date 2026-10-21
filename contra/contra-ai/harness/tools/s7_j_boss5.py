"""Job: door fight with the hover option (from s7/n4_ph90_boss_beam; n4's fight took 175 rows)."""
from contra.stages.s6ctl import Ctl
from contra.stages import s7b

f0 = sim.load("s7/n4_ph90_boss_beam")
c = Ctl(sim, (), f0)
c.stop_on_death = False
base = c.snap()
res = []
for j1 in (None, 43, 45, 47):
    for hover in (None, 152, 156, 160, 164, 168, 172):
        line = []
        for ph in range(5):
            c.restore(base)
            try:
                n = s7b.boss_try(c, j1, ph, None, hover=hover)
                line.append(n)
                res.append((n, str(j1), ph, str(hover)))
            except s7b.Fail as ex:
                line.append(str(ex)[:6])
        print("j1", j1, "hover", hover, line)
res.sort()
print("best", res[:6])
