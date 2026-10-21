"""Job: what kills Bill after the door's death in the c7_ph70 solve? (from s7/c7_ph70_boss_dead, holding Right)"""
from contra.stages.s7lab import line

f = sim.load("s7/c7_ph70_boss_dead")
print("start", line(0, f, (0x05, 0x16, 0x17, 0x18)))
for i in range(260):
    f = sim.run([("Right",)])[-1]
    if f.dead or i % 20 == 0:
        print(line(i, f), "lr", f["lroutine"], "en", [(hex(e["type"]), e["x"], e["y"], e["hp"], e["routine"]) for e in f.enemies()][:9])
    if f.dead:
        break
