import sys
sys.path.insert(0, "ng/stages"); sys.path.insert(0, ".")
import a34_core as K
e = K.open_emu("a34r2_x41b.log")
try:
    e.load("ref4751/08_4-1_control")
    rows = K.load_rows("b41_pre2")
    e.trace(True); e.run(rows); tr = e.last_trace; e.trace(False)
    for i, s in enumerate(tr):
        if s["room"] == 14 or (i > 0 and tr[i-1]["room"] == 13 and s["room"] != 13):
            print(i, s["frame"], s["room"], s["x"], s["y"], hex(s["coll"]), "+".join(rows[i]))
finally:
    e.close()
