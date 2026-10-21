"""L12h stage 3a/3b: the wide-platform Hornhead (63 hp) from the dash landing at x 172 (piece s2b): hop (A a frames), flying kick B at kb
(63 -> 47, it is knocked Left), land, double-tap Left, run m frames, Left+B = the big boot (47 -> 0), slide to the platform's left part.
-> piece s3b / bookmark L12h_s3b (toad standing again after the kill), logs/fix/L12h_s3a.json (all results)."""
import json, sys
from l12h_lib import *
p = load_piece("s2b"); k0 = p["base_k"] + len(p["inputs"])
e = BizHawk(log_name="fix_l12h_s3a.log"); e.load(p["base"]); run(e, p["inputs"]); base = e.msave()
def hh(s): return [(d[1], d[2], d[3]) for d in s["objs"] if d[0] == 0x5c]
res = []; best = None
for a in (1, 2, 3, 4, 6, 8):
    for kb in range(k0 + 8, k0 + 34):
        e.mload(base); k = k0; seq = []
        def st(b):
            global k
            e.step(bt(b), 1); k += 1; seq.append(b); return rd(e)
        for i in range(a): s = st("A")
        while k < kb: s = st("")
        hit = None
        for i in range(13):
            s = st("B")
            h = hh(s)
            if h and h[0][2] < 63: hit = k
        for i in range(70):
            if not alive(s): break
            h = hh(s)
            if hit is None and h and h[0][2] < 63: hit = k
            if s["z"] == 0 and s["an"] in (1, 2): break
            s = st("")
        if hit is None or not alive(s) or s["z"] != 0: continue
        print("a", a, "kb", kb, "hit", hit, "ready", k, "toad", s["x"], "hornhead", hh(s), flush=True)
        mid = e.msave(); kmid = k; seqmid = list(seq)
        for w in (0, 4, 8, 12, 16, 20, 24):
            for m in range(28, 42, 2):
                e.mload(mid); k = kmid; seq = list(seqmid)
                for i in range(w): s = st("")
                st("Left"); st("")
                for i in range(m): s = st("Left")
                if not alive(s): continue
                s = st("Left+B"); K = None
                for i in range(45):
                    s = st("Left")
                    if not alive(s): break
                    h = hh(s)
                    if h and h[0][2] == 0: K = k; break
                if K is None: continue
                gone = None; land = None
                for i in range(90):
                    s = st("")
                    if not alive(s): break
                    if gone is None and not hh(s): gone = k
                    if s["z"] == 0 and land is None: land = (k, s["x"])
                    if land and gone and s["an"] in (1, 2): break
                if not alive(s) or land is None: continue
                r = dict(a=a, kb=kb, hit=hit, w=w, m=m, K=K, gone=gone, land=land, ready=k, x=s["x"], plat=ob(s, 0x36, 4632, 40))
                res.append(dict(r, seq=list(seq)))
                print("   ", r, flush=True)
                if best is None or (K, k) < (best["K"], best["ready"]): best = dict(r, seq=list(seq))
        e.mfree(mid)
json.dump(res, open(FIX / "L12h_s3a.json", "w"))
print("BEST", {k: v for k, v in best.items() if k != "seq"})
save_piece("s3b", p["base"], p["base_k"], p["inputs"] + best["seq"], K=best["K"], ready=best["ready"])
e.load(p["base"]); run(e, p["inputs"] + best["seq"]); e.save("L12h_s3b"); print("saved L12h_s3b", rd(e))
e.close()
