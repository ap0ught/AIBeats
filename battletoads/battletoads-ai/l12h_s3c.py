"""L12h stage 3c: from the kill (piece s3b) board the circling platform as the TAS does, ride it, pump as early as the flight allows,
dash launch Left to the static platform (240, H 4727), hop to the walker's platform (H 4766).
-> piece s3c / bookmark L12h_s3c (standing on the walker's platform)."""
import sys
from l12h_lib import *
from l12h_tasrun import tasrun
p = load_piece("s3b"); k0 = p["base_k"] + len(p["inputs"])
e = BizHawk(log_name="fix_l12h_s3c.log"); e.load(p["base"]); run(e, p["inputs"])
seq0, ev, k, dev = tasrun(e, k0, 74998, 75021)          # jump onto the circling platform (lands ~6157)
s = rd(e); print("on the platform?", k, s["x"], s["H"], s["z"], ob(s, 0x36, 4632, 40), flush=True)
assert s["z"] == 0 and 4630 <= s["H"] <= 4640
kb = k; base = e.msave()
best = None
for walk in ("", "Left"):                               # ride standing still, or creep Left on the platform like the TAS
    for pa in range(kb + 30, kb + 66, 1):
        e.mload(base); k = kb; seq = []
        def st(b):
            global k
            e.step(bt(b), 1); k += 1; seq.append(b); return rd(e)
        while k < pa - 1: s = st(walk)
        s = st("")                                       # (A must be a fresh press)
        if s["z"] != 0: continue
        # find the launch frame with A held
        e2 = e.msave(); L = None
        for i in range(40):
            e.step(("A",), 1)
            if rd(e)["z"] == 8: L = k + i + 1; break
        e.mload(e2); e.mfree(e2)
        if L is None: continue
        while k < L - 3: s = st("A")
        s = st("Left+A"); s = st("A"); s = st("Left+A")
        if s["z"] != 8 or s["spd"] < 180: continue
        la = e.msave(); kl = k; seql = list(seq); xl = s["x"]; pl = (ob(s, 0x36, 4632, 40) or [None])[0]
        for fa in (16, 20, 24, 28, 32, 40, 60):
            e.mload(la); k = kl; seq = list(seql); land = None
            for i in range(90):
                s = st("Left+A" if i < fa else "Left")
                if not alive(s): break
                if s["z"] == 0: land = (k, s["x"], s["H"]); break
            if not land or not (4728 <= land[2] <= 4736): continue
            # hop up to the walker's platform (TAS: leA x3, -, le, -, leA, le...)
            for hop in (("Left+A",) * 3 + ("", "Left", "", "Left+A") + ("Left",) * 20, ("Left+A",) * 6 + ("Left",) * 24, ("",) + ("Left+A",) * 5 + ("Left",) * 24, ("Left+A",) * 10 + ("Left",) * 20):
                e3 = e.msave(); k3 = k; seq3 = list(seq); arr = None
                for b in hop:
                    s = st(b)
                    if not alive(s): break
                    if s["z"] == 0 and 4762 <= s["H"] <= 4770: arr = (k, s["x"]); break
                if arr and (best is None or arr[0] < best[0][0]):
                    best = (arr, dict(walk=walk, pa=pa, L=L, xl=xl, plat=pl, fa=fa, static=land), p["inputs"] + seq0 + list(seq))
                    print("new best", best[0], best[1], flush=True)
                e.mload(e3); e.mfree(e3); k = k3; seq = seq3
        e.mfree(la)
print("BEST", best[0], best[1])
save_piece("s3c", p["base"], p["base_k"], best[2], arrive=best[0][0])
e.load(p["base"]); run(e, best[2]); e.save("L12h_s3c"); s = rd(e); print("saved L12h_s3c", {a: b for a, b in s.items() if a != "objs"}, [d for d in s["objs"] if d[0] in (0x36, 0x34, 0x62)])
e.close()
