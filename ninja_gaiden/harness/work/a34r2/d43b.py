import sys
sys.path.insert(0, "ng/stages"); sys.path.insert(0, ".")
import a34_core as K
C8 = [("Left", "A"), ("Left", "A")] + [("Right",)] * 6
e = K.open_emu("a34r2_d43b.log")
try:
    e.load("ref4751/10_4-3_control")
    rows0 = K.load_rows("r2_43b_entry")
    s = e.run(rows0); print("start", s.frame, s.x, s.y, hex(s.coll))
    e.save("tmp/a34r2_x/e43b_entry2")
    rows = C8 * 9 + [("Right",)] * 40
    leg = K.greedy_legal(rows, K.Legal(rows0))
    e.trace(True); e.run(leg); tr = e.last_trace; e.trace(False)
    for i, x in enumerate(tr):
        print(i, x["frame"], x["x"], x["y"], hex(x["coll"]), x["rflags"], "+".join(leg[i]))
finally:
    e.close()
