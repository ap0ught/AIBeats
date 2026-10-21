"""Job: watch the B pill box (type 2) while replaying the ph90 run from its lower2 checkpoint."""
from pathlib import Path
from contra.inputs import read_inputs

ROOT = Path(r"")
rows = read_inputs(ROOT / "logs" / "s7" / "ph90.inputs.txt")
f = sim.load("s7/ph90_lower2")
print("start cam", f.cam, "wx", f.wx, "y", f["y"], "fc", f["fc"])
tr = sim.run(rows[1231:1700])
last = None
for i, f in enumerate(tr):
    for e in f.enemies():
        if e["type"] == 2:
            key = (e["hp"], e["routine"], e["state"], e["attr"])
            if key != last:
                print("row", 1231 + i, "cam", f.cam, "wx", f.wx, "y", f["y"], "fc", f["fc"], "pill", e)
                last = key
        if e["type"] == 0x15 and i % 10 == 0 and 1380 < f.wx < 1480:
            print("   row", 1231 + i, "wx", f.wx, "y", f["y"], "cart", e["x"] + f.cam, e["y"], "onen", f["onen"])
