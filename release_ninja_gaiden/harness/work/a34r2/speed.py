import sys, time
sys.path.insert(0, "ng/stages"); sys.path.insert(0, ".")
import a34_core as K
e = K.open_emu("a34r2_speed.log")
try:
    e.load("tmp/a34r2_x/e41c_entry2"); sid = e.msave()
    t = time.time(); e.run([()] * 600); print("600 frames run", round(time.time() - t, 2))
    t = time.time()
    for i in range(20):
        e.mload(sid); e.trace(True); e.run([()] * 60); tr = e.last_trace; e.trace(False)
    print("20x(load+60 traced)", round(time.time() - t, 2))
finally:
    e.close()
