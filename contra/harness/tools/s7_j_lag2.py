"""Job: replay the trio64 partial solve (from s7/scan_64_alley) and show where the lag frames are."""
import json
from pathlib import Path

d = json.loads(Path(r"logs\s7\trio64.part.json").read_text())
rows = [tuple(r) for r in d["rows"]]
sim.load("s7/scan_64_alley")
tr = sim.run(rows)
lagrows = [i for i, f in enumerate(tr) if f["lagged"]]
print("lag rows", lagrows)
for i in range(0, len(tr), 12):
    f = tr[i]
    types = {}
    for e in f.enemies():
        types[e["type"]] = types.get(e["type"], 0) + 1
    print(i, "wx", f.wx, "y", f["y"], "nb", f.nbullets(), "enemies", sum(types.values()), dict(sorted(types.items())),
          "lag in next 12:", sum(g["lagged"] for g in tr[i:i + 12]))
