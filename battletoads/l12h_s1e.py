"""L12h stage 1e: dash launch off the spring after the new fight: brute force Right on/off in the frames around the launch for a few a0;
then fly Right+A and see whether the x-480 pole is grabbed in ONE launch. -> logs/fix/L12h_s1.json, bookmark L12h_s1."""
import json, sys, itertools
from l12h_lib import *
G = seg("L12g")
R = json.load(open(FIX / "L12h_s0b.json"))
cands = [r for r in R if r["K"] <= 5323 and r["off"] >= 12 and r["land"][0] == 5340]
e = BizHawk(log_name="fix_l12h_s1e.log")
best = None; allr = []
for c in cands[:5]:
    e.load("L12h_g_f5000"); run(e, G[5000:5140]); run(e, c["seq"]); kb = 5140 + len(c["seq"]); base = e.msave()
    for a0 in range(5355, 5362):
        L = a0 + 25
        e.mload(base); run(e, [""] * (a0 - kb) + ["A"] * (L - 7 - a0)); mid = e.msave()       # at L-7
        for pat in itertools.product((0, 1), repeat=8):                                           # frames L-6 .. L+1
            if pat[6:] != (1, 1): continue
            e.mload(mid); seq = [""] * (a0 - kb) + ["A"] * (L - 7 - a0) + ["Right+A" if p else "A" for p in pat]
            run(e, seq[-8:]); k = L + 1; ev = {}
            for i in range(120):
                e.step(("Right", "A"), 1); k += 1; seq.append("Right+A"); s = rd(e)
                if i == 0: ev["spd"] = s["spd"]; ev["z"] = s["z"]
                if s["faces"] and "face" not in ev: ev["face"] = k
                if not alive(s): ev["dead"] = k; break
                if s["an"] in (94, 95, 96): ev["pole"] = (k, s["x"], s["H"]); break
                if s["z"] == 0: ev["land"] = (k, s["x"], s["H"]); break
            allr.append((c["n"], a0, pat, ev))
            if "pole" in ev and "face" in ev:
                key = (ev["face"], ev["pole"][0])
                if best is None or key < best[0]:
                    best = (key, c, a0, pat, list(G[5000:5140]) + c["seq"] + seq, ev); print("new best", key, c["n"], a0, pat, ev, flush=True)
        e.mfree(mid)
        import collections
        print("fight n", c["n"], "a0", a0, collections.Counter((r[3].get("spd"), "pole" in r[3], r[3].get("face")) for r in allr if r[0] == c["n"] and r[1] == a0), flush=True)
    e.mfree(base)
if best:
    print("BEST", best[0], {k: v for k, v in best[1].items() if k != "seq"}, best[2], best[3], best[5])
    save_piece("s1", "L12h_g_f5000", 5000, best[4], face=best[0][0], pole=best[0][1])
    e.load("L12h_g_f5000"); run(e, best[4]); e.save("L12h_s1"); print("saved L12h_s1 at", 5000 + len(best[4]), rd(e)["an"])
e.close()
