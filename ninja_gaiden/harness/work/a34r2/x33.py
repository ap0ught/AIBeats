import sys
sys.path.insert(0, "ng/stages"); sys.path.insert(0, ".")
import a34_core as K
e = K.open_emu("a34r2_x33.log")
try:
    e.load("ref4751/07_3-3_control")
    rows = K.load_rows("b33_pre2")
    e.trace(True); e.run(rows); tr = e.last_trace; e.trace(False)
    for i, s in enumerate(tr):
        if s["frame"] >= 13788:
            print(s["frame"], "ryu", s["x"], s["y"], "hp", s["hp"], "ninpo", s["ninpo"], "boss", s["boss_real"], "row", "+".join(rows[i]))
    e.load("ref4751/07_3-3_control")
    for i, r in enumerate(rows):
        e.step(r, 1)
        f = 13742 + i
        if f >= 13790 and f % 2 == 0:
            rb = e.ram(0x400, 0xC0)
            print("  B", f, "bx", rb[0x67], "by", rb[0x87], "id", rb[0x7], "proj", [(rb[j], rb[0x60+j], rb[0x80+j]) for j in range(7) if rb[j]])
finally:
    e.close()
