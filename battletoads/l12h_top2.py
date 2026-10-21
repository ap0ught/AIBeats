"""L12h top probe 2 (L12g's timeline): the level's end is an event (0x7F) - when does it fire? From the last jump of the old route
(old frame 8652: Right+A x16, Right x18, A x63, idle) try variants of the final approach and of what the toad does on the top ledge
(276, H 5950): fresh jumps so that the camera scrolls up sooner. Reports the frame the level byte turns 13 (L12g: 8880)."""
import sys, json, itertools
from l12h_lib import *
G = seg("L12g")
e = BizHawk(log_name="fix_l12h_top2.log"); e.load("L12h_g_f8500"); run(e, G[8500:8650]); base = e.msave()
def trial(seq, maxf=330):
    e.mload(base); k = 8650; ev = {}
    for i in range(maxf):
        b = seq[i] if i < len(seq) else ""
        e.step(bt(b), 1); k += 1; m = e.ram(0, 0x800)
        if m[0x10] == 13: return k, ev
        if m[0x10] == 5 and m[0x51A] < 47: return None, ev
        if "e7f" not in ev and any(m[0x3C1 + q] == 0x7F for q in range(2, 15)): ev["e7f"] = (k, m[0x89] | m[0x8A] << 8, m[0x439] | m[0x42A] << 8)
    return None, ev
old = G[8650:]
print("old:", trial(old), flush=True)
res = []
# the old final approach: 8650 Right, 8651 -, 8652 Right+A x16, Right x18, then A x63 (lands 8712), idle
for ra in (16, 12, 20, 24, 30):                      # frames of Right+A
    for rr in (18, 14, 22, 10, 26):                  # then Right
        head = ["Right", ""] + ["Right+A"] * ra + ["Right"] * rr
        for tail_name, tail in (("A held", ["A"] * 200), ("idle", [""] * 200), ("jump at landing", None), ("Right held", ["Right"] * 200), ("Left held", ["Left"] * 200)):
            if tail is not None:
                r, ev = trial(head + tail); res.append((r or 99999, (ra, rr, tail_name), ev))
            else:
                for d in range(18, 40, 2):           # frames after the head: idle d, then hold A (a fresh jump on the ledge), again every 44 frames
                    for per in (40, 60, 200):
                        t = [""] * d
                        while len(t) < 220: t += ["A"] * (per - 2) + ["", ""]
                        r, ev = trial(head + t); res.append((r or 99999, (ra, rr, "jump", d, per), ev))
    print("ra", ra, "best so far", min(res, key=lambda x: x[0])[:2], flush=True)
res.sort(key=lambda x: x[0])
for r in res[:12]: print(r)
e.close()
