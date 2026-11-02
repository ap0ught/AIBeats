"""4-1c hand route sweep: C8 climb x n, jump off onto the branch, jump right onto the wall top."""
import sys, itertools, json
sys.path.insert(0, "ng/stages"); sys.path.insert(0, ".")
import a34_core as K
C8 = [("Left", "A"), ("Left", "A")] + [("Right",)] * 6
e = K.open_emu("a34r2_s41c.log")
res = []
try:
    s0 = e.load("tmp/a34r2_x/e41c_wall")
    f0 = s0.frame
    pre_rows = K.load_rows("r2_41c_wall")
    base = e.msave()
    for n, c9, tail, k, w, jd in itertools.product((6, 7, 8), (0, 1), ("N", "R", "L"), (2, 4, 6, 8), (0, 2, 4, 8), ("R", "N")):
        rows = C8 * n
        if c9:
            rows = rows[:-1]          # shorter last cycle
        rows += [("Left", "A"), ("Left", "A")]
        rows += [() if tail == "N" else (("Right",) if tail == "R" else ("Left",))] * k
        rows += [()] * w
        rows += [("Right", "A")] * 2 + [("Right",)] * 50
        L = K.Legal(pre_rows)
        leg = K.greedy_legal(rows, L)
        e.mload(base)
        e.trace(True); e.run(leg); tr = e.last_trace; e.trace(False)
        top = next((i for i, s in enumerate(tr) if s["y"] == 96 and not (s["rflags"] & 4) and K.wpos(s) > 128), None)
        dead = any(s["y"] >= 248 for s in tr)
        if top is not None and not dead:
            res.append((f0 + top + 1, tr[top]["hp"], n, c9, tail, k, w, jd, len(leg)))
    res.sort()
    for r in res[:15]:
        print(r)
    json.dump(res[:50], open("work/a34r2/s41c.json", "w"))
finally:
    e.close()
