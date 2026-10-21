"""Job (worker): replay a stage 7 segment and dump the compact trace logs/s7/<name>.trace.json (as tools/s7_trace.py).
Set S7_TRACE="<state>|<name>" in the environment, or edit DEFAULT."""
import json
import os
from pathlib import Path
from contra.inputs import read_inputs

DEFAULT = "s7/ph90|n4_ph90"
state, name = os.environ.get("S7_TRACE", DEFAULT).split("|")
ROOT = Path(r"")
rows = read_inputs(ROOT / "logs" / "s7" / f"{name}.inputs.txt")
sim.load(state)
out = []
for i in range(0, len(rows), 500):
    for f in sim.run(rows[i:i + 500]):
        out.append([f.cam, f["x"], f["y"], f["fc"], f["lagged"], f["pause"], f["barrier"], f.nbullets(),
                    len(f.enemies()), f["stop"], f["auto"], f["weapon"], f["bossdef"], f["lroutine"]])
(ROOT / "logs" / "s7" / f"{name}.trace.json").write_text(json.dumps(out), encoding="utf-8")
print("rows", len(out), "lag", sum(r[4] for r in out), "lag rows", [i for i, r in enumerate(out) if r[4]])
