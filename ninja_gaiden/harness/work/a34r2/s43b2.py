"""4-3b: box-face climb -> jump off onto the left ledge (y 208) -> jump onto the box top."""
import sys, itertools, json
sys.path.insert(0, "ng/stages"); sys.path.insert(0, ".")
import a34_core as K
C8 = [("Left", "A"), ("Left", "A")] + [("Right",)] * 6
e = K.open_emu("a34r2_s43b2.log")
try:
    s0 = e.load("tmp/a34r2_x/e43b_entry2"); f0 = s0.frame
    hist = K.load_rows("r2_43b_entry")
    base = e.msave()
    land = []
    for c, cut, tail, k in itertools.product((1, 2, 3), (0, 2, 4), ("N", "R", "L"), (2, 4, 6, 8, 10)):
        rows = (C8 * c)[: 8 * c - cut] + [("Left", "A")] * 2 + [() if tail == "N" else ((tail == "R" and ("Right",)) or ("Left",))] * k + [()] * 40
        leg = K.greedy_legal(rows, K.Legal(hist))
        e.mload(base); e.trace(True); e.run(leg); tr = e.last_trace; e.trace(False)
        i = next((i for i, s in enumerate(tr) if i > 3 and s["y"] == 208 and not (s["rflags"] & 4)), None)
        if i is not None and not any(s["y"] >= 248 for s in tr[:i]):
            land.append((f0 + i + 1, tr[i]["x"], c, cut, tail, k, leg[: i + 1]))
    land.sort(key=lambda r: r[0])
    print("ledge landings", [(r[0], r[1], r[2:6]) for r in land[:8]], flush=True)
    res = []
    for li, L0 in enumerate(land[:4]):
        e.mload(base); e.run(L0[6]); b2 = e.msave()
        h2 = hist + L0[6]
        for wl, jt, rd, wr in itertools.product(range(0, 20, 2), ("A", "RA", "LA"), (0, 4, 8, 12, 14, 16, 18, 20), (0, 1)):
            rows = [("Left",)] * wl + ([()] * 2 if wr else []) + [(("Right", "A") if jt == "RA" else (("Left", "A") if jt == "LA" else ("A",)))] * 2
            rows += [() if jt != "LA" else ("Left",)] * rd + [("Right",)] * 40
            leg = K.greedy_legal(rows, K.Legal(h2))
            e.mload(b2); e.trace(True); e.run(leg); tr = e.last_trace; e.trace(False)
            i = next((i for i, s in enumerate(tr) if s["y"] <= 164 and not (s["rflags"] & 4) and s["x"] >= 92), None)
            if i is not None and not any(s["y"] >= 248 for s in tr[:i]):
                res.append((L0[0] + i + 1, tr[i]["x"], tr[i]["y"], li, wl, jt, rd, wr))
                print("ok", res[-1], flush=True)
        e.mfree(b2)
    res.sort()
    for r in res[:10]:
        print(r, flush=True)
    json.dump({"land": [r[:6] for r in land[:8]], "res": res[:30]}, open("work/a34r2/s43b2.json", "w"))
finally:
    e.close()
