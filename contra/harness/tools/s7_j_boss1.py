"""Job: trace of the ph90 boss fight (from its boss_beam checkpoint, row 3738)."""
from pathlib import Path
from contra.inputs import read_inputs

ROOT = Path(r"")
rows = read_inputs(ROOT / "logs" / "s7" / "ph90.inputs.txt")
sim.load("s7/ph90_boss_beam")
tr = sim.run(rows[3738:3945])
for i, f in enumerate(tr):
    d = [e for e in f.enemies() if e["type"] == 0x16]
    if i % 4 == 0 or (d and i > 0 and d[0]["hp"] != dprev):
        print(3738 + i, "cam", f.cam, "x", f["x"], "y", f["y"], "stop", f["stop"], "auto", f["auto"], "nb", f.nbullets(),
              "door", (d[0]["x"], d[0]["y"], d[0]["hp"], d[0]["routine"]) if d else None, "+".join(rows[3738 + i]),
              "en", [(e["type"], e["x"], e["y"]) for e in f.enemies() if e["type"] not in (0x16,)])
    dprev = d[0]["hp"] if d else None
