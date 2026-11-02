"""3-3 plan B: after wheel 3 (8 HP at 13792) run right to x X, turn left and throw wheel 4 at the crossing boss,
turn right, jump-slash the boss sitting right (13874-13895)."""
import sys, itertools, json, time
sys.path.insert(0, "ng/stages"); sys.path.insert(0, ".")
import a34_core as K
e = K.open_emu("a34r2_s33b.log")
res = []
try:
    e.load("ref4751/07_3-3_control")
    pre = K.load_rows("b33_pre2")[:13792 - 13741]
    e.run(pre)
    base = e.msave()
    t = time.time()
    for X, tl, trd, ja, s0, jd in itertools.product((170, 180, 190), range(13832, 13860, 4), (6, 10), range(13862, 13890, 4), (1, 3), ("A", "RA")):
        tr_ = tl + 2 + trd
        if ja <= tr_ + 1:
            continue
        L = K.Legal(pre)
        e.mload(base)
        rows = []
        f = 13793
        hits = []
        prevb = None
        kill = None
        bad = False
        reached = False
        while f < 13935:
            if f < tl:
                r = ("Right",) if not reached else ()
            elif f < tl + 2:
                r = ("Left",)
            elif f < tl + 4:
                r = ("Up", "B")
            elif tr_ <= f < tr_ + 2:
                r = ("Right",)
            elif f in (ja, ja + 1):
                r = ("A",) if jd == "A" else ("Right", "A")
            elif f >= ja + s0 and (f - ja - s0) % 5 in (0, 1):
                r = ("Down", "B")
            else:
                r = ()
            r = K.greedy_legal([r], L)[0]
            s = e.step(r, 1)
            rows.append(r)
            if s.x >= X:
                reached = True
            if s.hp == 0 or (s.dead & 0x80):
                bad = True
                break
            if prevb is not None and s.boss_real < prevb:
                hits.append((s.frame, s.boss_real))
            prevb = s.boss_real
            if s.boss_real == 0:
                kill = s.frame
                break
            f += 1
        if bad:
            continue
        res.append((kill or 99999, prevb, (X, tl, trd, ja, s0, jd), hits[-6:]))
        if kill or prevb <= 2:
            print("ok", res[-1], flush=True)
    res.sort(key=lambda r: (r[0], r[1]))
    for r in res[:12]:
        print(r, flush=True)
    print(f"{time.time() - t:.0f}s", flush=True)
    json.dump(res[:40], open("work/a34r2/s33b.json", "w"))
finally:
    e.close()
