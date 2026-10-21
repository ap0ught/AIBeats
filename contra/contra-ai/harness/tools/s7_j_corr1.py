"""Job: why does every claw-corridor plan die in the scan_144 solve? (from s7/scan_144_lower2)"""
from contra.stages.s6ctl import Ctl
from contra.stages import s7b
from contra.stages.s7lab import line

f0 = sim.load("s7/scan_144_lower2")
print("start", line(0, f0), [(hex(e["type"]), e["x"] + f0.cam, e["y"], e["hp"], e["routine"]) for e in f0.enemies()])
c = Ctl(sim, (), f0)
c.stop_on_death = False
base = c.snap()
for (w0, kill) in ((0, ()), (20, ()), (0, (0x60,)), (40, ())):
    c.restore(base)
    try:
        n = s7b.corridor_try(c, 1392, w0, kill)
        print("plan", w0, kill, "ok rows", n)
    except s7b.Fail as ex:
        f = c.f
        print("plan", w0, kill, "FAIL", ex, "at row", len(c.rows), line(len(c.rows), f),
              "enemies", [(hex(e["type"]), e["x"] + f.cam, e["y"], e["hp"], e["routine"]) for e in f.enemies()])
