"""Job: trace the B grab (k=28) from the second jump on."""
from contra.stages.s6ctl import Ctl
from contra.stages import s7b
from contra.stages.s7lab import line

f0 = sim.load("s7/lab_cart")
c = Ctl(sim, (), f0)
c.stop_on_death = False
base = c.snap()
log = []
res = s7b.bgrab_try(c, 28, 0, 33, log=log)
print(res)
for i, f in enumerate(log):
    if i >= 92:
        print("   ", line(i, f, (0x02, 0x00)), "+".join(c.rows[i]))
