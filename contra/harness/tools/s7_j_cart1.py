"""Job: first cart (624): walk off the step at 608 versus a jump from the step that lands on the cart's rear edge."""
from pathlib import Path
from contra.inputs import read_inputs
from contra.stages.s7lab import line

ROOT = Path(r"")
rows = read_inputs(ROOT / "logs" / "s7" / "ph90.inputs.txt")
sim.load("s7/ph90")
tr = sim.run(rows[:470])
f = tr[-1]
print("lab state:", line(470, f, (0x15,)))
sim.save("s7/lab_step1")
base = sim.msave()
for jx in [None] + list(range(530, 566, 2)):
    sim.mload(base)
    wx = f.wx
    st = "run"
    board = leave = None
    t = None
    dead = False
    for i in range(260):
        if st == "run" and jx is not None and wx >= jx:
            row = ("Right", "A")
            st = "j2"
        elif st == "j2":
            row = ("Right", "A")
            st = "air"
        else:
            row = ("Right",)
        g = sim.run([row])[-1]
        wx = g.wx
        if g.dead:
            dead = True
            break
        if g["onen"] and board is None:
            board = (i, g.wx)
        if board and not g["onen"] and leave is None:
            leave = (i, g.wx)
        if g.wx >= 700:
            t = i
            break
    print("jx", jx, "board", board, "leave", leave, "frames to wx 700:", t, "DEAD" if dead else "")
sim.mfree(base)
