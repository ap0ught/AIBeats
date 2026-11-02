import sys
sys.path.insert(0, "ng/stages"); sys.path.insert(0, ".")
import a34_core as K
e = K.open_emu("a34r2_x42.log")
try:
    e.load("ref4751/09_4-2_control")
    T = K.tas_rows()
    e.run(T[16682:18290]); e.screenshot("tmp/a34r2_x/tas42_18290")
    e.load("ref4751/09_4-2_control")
    rows = K.load_rows("r2_42_astar1")
    s = e.run(rows); e.screenshot("tmp/a34r2_x/our42_18254")
    L = K.Legal(rows)
    for i in range(40):
        r = K.greedy_legal([("Right",)], L)[0]
        s = e.step(r, 1)
        if i % 4 == 3:
            print(s.frame, s.x, s.y, K.wpos(s), s.hp, hex(s.coll))
    e.screenshot("tmp/a34r2_x/our42_18294")
finally:
    e.close()
