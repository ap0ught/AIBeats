"""3-3: wheel 4 early at the left-sitting boss, run right, jump-slash the boss when it sits right (13874-13895)."""
import sys, itertools, json, time
sys.path.insert(0, "ng/stages"); sys.path.insert(0, ".")
import a34_core as K
e = K.open_emu("a34r2_s33.log")
res = []
try:
    e.load("ref4751/07_3-3_control")
    pre_all = K.load_rows("b33_pre2")
    n0 = 13792 - 13741
    pre = pre_all[:n0]
    e.run(pre)
    base = e.msave()
    t = time.time()
    for t4, ja, s0, jd, rs in itertools.product(range(13793, 13813, 2), range(13856, 13892, 2), (1, 2, 3), ("A", "RA"), (0, 4)):
        rows = {}
        f = 13793
        for g in range(13793, t4):
            rows[g] = ()
        rows[t4] = ("Up", "B"); rows[t4 + 1] = ("Up", "B")
        for g in range(t4 + 2 + rs, ja):
            rows[g] = ("Right",)
        jr = ("A",) if jd == "A" else ("Right", "A")
        rows[ja] = jr; rows[ja + 1] = jr
        g = ja + s0
        while g < 13930:
            rows[g] = ("Down", "B"); rows[g + 1] = ("Down", "B")
            g += 5
        seq = [rows.get(g, ()) for g in range(13793, 13930)]
        L = K.Legal(pre)
        leg = K.greedy_legal(seq, L)
        e.mload(base)
        e.trace(True); e.run(leg); tr = e.last_trace; e.trace(False)
        kill = next((x["frame"] for x in tr if x["boss_real"] == 0), None)
        bad = any(x["hp"] == 0 or (x["dead"] & 0x80) for x in tr)
        left = min(x["boss_real"] for x in tr)
        if not bad:
            res.append((kill or 99999, left, (t4, ja, s0, jd, rs)))
            if kill or left <= 2: print("ok", res[-1], flush=True)
    res.sort()
    for r in res[:15]:
        print(r, flush=True)
    print(f"{time.time() - t:.0f}s", flush=True)
    json.dump(res[:60], open("work/a34r2/s33.json", "w"))
finally:
    e.close()
