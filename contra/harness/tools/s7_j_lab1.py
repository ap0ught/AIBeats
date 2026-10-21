"""Job: what does ph90 do around the cart 1424, and the geometry of the B grab (hand-driven)."""
from pathlib import Path
from contra.inputs import read_inputs
from contra.stages.s7lab import seq, show, line

ROOT = Path(r"")
rows = read_inputs(ROOT / "logs" / "s7" / "ph90.inputs.txt")
sim.load("s7/ph90_lower2")
tr = sim.run(rows[1231:1380])
show(tr, every=10, types=(0x14, 0x15, 0x10), start=1231)
sim.save("s7/lab_pre_cart")          # row 1380, wx about 1386
tr = sim.run(rows[1380:1520])
show(tr, every=4, types=(0x14, 0x15, 0x02, 0x05), start=1380)
print("inputs 1380..1520:", ["+".join(r) for r in rows[1380:1520]])
