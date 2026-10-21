"""Job: shoot the B pill box from the lower floor (Up+Right+B while running) at different frames; follow the item."""
from pathlib import Path
from contra.inputs import read_inputs

ROOT = Path(r"")
rows = read_inputs(ROOT / "logs" / "s7" / "ph90.inputs.txt")
sim.load("s7/ph90_lower2")
tr = sim.run(rows[1231:1476])
f = tr[-1]
print("at row 1476: cam", f.cam, "wx", f.wx, "y", f["y"], "bullets", f.nbullets())
base = sim.msave()
for d in range(0, 64, 4):
    sim.mload(base)
    seq = []
    for k in range(200):
        r = ["Right"]
        if d <= k < d + 2:
            r += ["Up", "B"]
        elif d - 3 <= k < d + 6:
            r += ["Up"]
        seq.append(tuple(r))
    tr = sim.run(seq)
    hit = None
    path = []
    got = None
    for i, f in enumerate(tr):
        for e in f.enemies():
            if e["slot"] == 15:
                if e["type"] == 2 and e["routine"] >= 4 and hit is None:
                    hit = (i, f.wx)
                if e["type"] == 0 and i % 8 == 0:
                    path.append((i, e["x"] + f.cam, e["y"], e["routine"]))
        if f["barrier"] and got is None:
            got = (i, f.wx, f["y"], f["barrier"], f["fc"])
    print(f"d {d:2d} fire at wx {tr[d].wx if d < len(tr) else None} hit {hit} got {got} end wx {tr[-1].wx} dead {any(x.dead for x in tr)}")
    if d in (8, 24, 40):
        print("    item path (frame, wx, y, routine):", path)
sim.mfree(base)
