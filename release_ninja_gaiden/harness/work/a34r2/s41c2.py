"""4-1c hand route sweep v2 from the room-15 floor state: C8 x n, jump off (L+A,L+A + tail), wait w, jump right."""
import sys, itertools, json
sys.path.insert(0, "ng/stages"); sys.path.insert(0, ".")
import a34_core as K
state, rows_name = sys.argv[1], sys.argv[2]
C8 = [("Left", "A"), ("Left", "A")] + [("Right",)] * 6
e = K.open_emu("a34r2_s41c2.log")
res = []
try:
    s0 = e.load(state); f0 = s0.frame
    hist = K.load_rows(rows_name)
    base = e.msave()
    for pre_r, n, cut, tail, k, w in itertools.product((0, 1), (7,), (0, 1, 2), ("N", "L"), (4, 6, 8, 10), range(0, 14, 2)):
        rows = [("Right",)] * pre_r
        rows += C8 * n
        rows = rows[:len(rows) - cut]
        rows += [("Left", "A"), ("Left", "A")]
        rows += [() if tail == "N" else (("Right",) if tail == "R" else ("Left",))] * k
        rows += [()] * w
        rows += [("Right", "A")] * 2 + [("Right",)] * 45
        L = K.Legal(hist)
        leg = K.greedy_legal(rows, L)
        e.mload(base)
        e.trace(True); e.run(leg); tr = e.last_trace; e.trace(False)
        top = next((i for i, s in enumerate(tr) if s["y"] == 96 and not (s["rflags"] & 4) and K.wpos(s) > 128), None)
        if top is None:
            continue
        dead = any(s["y"] >= 248 for s in tr)
        # progress score: wpos at the end of the trace (all end with Right held)
        endw = K.wpos(tr[-1])
        if not dead:
            res.append((f0 + top + 1, -endw, tr[top]["hp"], (pre_r, n, cut, tail, k, w), len(leg))); print('ok', res[-1], flush=True)
    res.sort()
    for r in res[:15]:
        print(r, flush=True)
    json.dump(res[:60], open("work/a34r2/s41c2.json", "w"))
finally:
    e.close()
