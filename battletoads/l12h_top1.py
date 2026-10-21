"""L12h top probe 1 (on L12g's own timeline, bookmark L12h_g_f8250): the walk along the H-5694 floor (old frames 8496..8568: Left x72 at
walking speed, then Left+A) -> sprint (tap, gap, hold) and a dash jump to the static platform (240, H 5741). Then L12g's inputs from its
landing there (old 8609) with a standing wait scanned, up to the level end. Reports the frame the level byte turns 13 (L12g: 8880).
Also tries, at the very top, a fresh jump after the last landing (the end event is camera-triggered)."""
import sys, json
from l12h_lib import *
G = seg("L12g")
e = BizHawk(log_name="fix_l12h_top1.log"); e.load("L12h_g_f8250"); run(e, G[8250:8496]); base = e.msave()
s = rd(e); print("at 8496:", s["x"], s["H"], s["z"], s["an"], flush=True)
class Run:
    def __init__(self, sid, k, seq): e.mload(sid); self.k = k; self.seq = list(seq); self.s = rd(e)
    def st(self, b):
        e.step(bt(b), 1); self.k += 1; self.seq.append(b); self.s = rd(e); return self.s
    def ok(self): return alive(self.s)
res = []
for pre in (("Left", ""), ("", "Left", ""), ("Left", "", "Left", "")):
    for n in range(10, 44, 2):                      # sprint frames before the jump
        for gap in (0, 1):                          # one released frame before Left+A keeps the sprint in the air
            for ja in (6, 10, 14, 20, 28):
                r = Run(base, 8496, [])
                for b in pre: r.st(b)
                for i in range(n): r.st("Left")
                if not r.ok() or r.s["z"] != 0: continue
                for i in range(gap): r.st("")
                land = None
                for i in range(70):
                    s = r.st("Left+A" if i < ja else "Left")
                    if not r.ok(): break
                    if s["z"] == 0:
                        land = (r.k, s["x"], s["H"]); break
                if land and 5744 <= land[2] <= 5748: res.append((land[0], land[1], (pre, n, gap, ja), e.msave(), list(r.seq)))
res.sort(key=lambda t: t[0])
print("landings on the (240, 5741) platform (old: 8609 at x 251):", [(t[0], t[1], t[2]) for t in res[:10]], flush=True)
def finish(sid, k, seq, j):
    """old inputs from old index j with a wait scan at this landing only, then straight to the level end"""
    for wv in list(range(0, 40)) + list(range(40, 200, 2)):
        e.mload(sid); kk = k; sq = list(seq)
        for i in range(wv): e.step((), 1); kk += 1; sq.append("")
        end = None; hurt = False
        for i in range(j, len(G) + 300):
            b = G[i] if i < len(G) else ""
            e.step(bt(b), 1); kk += 1; sq.append(b); m = e.ram(0, 0x800)
            if m[0x10] == 13: end = kk; break
            if m[0x10] == 5 and m[0x51A] < 47: hurt = True; break
            if kk - k > 420: break
        if end and not hurt: return end, wv, sq
    return None, None, None
best = None
for lk, lx, par, sid, seq in res[:8]:
    end, wv, sq = finish(sid, lk, seq, 8609)
    print("from landing", lk, lx, par, "-> wait", wv, "level 13 at", end, flush=True)
    if end and (best is None or end < best[0]): best = (end, wv, sq, par)
if best:
    json.dump(dict(base="L12h_g_f8250", base_k=8250, inputs=G[8250:8496] + best[2], end=best[0], params=best[3]), open(FIX / "L12h_top1.json", "w"))
    print("BEST level 13 at", best[0], "(L12g 8880)", best[3], "wait", best[1])
e.close()
