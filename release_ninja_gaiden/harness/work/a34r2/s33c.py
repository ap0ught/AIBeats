"""3-3 plan C (the record's): after wheel 4 (4 HP at 13822) stand at x X facing right and ground-slash the boss on
the descending half of its crossing (13850-13874); then jump-slash it as it sits right / takes off."""
import sys, itertools, json, time
sys.path.insert(0, "ng/stages"); sys.path.insert(0, ".")
import a34_core as K
e = K.open_emu("a34r2_s33c.log")
res = []
try:
    e.load("ref4751/07_3-3_control")
    pre = K.load_rows("b33_pre2")[:13822 - 13741]
    e.run(pre)
    base = e.msave()
    t = time.time()
    for X, sb, per, ja, jd in itertools.product(range(100, 176, 10), range(13840, 13872, 4), (5,), (0, 13884, 13890), ("A",)):
        if ja == 0 and jd == "RA":
            continue
        L = K.Legal(pre)
        e.mload(base)
        hits, prevb, kill, bad, reached = [], None, None, False, False
        f = 13823
        while f < 13915:
            if not reached and f < sb:
                r = ("Right",)
            elif ja and f in (ja, ja + 1):
                r = ("A",) if jd == "A" else ("Right", "A")
            elif ja and f > ja + 1:
                r = ("Down", "B") if (f - ja - 2) % 5 in (0, 1) else ()
            elif f >= sb and (f - sb) % per in (0, 1):
                r = ("B",)
            else:
                r = ()
            r = K.greedy_legal([r], L)[0]
            s = e.step(r, 1)
            if s.x >= X:
                reached = True
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
        res.append((kill or 99999, prevb, (X, sb, per, ja, jd), hits))
        if kill or prevb <= 2 or (hits and hits[0][0] < 13880):
            print("ok", res[-1], flush=True)
    res.sort(key=lambda r: (r[0], r[1]))
    for r in res[:12]:
        print(r, flush=True)
    print(f"{time.time() - t:.0f}s", flush=True)
    json.dump(res[:40], open("work/a34r2/s33c.json", "w"))
finally:
    e.close()
