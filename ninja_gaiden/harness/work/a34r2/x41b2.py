import sys
sys.path.insert(0, "ng/stages"); sys.path.insert(0, ".")
import a34_core as K
C8 = [("Left", "A"), ("Left", "A")] + [("Right",)] * 6
e = K.open_emu("a34r2_x41b2.log")
try:
    e.load("ref4751/08_4-1_control")
    rows = K.load_rows("r2_41b_entry")
    s = e.run(rows)
    for skip in (0,):
        L = K.Legal(rows)
        i = 0
        while s.room == 14 and i < 400:
            r = C8[i % 8]
            r = K.greedy_legal([r], L)[0]
            s = e.step(r, 1); rows.append(r); i += 1
        print("room 15 at", s.frame, "TAS 16107 ->", s.frame - 16107, "y", s.y)
        # stop pressing; wait to the floor of room 15 (keep legal: release)
        while not (s.room == 15 and s.y >= 230):
            r = K.greedy_legal([()], L)[0]
            s = e.step(r, 1); rows.append(r)
        print("room 15 floor at", s.frame, s.x, s.y, hex(s.coll))
        K.save_rows("r2_41c_entry2", rows, "4-1: b41_pre2 to the shaft bottom + C8 single-wall climb; room 15 floor")
        e.save("tmp/a34r2_x/e41c_entry2")
finally:
    e.close()
