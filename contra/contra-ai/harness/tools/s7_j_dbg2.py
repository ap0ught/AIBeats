"""Job: reproduce the repeated door fights of the c7_ph70 solve: run route_e + route_boss from its `lower4`
checkpoint and print every death the moment it happens (stop at the first death after the door fight)."""
import time
from contra.stages import s7, s6run
from contra.stages.s7lab import line

f0 = sim.load("s7/c7_ph70_lower4")
print("start", line(0, f0))
r = s7.make_runner(sim, route=s7.tag_route(s7.route_e() + s7.route_boss()), name="dbg2")
orig = s6run.Runner.repair


def spy(self, D, back, horizon, killer, depth=0):
    f = self.c.f
    after = any(m[0] == "boss_killed" for m in self.marks)
    print(f"!! death at row {D} wx {f.wx} x {f['x']} y {f['y']} fc {f['fc']} lroutine {f['lroutine']} level {f['level']} "
          f"killer {killer} step {self.route[self.i] if self.i < len(self.route) else None} after_door {after} "
          f"pstate {f['pstate']} death {f['death']} weapon {f['weapon']}", flush=True)
    if after or f.cam >= 3584:
        print("   enemies", [(hex(e['type']), e['x'], e['y'], e['hp'], e['routine']) for e in f.enemies()], flush=True)
        for i in range(max(0, len(self.c.tr) - 40), len(self.c.tr), 4):
            g = self.c.tr[i]
            print("     ", line(i, g), "lr", g["lroutine"], "+".join(self.c.rows[i]),
                  [(hex(e['type']), e['x'], e['y'], e['routine']) for e in g.enemies()][:6], flush=True)
        raise RuntimeError("death after the door")
    return orig(self, D, back, horizon, killer, depth)


s6run.Runner.repair = spy
t0 = time.time()
try:
    res = r.solve(max_deaths=20, back=110)
    print("result", res, "rows", len(r.c.rows), "seconds", round(time.time() - t0))
except RuntimeError as ex:
    print("stopped:", ex)
finally:
    s6run.Runner.repair = orig
print([(m[0], m[1]) for m in r.marks])
