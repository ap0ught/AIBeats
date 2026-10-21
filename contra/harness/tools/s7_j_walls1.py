"""Job: the two rising walls on the step (852, 884): one jump over both? Where does a plain jump die / land."""
from pathlib import Path
from contra.inputs import read_inputs
from contra.stages.s7lab import line

ROOT = Path(r"")
rows = read_inputs(ROOT / "logs" / "s7" / "ph90.inputs.txt")
sim.load("s7/ph90_cart1")
tr = sim.run(rows[581:764])
f = tr[-1]
print("lab state:", line(764, f, (0x11,)))
sim.save("s7/lab_step2")
base = sim.msave()
for jx in range(812, 846, 2):
    sim.mload(base)
    wx = f.wx
    st = "run"
    res = None
    for i in range(200):
        if st == "run" and wx >= jx:
            row = ("Right", "A")
            st = "j2"
            j = i
        elif st == "j2":
            row = ("Right", "A")
            st = "air"
        else:
            row = ("Right",)
        g = sim.run([row])[-1]
        wx = g.wx
        walls = [(e["x"] + g.cam, e["y"], e["frame"], e["routine"]) for e in g.enemies() if e["type"] == 0x11]
        if g.dead:
            res = ("DEAD", i, g.wx, g["y"], walls)
            break
        if st == "air" and i > j + 4 and (g["jump"] & 15) == 0 and g["fall"] == 0:
            res = ("land", i, g.wx, g["y"], walls)
            break
    print("jx", jx, res)
sim.mfree(base)
