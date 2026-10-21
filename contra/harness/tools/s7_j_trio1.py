"""Job: what the partial solve does at the trio of rising walls (replay from s7/part_trio)."""
import json
from pathlib import Path
from contra.stages.s7lab import line

d = json.loads(Path(r"logs\s7\part.part.json").read_text())
rows = [tuple(r) for r in d["rows"]]
i0 = 2626 - 1231
f = sim.load("s7/part_trio")
print("start", line(2626, f, (0x11,)))
tr = sim.run(rows[i0:i0 + 210])
for i, f in enumerate(tr):
    if i % 4 == 0:
        print(line(2626 + i, f, (0x11,)), "+".join(rows[i0 + i]))
