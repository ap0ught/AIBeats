"""L12h stage 2 refined: face 2's exit from piece s1 (face F): drop at F+351, dash jump Left to the spring, pump (optionally walking Left
on it first), dash launch, lift at its spawn, jump to the wide platform. Scans the pump/flight parameters for the earliest wide-platform
landing. -> piece s2 (inputs from L12h_g_f5000), bookmark L12h_s2."""
import sys, json, itertools
from l12h_lib import *
p = load_piece("s1"); F = p["face"]
e = BizHawk(log_name="fix_l12h_s2r.log"); e.load(p["base"]); run(e, p["inputs"]); k0 = p["base_k"] + len(p["inputs"])
D = F + 351
pre_idle = [""] * (D - k0); run(e, pre_idle); base = e.msave()
# landing frame on the floor with Left held
e.step(("Left",), 1); e.step(("Down", "Left"), 1); kk = D + 2
while True:
    e.step(("Left",), 1); kk += 1
    if rd(e)["z"] == 0: break
LF = kk; print("floor landing at", LF, flush=True)
head = ["Left", "Down+Left"] + ["Left"] * (LF - 2 - (D + 2)) + ["", "Left", ""]       # ... release, tap, release on the landing frame
e.mload(base); run(e, head); s = rd(e); assert s["z"] == 0, s
fl = e.msave(); kf = D + len(head); print("on the floor", kf, s["x"], flush=True)
best = None; n = 0
def flight_and_rest(k, seq, ev, fa, coast):
    for i in range(110):
        b = "Left+A" if i < fa else ("Left" if not (coast and coast[0] <= i < coast[1]) else "")
        e.step(bt(b), 1); k += 1; seq.append(b); s = rd(e)
        if not alive(s): ev["dead"] = k; return None
        lf = ob(s, 0x34, 4488, 6)
        if lf and "liftspawn" not in ev: ev["liftspawn"] = (k, lf[0], s["x"], s["H"])
        if s["z"] == 0: ev["land2"] = (k, s["x"], s["H"], lf); break
    if "land2" not in ev or not (4486 <= s["H"] <= 4500): return None
    for i in range(60):
        e.step(("Left", "A"), 1); k += 1; seq.append("Left+A"); s = rd(e)
        if not alive(s): ev["dead"] = k; return None
        if s["z"] == 0 and s["H"] >= 4570: ev["wide"] = (k, s["x"]); return k
    return None
for h in (38, 40, 42, 44, 46, 50):
    for pre in (0, 1, 2, 3):
        # pass A: where/when do we land on the spring?
        e.mload(fl); k = kf; seqA = []
        land = None
        for i in range(100):
            b = "Left+A" if i < h else "Left"
            e.step(bt(b), 1); k += 1; seqA.append(b); s = rd(e)
            if s["z"] == 0: land = (k, s["x"], s["H"], ob(s, 0x36, 4407, 40)); break
        if not land or land[2] < 4400: print("h", h, "no spring", land, flush=True); continue
        Ls = land[0]
        if pre:
            if Ls - pre - kf < h + 1: continue                      # A must have been released first
            e.mload(fl); k = kf; seqA = []
            for i in range(Ls - kf):
                b = "Left+A" if (i < h or kf + i + 1 > Ls - pre) else "Left"
                e.step(bt(b), 1); k += 1; seqA.append(b)
            s = rd(e)
            if s["z"] != 0 or s["H"] < 4400: print("h", h, "pre", pre, "no spring", s["x"], s["H"], s["z"], flush=True); continue
            land = (k, s["x"], s["H"], ob(s, 0x36, 4407, 40))
        sp = e.msave()
        # pass B: launch frame with A held
        L = None
        for i in range(40):
            e.step(("A",), 1)
            if rd(e)["z"] == 8: L = Ls + i + 1; break
        if L is None: print("h", h, "pre", pre, "no launch", land, flush=True); e.mfree(sp); continue
        print("h", h, "pre", pre, "spring landing", land, "launch", L, flush=True)
        for w in (0, 6, 10, 14, 18):                                # walk Left on the spring for w frames at the start of the pump
            for tap in ((L - 2, L - 1), (L - 3, L - 2), (L - 13, L - 1), (L - 9, L - 1)):       # Left pressed on [tap0, tap1), released until L
                e.mload(sp); k = Ls; seqB = []
                for f in range(Ls + 1, L + 1):
                    b = "Left+A" if (f <= Ls + w or tap[0] <= f < tap[1] or f >= L) else "A"
                    e.step(bt(b), 1); k += 1; seqB.append(b)
                s = rd(e)
                if s["z"] != 8 or s["spd"] < 180: continue
                la = e.msave(); xl = s["x"]; spx = (ob(s, 0x36, 4407, 40) or [0])[0]
                for fa in (10, 12, 14, 16, 18, 20, 22, 26):
                    for coast in (None, (20, 26), (24, 30)):
                        e.mload(la); ev = {"land": land, "launch": (L, xl, spx)}; seq = []
                        r = flight_and_rest(L, seq, ev, fa, coast); n += 1
                        if r and (best is None or r < best[0]):
                            best = (r, ev, pre_idle + head + seqA + seqB + seq, dict(h=h, pre=pre, w=w, tap=(tap[0] - L, tap[1] - L), fa=fa, coast=coast))
                            print("  new best", r, ev, best[3], flush=True)
                e.mfree(la)
        e.mfree(sp)
print("tried", n, "BEST", best[0], best[1], best[3])
save_piece("s2", p["base"], p["base_k"], p["inputs"] + best[2], wide=best[0], face=F, params=best[3])
e.load(p["base"]); run(e, p["inputs"] + best[2]); e.save("L12h_s2"); print("saved L12h_s2", rd(e))
e.close()
