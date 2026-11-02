import sys, itertools
sys.path.insert(0, "ng/stages"); sys.path.insert(0, ".")
import a34_core as K
P = [("Left", "A"), ("Left", "A")] + [("Right",)] * 6
e = K.open_emu("a34r2_x41c3.log")
try:
    e.load("tmp/a34r2_x/e41c_wall")
    sids = []
    for k in range(12):
        sids.append((k, e.msave(), e.state().y))
        e.run(P)
    for k, sid, y0 in sids:
        for tail in ([()] * 30, [("Left",)] * 30, [("Right",)] * 30, [("Left",)] * 4 + [("Right",)] * 26, [("Left",)] * 8 + [("Right",)] * 22):
            e.mload(sid)
            rows = [("Left", "A"), ("Left", "A")] + tail
            e.trace(True); e.run(rows); tr = e.last_trace; e.trace(False)
            land = next(((i, s["x"], s["y"], s["hp"]) for i, s in enumerate(tr) if i > 2 and not (s["rflags"] & 4) and s["coll"] in (0, 0x10, 0x1, 0x11) and s["y"] < 200), None)
            print(k, y0, tail[0], tail[-1], "land", land, "end", tr[-1]["x"], tr[-1]["y"], hex(tr[-1]["coll"]), tr[-1]["rflags"])
finally:
    e.close()
