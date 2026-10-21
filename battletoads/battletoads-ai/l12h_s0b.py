"""L12h stage 0b: the pre-face-2 Hornhead fight re-scanned (kick, sprint away, turn-around boot) from several start x.
params: drift n (Right frames from 5168), n1 extra Right frames after the landing 5225, g idle, then Left+B; after the landing
double-tap Left, run m frames, Right+B held to the kill. Reports kill frame K, the spring landing and the toad's offset on the spring."""
import json, sys
from l12h_lib import *
G = seg("L12g")
e = BizHawk(log_name="fix_l12h_s0b.log"); e.load("L12h_g_f5000")
run(e, G[5000:5140]); base0 = e.msave()
res = []
for n in (0, 3, 5, 6, 7, 8, 9, 10, 11):
    e.mload(base0); seq0 = list(G[5140:5225])
    for i in range(n):
        j = 5168 - 5140 + i
        seq0[j] = "Right+A" if seq0[j] == "A" else seq0[j]
    run(e, seq0); s = rd(e); x0 = s["x"]; base = e.msave()
    for n1 in range(0, 8):
        for g in (0, 1):
            e.mload(base); k = 5225; seq = list(seq0)
            def st(b):
                global k
                e.step(bt(b), 1); k += 1; seq.append(b); return rd(e)
            for i in range(n1): s = st("Right")
            for i in range(g): s = st("")
            s = st("Left+B"); hit = None
            for i in range(60):
                s = st("")
                hh = [d[3] for d in s["objs"] if d[0] == 0x5c]
                if hit is None and hh and hh[0] < 47: hit = k
                if not alive(s): break
                if hit and s["z"] == 0 and s["an"] == 1: break
                if hit is None and i > 24: break
            if hit is None or not alive(s) or s["an"] != 1: continue
            mid = e.msave(); kmid = k; seqmid = list(seq)
            for m in range(22, 42):
                e.mload(mid); k = kmid; seq = list(seqmid)
                st("Left"); st(""); 
                for i in range(m): s = st("Left")
                K = None
                for i in range(40):
                    s = st("Right+B")
                    hh = [d[3] for d in s["objs"] if d[0] == 0x5c]
                    if not alive(s): break
                    if hh and hh[0] == 0: K = k; xk = s["x"]; break
                if K is None: continue
                land = None
                for i in range(40):
                    s = st("")
                    if s["z"] == 0: land = (k, s["x"], s["H"], (ob(s, 0x36, 4407, 40) or [None])[0]); break
                if land and land[2] >= 4400:
                    off = dx(land[1], land[3])
                    res.append(dict(n=n, x0=x0, n1=n1, g=g, m=m, hit=hit, K=K, xk=xk, land=land, off=off, seq=seq))
                    print(f"n={n} x0={x0} n1={n1} g={g} m={m} hit={hit} K={K} xk={xk} land={land} off={off}", flush=True)
            e.mfree(mid)
    e.mfree(base)
res.sort(key=lambda r: (r["K"] - r["off"] / 2))
json.dump(res, open(FIX / "L12h_s0b.json", "w"))
print("BEST by K - off/2:")
for r in res[:15]: print({k: v for k, v in r.items() if k != "seq"})
e.close()
