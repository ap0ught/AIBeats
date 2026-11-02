import sys
sys.path.insert(0, "ng/stages"); sys.path.insert(0, ".")
import a34_core as K
e = K.open_emu("a34r2_x43c.log")
try:
    e.load("ref4751/10_4-3_control")
    rows = K.load_rows("r2_43c_a1")
    s = e.run(rows)
    L = K.Legal(rows)
    for i in range(170):
        r = K.greedy_legal([("Right",)], L)[0]
        s = e.step(r, 1)
        if i % 5 == 0:
            print(s.frame, s.x, s.y, K.wpos(s), s.hp, hex(s.coll), s.rflags)
    e.screenshot("tmp/a34r2_x/our43c_run")
finally:
    e.close()
