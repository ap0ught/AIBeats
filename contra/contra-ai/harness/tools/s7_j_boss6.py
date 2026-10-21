"""Job: why does no scripted door fight work in the c7_ph1 solve? (from s7/c7_ph1_boss_beam)"""
from contra.stages.s6ctl import Ctl
from contra.stages import s7b
from contra.stages.s7lab import line

f0 = sim.load("s7/c7_ph1_boss_beam")
print("start", line(0, f0), "cam", f0.cam, [(hex(e["type"]), e["x"], e["y"], e["hp"], e["routine"]) for e in f0.enemies()])
c = Ctl(sim, (), f0)
c.stop_on_death = False
base = c.snap()
for (j1, ph) in ((None, 0), (44, 1), (45, 2), (50, 3)):
    c.restore(base)
    try:
        n = s7b.boss_try(c, j1, ph)
        print("j1", j1, "ph", ph, "rows", n)
    except s7b.Fail as ex:
        f = c.f
        d = s7b.door_of(f)
        print("j1", j1, "ph", ph, "FAIL", ex, "after", len(c.rows), "rows; x", f["x"], "y", f["y"], "stop", f["stop"], "auto", f["auto"],
              "door", (d["x"], d["hp"]) if d else None, "enemies",
              [(hex(e["type"]), e["x"], e["y"], e["hp"], e["routine"]) for e in f.enemies()])
        for i in range(max(0, len(c.rows) - 24), len(c.rows), 4):
            g = c.tr[i]
            print("     ", i, "x", g["x"], "y", g["y"], "+".join(c.rows[i]), [(hex(e["type"]), e["x"], e["y"]) for e in g.enemies() if e["type"] in (5, 0xb, 0xf, 1)])
