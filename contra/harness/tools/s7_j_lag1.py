"""Job: which enemies are alive during the lag before the trio in the scan_64 solve (start state s7/ph2)?"""
from pathlib import Path
from contra.inputs import read_inputs

ROOT = Path(r"")
rows = read_inputs(ROOT / "logs" / "s7" / "scan_64.inputs.txt")
sim.load("s7/ph2")
tr = sim.run(rows[:2500])
for k in (2500, 2540, 2580, 2620):
    tr = sim.run(rows[k:k + 40]) if k > 2500 else tr
    f = tr[-1]
    print("row", k if k > 2500 else 2500, "cam", f.cam, "wx", f.wx, "y", f["y"], "bar", f["barrier"], "nb", f.nbullets(),
          "enemies:", [(hex(e["type"]), e["x"] + f.cam, e["y"], e["hp"], e["routine"]) for e in f.enemies()])
