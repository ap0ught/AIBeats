"""L12h probe 2: dash launch after WALKING on the spring during the pump: Left+A from frame w0 to L-g-1, gap g frames, Left+A from L (launch 6825)."""
from l12h_lib import *
G = seg("L12g")
e = BizHawk(log_name="fix_l12h_dash2.log"); e.load("L12h_g_f6750"); run(e, G[6750:6800]); base = e.msave()
L = 6825
for w0 in (6801, 6805, 6810, 6815, 6820, 6822):
    for g in (1, 2, 3):
        for hold_from in (L - 1, L, L + 1):
            e.mload(base); k = 6800; out = None
            while k < L + 20:
                if k + 1 < 6801: b = ""
                elif w0 <= k + 1 < hold_from - g: b = "Left+A"
                elif k + 1 >= hold_from: b = "Left+A"
                else: b = "A"
                e.step(bt(b), 1); k += 1; s = rd(e)
                if k == L: xl = s["x"]; sp = ob(s, 0x36, 4800, 40); zl = s["z"]
            print("walk from", w0, "gap", g, "hold from L%+d" % (hold_from - L), "-> at launch x", xl, "spring", sp, "z", zl, "| +20: x", s["x"], "spd", s["spd"], "H", s["H"], flush=True)
e.close()
