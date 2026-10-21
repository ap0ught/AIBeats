"""Job (side job, stage 6 boss): trace of the best stage 6 segment's boss fight (final_ph66, from its b_last
checkpoint at row 2873): boss position / HP / routine and Bill, every 4 rows from the reveal scroll on."""
from pathlib import Path
from contra.inputs import read_inputs

ROOT = Path(r"")
rows = read_inputs(ROOT / "logs" / "s6" / "final_ph66.inputs.txt")
sim.load("s6/final_ph66_b_last")
tr = sim.run(rows[2873:3440])
last = None
for i, f in enumerate(tr):
    b = [e for e in f.enemies() if e["type"] == 0x13 or e["hp"] > 30 and e["hp"] < 0xF0]
    key = (b[0]["hp"],) if b else None
    if i % 4 == 0 and (f["stop"] == 0xFF or f.cam > 2940):
        print(2873 + i, "cam", f.cam, "x", f["x"], "y", f["y"], "auto", f["auto"], "nb", f.nbullets(),
              "boss", [(hex(e["type"]), e["x"], e["y"], e["hp"], e["routine"], e["var1"] & 3) for e in b],
              "+".join(rows[2873 + i]))
