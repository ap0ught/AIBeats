"""Job: make s7/lab_cart (wx about 1394, cart 1424 alive) and try boarding the cart by a late jump."""
from contra.stages.s7lab import seq, show, line

base_f = sim.load("s7/ph90_lower2")
f = base_f
fired = -9
hold = 0
n = 0
while f.wx < 1392:
    row = ["Right"]
    mc = [e for e in f.enemies() if e["type"] == 0x14 and e["hp"] and e["routine"] < 5]
    if hold:
        row.append("B")
        hold -= 1
    elif mc and 0 < mc[0]["x"] - f["x"] < 24 and fired <= n - 5:
        row.append("B")
        hold = 1
        fired = n
    f = sim.run([tuple(row)])[-1]
    n += 1
sim.save("s7/lab_cart")
print("lab_cart:", line(n, f, (0x14, 0x15)))
base = sim.msave()
for jx in range(1394, 1416, 2):
    sim.mload(base)
    f = sim.state() if False else None
    tr = []
    # run to jx
    cur = None
    k = 0
    st = "run"
    log = []
    board = leave = None
    t1470 = None
    dead = False
    wx = 1392
    for i in range(140):
        if st == "run" and wx >= jx:
            st = "j1"
        if st == "j1":
            row = ("Right", "A")
            st = "j2"
        elif st == "j2":
            row = ("Right", "A")
            st = "air"
        else:
            row = ("Right",)
        f = sim.run([row])[-1]
        wx = f.wx
        if f.dead:
            dead = True
            break
        if f["onen"] and board is None:
            board = (i, f.wx, f["y"])
        if board and not f["onen"] and leave is None:
            leave = (i, f.wx, f["y"])
        if f.wx >= 1470 and t1470 is None:
            t1470 = i
            break
        if jx in (1404,) and 0 <= i < 60:
            log.append(line(i, f, (0x15,)))
    print("jx", jx, "board", board, "leave", leave, "frames to 1470", t1470, "dead" if dead else "", "wx", wx)
    for l in log:
        print("    ", l)
sim.mfree(base)
