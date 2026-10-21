"""L12h stage 1 scan: early pump after the pre-face-2 kill -> face 2 spawns -> land back on the spring -> second pump -> x-480 pole.
params: a0 = first A frame, r0 = frames of plain A after the launch before Right+A, rel = frames before landing where A is released (0 = hold)."""
import sys, itertools
from l12h_lib import *
G = seg("L12g")
e = BizHawk(log_name="fix_l12h_s1c.log"); e.load("L12h_g_f5250")
run(e, G[5250:5331]); base = e.msave()
def attempt(a0, r0, d2="Left+A", pre2=0, p1="Right+A"):
    e.mload(base); k = 5331; seq = []; ev = {}
    def st(b):
        nonlocal k
        e.step(bt(b), 1); k += 1; seq.append(b); return rd(e)
    while k < a0: st("")
    s = None
    for i in range(60):                      # pump 1
        s = st(p1)
        if s["z"] == 8: ev["launch"] = k; break
    if "launch" not in ev: return ev, seq
    for i in range(r0): s = st("A")
    for i in range(140):                     # fly right over the spring
        s = st("Right+A")
        if s["faces"] and "face" not in ev: ev["face"] = k
        if not alive(s): ev["dead"] = k; return ev, seq
        if s["z"] == 0: ev["land"] = (k, s["x"], s["H"], ob(s, 0x36, 4407, 40)); break
    if "land" not in ev or s["H"] < 4400: return ev, seq
    for i in range(pre2): s = st("")
    for i in range(60):                      # pump 2
        s = st("A")
        if s["z"] == 8: ev["launch2"] = k; break
    if "launch2" not in ev: return ev, seq
    top = 0
    for i in range(120):
        s = st(d2); top = max(top, s["H"])
        if s["faces"] and "face" not in ev: ev["face"] = k
        if not alive(s): ev["dead"] = k; break
        if s["an"] in (94, 95, 96): ev["pole"] = (k, s["x"], s["H"]); break
        if s["z"] == 0: ev["land2"] = (k, s["x"], s["H"]); break
    ev["apex2"] = top
    return ev, seq
best = None
for a0 in range(5363, 5384):
    for r0 in (0,):
        ev, seq = attempt(a0, r0)
        print(a0, r0, ev, flush=True)
        if "pole" in ev and "face" in ev and (best is None or (ev["face"], ev["pole"][0]) < best[0]): best = ((ev["face"], ev["pole"][0]), a0, r0, seq)
print("BEST", best[:3] if best else None)
if best:
    save_piece("s1", "L12h_g_f5250", 5250, G[5250:5331] + best[3], face=best[0][0], pole=best[0][1])
e.close()
