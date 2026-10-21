"""Job: cart 1824 with the Barrier: walk off the ledge at 1792 versus jumps from the ledge (from s7/part_bgrab)."""
from contra.stages.s6ctl import Ctl
from contra.stages.s7b import _fr, grounded, Fail
from contra.stages.s7lab import line

f0 = sim.load("s7/part_bgrab")
c = Ctl(sim, (), f0)
c.stop_on_death = False
print("start", line(0, f0, (0x15,)))


def jump_at(c, x):
    while c.f.wx < x or not grounded(c.f) or not c.can("A"):
        _fr(c, ("Right",))
    _fr(c, ("Right", "A"))
    _fr(c, ("Right", "A"))
    n = 0
    while not grounded(c.f) or n < 3:
        _fr(c, ("Right",))
        n += 1


jump_at(c, 1596)
print("after jump 1:", line(len(c.rows), c.f))
jump_at(c, 1652)
print("after jump 2:", line(len(c.rows), c.f, (0x15, 0x10)))
base = c.snap()
n_base = len(c.rows)
for jx in [None] + list(range(1736, 1792, 2)):
    c.restore(base)
    board = leave = None
    t = None
    try:
        jumped = False
        for i in range(400):
            want = {"Right"}
            if jx is not None and not jumped and c.f.wx >= jx and grounded(c.f) and c.can("A"):
                want.add("A")
                jumped = True
            _fr(c, want)
            if c.f["onen"] and board is None:
                board = (len(c.rows) - n_base, c.f.wx)
            if board and not c.f["onen"] and leave is None:
                leave = (len(c.rows) - n_base, c.f.wx)
            if c.f.wx >= 1920 and grounded(c.f):
                t = len(c.rows) - n_base
                break
        print("jx", jx, "board", board, "leave", leave, "rows to wx 1920:", t, "y", c.f["y"])
    except Fail as ex:
        print("jx", jx, "FAIL", ex, "wx", c.f.wx, "y", c.f["y"])
