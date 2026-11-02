"""4-3b entry probe: python work/a34r2/x43b.py"""
import sys, itertools
sys.path.insert(0, "ng/stages"); sys.path.insert(0, ".")
import a34_core as K
e = K.open_emu("a34r2_x43b.log")
try:
    e.load("ref4751/10_4-3_control")
    pre = K.load_rows("b43_pre")
    s = e.run(pre)
    print("after pre", s.frame, s.room, s.x, s.y, s.coll)
    n = 0
    while True:
        s = e.step((), 1); n += 1
        if s.room == 18 and n > 3 and s.y > 200:
            break
    for i in range(30):
        s = e.step((), 1)
        print(s.frame, s.room, s.x, s.y, hex(s.coll), s.rflags, s.anim)
        if s.get("gm", 1) and i > 25: break
    e.screenshot("tmp/a34r2_x/e43b_entry")
    e.save("tmp/a34r2_x/e43b_entry")
    sid = e.msave()
    P = {"L": [("Left",)], "R": [("Right",)], "LA": [("Left", "A")], "RA": [("Right", "A")], "A": [("A",)]}
    for a, b in itertools.product(P, P):
        e.mload(sid)
        rows = P[a] * 6 + [()] * 3 + P[b] * 6 + [()] * 3
        L = K.Legal(); leg = K.greedy_legal(rows * 3, L)
        e.trace(True); e.run(leg); tr = e.last_trace; e.trace(False)
        print(a, b, [(t["x"], t["y"], hex(t["coll"])) for t in tr[::6]])
finally:
    e.close()
