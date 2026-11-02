"""3-3 plan D: from 13792 (8 HP, wheel 3 done) run right to X1, turn left, throw wheel 4 at the take-off (tt),
run right to X2, jump-slash the boss as it sits right / takes off."""
import sys, itertools, json, time
sys.path.insert(0, "ng/stages"); sys.path.insert(0, ".")
import a34_core as K
e = K.open_emu("a34r2_s33d.log")
res = []
try:
    e.load("ref4751/07_3-3_control")
    pre = K.load_rows("b33_pre2")[:13792 - 13741]
    e.run(pre)
    base = e.msave()
    t = time.time()
    for X1, tt, X2, ja, jd in itertools.product((79, 90, 100, 110), range(13814, 13826, 2), (176, 186), range(13866, 13892, 4), ("A", "RA")):
        L = K.Legal(pre)
        e.mload(base)
        hits, prevb, kill, bad = [], None, None, False
        r1 = r2 = False
        f = 13793
        while f < 13915:
            if f < tt - 2:
                r = ("Right",) if not r1 else ()
            elif f < tt:
                r = ("Left",)
            elif f < tt + 2:
                r = ("Up", "B")
            elif f < ja:
                r = ("Right",) if not r2 else ()
            elif f < ja + 2:
                r = ("A",) if jd == "A" else ("Right", "A")
            else:
                r = ("Down", "B") if (f - ja - 2) % 5 in (0, 1) else ()
            r = K.greedy_legal([r], L)[0]
            s = e.step(r, 1)
            if f < tt - 2 and s.x >= X1:
                r1 = True
            if f >= tt + 2 and s.x >= X2:
                r2 = True
            if s.hp == 0 or (s.dead & 0x80):
                bad = True; break
            if prevb is not None and s.boss_real < prevb:
                hits.append((s.frame, s.boss_real))
            prevb = s.boss_real
            if s.boss_real == 0:
                kill = s.frame; break
            f += 1
        if bad:
            continue
        res.append((kill or 99999, prevb, (X1, tt, X2, ja, jd), hits))
        if kill or prevb <= 2:
            print("ok", res[-1], flush=True)
    res.sort(key=lambda r: (r[0], r[1]))
    for r in res[:12]:
        print(r, flush=True)
    print(f"{time.time() - t:.0f}s", flush=True)
    json.dump(res[:40], open("work/a34r2/s33d.json", "w"))
finally:
    e.close()
