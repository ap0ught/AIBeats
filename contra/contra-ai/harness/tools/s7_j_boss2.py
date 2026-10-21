"""Job: scripted door fights with an early first jump and a second jump at landing."""
from contra.stages.s6ctl import Ctl
from contra.stages import s7b

f0 = sim.load("s7/ph90_boss_beam")
c = Ctl(sim, (), f0)
c.stop_on_death = False
base = c.snap()
res = []
for j1 in (6, 10, 14, 18, 22, 26, 30, 34):
    for (j2, band, ab) in ((120, (112, 144), "Down"), (120, (112, 150), ""), (120, (104, 150), "Down")):
        line = []
        for ph in range(5):
            c.restore(base)
            try:
                n = s7b.boss_try(c, j1, ph, j2, band, ab)
                line.append(n)
                res.append((n, j1, ph, j2, band, ab))
            except s7b.Fail as ex:
                line.append(str(ex)[:6])
        print("j1", j1, "j2", j2, band, repr(ab), line)
res.sort()
print("best", res[:5])
