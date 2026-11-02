import sys
sys.path.insert(0, "ng/stages"); sys.path.insert(0, ".")
import a34_core as K
P = [("Left", "A"), ("Left", "A")] + [("Right",)] * 6
e = K.open_emu("a34r2_x41c2.log")
try:
    e.load("tmp/a34r2_x/e41c_wall")
    e.trace(True); e.run(P * 14); tr = e.last_trace; e.trace(False)
    for i, s in enumerate(tr):
        print(s["frame"], i % 8, s["x"], s["y"], hex(s["coll"]), s["rflags"], s["hp"])
    e.screenshot("tmp/a34r2_x/e41c_top")
    e.save("tmp/a34r2_x/e41c_c8top")
finally:
    e.close()
