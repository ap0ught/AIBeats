"""L12h stage 2b: redo the flight from the spring launch (piece s2 cut at its launch frame) so that the jump off the lift is a dash jump
(release, tap, release on the landing frame, Left+A): the TAS reaches the wide platform at x 170 at 3 px/frame.
 -> piece s2b / bookmark L12h_s2b (standing on the wide platform), also piece s2lift / bookmark L12h_s2lift (on the lift, landing frame)."""
import sys
from l12h_lib import *
p = load_piece("s2"); par = p["params"]
# find the launch frame: first z=8 after the spring landing
e = BizHawk(log_name="fix_l12h_s2b2.log"); e.load(p["base"]); k = p["base_k"]; Lz = None; onspring = False
for i, b in enumerate(p["inputs"]):
    e.step(bt(b), 1); k += 1; s = rd(e)
    if s["z"] == 0 and 4395 <= s["H"] <= 4420 and k > 5860: onspring = True
    if onspring and s["z"] == 8: Lz = k; break
print("launch frame", Lz, s["x"], s["spd"], flush=True)
pre = p["inputs"][:Lz - p["base_k"]]; la = e.msave()
best = None
for fa in range(8, 30):
    # pass 1: Left held to the landing
    e.mload(la); k = Lz; seq = []
    land = None
    for i in range(80):
        b = "Left+A" if i < fa else "Left"
        e.step(bt(b), 1); k += 1; seq.append(b); s = rd(e)
        if not alive(s): break
        if s["z"] == 0: land = (k, s["x"], s["H"]); break
    if not land or not (4486 <= land[2] <= 4500): continue
    for variant in (0, 1, 2):
        Ll = land[0] + (1 if variant == 2 else 0)
        seq2 = list(seq[:Ll - Lz])
        while len(seq2) < Ll - Lz: seq2.append("Left")
        if variant in (0, 2): seq2[-3] = seq2[-3].replace("Left", "").strip("+"); seq2[-1] = seq2[-1].replace("Left", "").strip("+")      # release, tap, release
        else: seq2[-2] = seq2[-2].replace("Left", "").strip("+"); seq2[-1] = "Left"; seq2.append("")
        e.mload(la); run(e, seq2); s = rd(e); k = Lz + len(seq2)
        if s["z"] != 0 or not (4486 <= s["H"] <= 4500): continue
        lift_state = (k, s["x"], ob(s, 0x34, 4488, 6))
        for hj in (12, 16, 20, 22, 24, 30):
            e2 = e.msave(); kk = k; sq = list(seq2); wide = None; sp0 = None
            for i in range(60):
                b = "Left+A" if i < hj else "Left"
                e.step(bt(b), 1); kk += 1; sq.append(b); s = rd(e)
                if i == 1: sp0 = s["spd"]
                if not alive(s): break
                if s["z"] == 0 and s["H"] >= 4570: wide = (kk, s["x"]); break
            e.mload(e2); e.mfree(e2)
            if wide:
                print("fa", fa, "variant", variant, "lift", lift_state, "jump hold", hj, "spd", sp0, "wide", wide, flush=True)
                if best is None or (wide[0], wide[1]) < (best[0][0], best[0][1]): best = (wide, pre + sq, lift_state, pre + seq2)
print("BEST", best[0], best[2])
save_piece("s2b", p["base"], p["base_k"], best[1], wide=best[0][0], face=p["face"])
save_piece("s2lift", p["base"], p["base_k"], best[3], lift=best[2][0], face=p["face"])
e.load(p["base"]); run(e, best[3]); e.save("L12h_s2lift"); run(e, best[1][len(best[3]):]); e.save("L12h_s2b"); print("saved", rd(e))
e.close()
