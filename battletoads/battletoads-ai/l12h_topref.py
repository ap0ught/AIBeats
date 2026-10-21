"""L12h: the improved reference line for the top of the tower (from the static spring ledge (51, H 4941), old frame 8085, to the level
end), built and checked on L12g's own timeline (bookmark L12h_g_f8000):
   L12g[8085:8496]  +  sprint along the H-5694 floor and dash jump (l12h_top1: -30)  +  1 idle  +  L12g[8609:8650]
   +  the last hop shortened (Right, -, Right+A x16, Right x14; l12h_top2: -6)  +  A held to the end event.
-> logs/fix/L12h_topref.json {inputs (from old frame 8085), landings [(index, x, H)], end (frames from 8085 to the level byte 13)}"""
import json
from l12h_lib import *
G = seg("L12g")
t1 = json.load(open(FIX / "L12h_top1.json")); n_pre, n, gap, ja = t1["params"]
sprint = t1["inputs"][8496 - 8250:][:len(n_pre) + n + gap]          # taps + sprint (+ the released frame)
e = BizHawk(log_name="fix_l12h_topref.log"); e.load("L12h_g_f8000"); run(e, G[8000:8085]); root = e.msave()
def build(tail_wait, ra, rr):
    T = G[8085:8496] + list(sprint); return T
best = None
for wait in (0, 1, 2, 3):
    for ra, rr in ((16, 14), (16, 12), (16, 16), (16, 18), (14, 14), (18, 14)):
        e.mload(root); T = G[8085:8496] + list(sprint); run(e, T); k = len(T); land = None
        for i in range(70):                                              # the dash jump to the (240, 5741) platform
            b = "Left+A" if i < ja else "Left"
            e.step(bt(b), 1); T.append(b); s = rd(e)
            if s["z"] == 0: land = (len(T), s["x"], s["H"]); break
        if not land or not (5744 <= land[2] <= 5748): continue
        T2 = T + [""] * wait + G[8609:8650] + ["Right", ""] + ["Right+A"] * ra + ["Right"] * rr + ["A"] * 300
        e.mload(root); end = None; lands = []; pz = 0
        for i, b in enumerate(T2):
            e.step(bt(b), 1); m = e.ram(0, 0x800); s = rd(None, m)
            if m[0x10] == 13: end = i + 1; break
            if m[0x51A] < 47: break
            if s["z"] == 0 and pz != 0: lands.append((i + 1, s["x"], s["H"]))
            pz = s["z"]
        print("wait", wait, "ra", ra, "rr", rr, "-> level 13 after", end, "frames (L12g: 795)", flush=True)
        if end and (best is None or end < best[0]): best = (end, T2[:end], lands, (wait, ra, rr))
print("BEST", best[0], best[3], "landings", best[2])
json.dump(dict(inputs=best[1], landings=best[2], end=best[0], params=best[3]), open(FIX / "L12h_topref.json", "w"))
e.close()
