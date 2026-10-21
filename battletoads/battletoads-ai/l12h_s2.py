"""L12h stage 2: face 2's exit the TAS's way. From the x-480 pole: drop when the wind lets go (face + 351), land on the floor, jump Left
onto the circling spring, pump, launch Left as the camera unlocks, land on the lift where it spawns (x ~238), jump Left to the wide
platform (H 4574).  python l12h_s2.py <piece or G> <face frame> [verbose]"""
import sys, json
from l12h_lib import *
src, F = sys.argv[1], int(sys.argv[2]); VERB = len(sys.argv) > 3
e = BizHawk(log_name=f"fix_l12h_s2_{src}.log")
if src == "G":
    G = seg("L12g"); e.load("L12h_g_f5250"); run(e, G[5250:5700]); k0 = 5700; pre_p = None
else:
    p = load_piece(src); e.load(p["base"]); run(e, p["inputs"]); k0 = p["base_k"] + len(p["inputs"]); pre_p = p
s = rd(e); assert s["an"] in (94, 95, 96), s
base = e.msave()
def attempt(D, j0, h, pre, pd, fa, verbose=False):
    """drop at D; jump j0 frames after the landing with A held h frames; pump after pw idle frames on the spring holding A(+pd);
    flight Left+A for fa frames then Left; from the lift jump Left+A."""
    e.mload(base); k = k0; seq = []; ev = {}
    def st(b):
        nonlocal k
        e.step(bt(b), 1); k += 1; seq.append(b); s = rd(e)
        if verbose: print(k, f"{b:9s} x={s['x']} H={s['H']} z={s['z']} an={s['an']} spd={s['spd']} cam={s['cam']} f{s['faces']} |", "spring", ob(s, 0x36, 4407, 40), "lift", ob(s, 0x34, 4488, 6), flush=True)
        return s
    while k < D: st("")
    s = st("Left"); s = st("Down+Left")
    if D not in LAND:                                   # first pass: when does the toad reach the floor?
        e2 = e.msave(); kk = k
        for i in range(80):
            e.step(("Left",), 1); kk += 1
            if rd(e)["z"] == 0: LAND[D] = kk; break
        e.mload(e2); e.mfree(e2)
    if D not in LAND: return ev, seq
    L = LAND[D]
    while k < L - 2: s = st("Left")
    s = st(""); s = st("Left"); s = st("")              # release, tap, release on the landing frame: the dash jump (speed 192 at once)
    if s["z"] != 0: ev["nofloor"] = (k, s["x"], s["H"], s["z"]); return ev, seq
    ev["floor"] = (k, s["x"])
    for i in range(j0): s = st("")
    # pass A: jump (A held h frames) and find the landing on the spring
    key = (D, j0, h)
    if key not in SPR:
        e2 = e.msave(); kk = k; r = None
        for i in range(h + 90):
            e.step(bt("Left+A" if i < h else "Left"), 1); kk += 1; s2 = rd(e)
            if not alive(s2): break
            if s2["z"] == 0: r = (kk, s2["x"], s2["H"], ob(s2, 0x36, 4407, 40)); break
        SPR[key] = r; e.mload(e2); e.mfree(e2)
    r = SPR[key]
    if r is None or r[2] < 4400: ev["land"] = r; return ev, seq
    Ls = r[0]
    while k < Ls - pre: s = st("Left+A" if k < ev["floor"][0] + j0 + h else "Left")
    while k < Ls: s = st("A")
    if s["z"] != 0 or s["H"] < 4400: ev["land"] = (k, s["x"], s["H"], s["z"]); return ev, seq
    ev["land"] = (k, s["x"], s["H"], ob(s, 0x36, 4407, 40))
    # pass B: pump (A held) and find the launch frame
    key2 = (D, j0, h, pre, pd)
    if key2 not in LAU:
        e2 = e.msave(); kk = k; L = None
        for i in range(40):
            e.step(bt("+".join([x for x in (pd, "A") if x])), 1); kk += 1
            if rd(e)["z"] == 8: L = kk; break
        LAU[key2] = L; e.mload(e2); e.mfree(e2)
    L = LAU[key2]
    if L is None: return ev, seq
    while k < L - 3: s = st("+".join([x for x in (pd, "A") if x]))
    s = st("Left+A"); s = st("A"); s = st("Left+A")           # tap, gap, hold from the launch frame: dash launch (speed 192)
    ev["launch"] = (k, s["x"], s["spd"], s["z"])
    for i in range(110):
        s = st("Left+A" if i < fa else "Left")
        if not alive(s): ev["dead"] = k; return ev, seq
        lf = ob(s, 0x34, 4488, 6)
        if lf and "liftspawn" not in ev: ev["liftspawn"] = (k, lf[0], s["x"], s["H"])
        if s["z"] == 0:
            ev["land2"] = (k, s["x"], s["H"], lf); break
    if "land2" not in ev or not (4486 <= s["H"] <= 4500): return ev, seq
    for i in range(60):
        s = st("Left+A")
        if not alive(s): ev["dead"] = k; return ev, seq
        if s["z"] == 0 and s["H"] >= 4570: ev["wide"] = (k, s["x"]); break
    return ev, seq
best = None; LAND = {}; SPR = {}; LAU = {}
for D in (F + 351, F + 352):
    for j0 in (0, 1):
        for h in (30, 32, 34, 36, 40, 60):
            for pre in (0, 3):
                for pd in ("",):
                    for fa in (10, 14, 18, 22, 26, 99):
                        ev, seq = attempt(D, j0, h, pre, pd, fa)
                        if fa == 99 or "wide" in ev: print("D", D, "j0", j0, "h", h, "pre", pre, "pd", pd, "fa", fa, ev, flush=True)
                        if "wide" in ev and (best is None or ev["wide"][0] < best[0]): best = (ev["wide"][0], ev, seq, (D, j0, h, pre, pd, fa))
                        if "land" not in ev or "launch" not in ev:
                            print("D", D, "j0", j0, "h", h, "pre", pre, "FAIL", ev, flush=True); break
print("BEST", best[:2] + best[3:] if best else None)
if best and src != "G":
    save_piece("s2", pre_p["base"], pre_p["base_k"], pre_p["inputs"] + best[2], wide=best[0])
    e.load(pre_p["base"]); run(e, pre_p["inputs"] + best[2]); e.save("L12h_s2"); print("saved L12h_s2", rd(e))
e.close()
