"""TOWER1 probe: legal dash jump out of a standstill facing the wrong way: w idle, tap a1, gap g1, tap a2, gap g2, D+A.
    python tw1_dash2.py <K:idx or piece> <Left|Right> [maxw]  -> earliest airborne frame with speed 192"""
import sys
from tw1_lib import *
src, D = sys.argv[1], sys.argv[2]; maxw = int(sys.argv[3]) if len(sys.argv) > 3 else 6
A = seg("A12r")
e = BizHawk(log_name="tw1_dash2.log")
if src.startswith("K:"):
    k0 = int(src[2:]); b0 = (k0 // 250) * 250; e.load(f"tw1_a_f{b0}"); run(e, A[b0:k0])
else:
    p = load_piece(src); e.load(p["base"]); run(e, p["inputs"]); k0 = p["base_k"] + len(p["inputs"])
root = e.msave(); s = rd(e); print("start", fmt(k0, "", s)[:110])
res = []
for w in range(0, maxw + 1):
    for a1 in (1, 2, 3):
        for g1 in range(0, 8):
            for a2 in (0, 1, 2):
                for g2 in range(0, 4):
                    if a2 == 0 and g2: continue
                    seq = [""] * w + [D] * a1 + [""] * g1 + [D] * a2 + [""] * g2 + [D + "+A"] * 3
                    e.mload(root); air = None
                    for i, x in enumerate(seq):
                        e.step(bt(x), 1); s = rd(e)
                        if s["z"] == 8 and air is None: air = i + 1; xa = s["x"]; ha = s["H"]; sp = s["spd"]
                    if air is not None and sp == 192:
                        res.append((air, w, a1, g1, a2, g2, xa, ha))
res.sort()
for r in res[:30]:
    print(f"airborne at +{r[0]} spd 192 | w={r[1]} tap={r[2]} gap={r[3]} tap={r[4]} gap={r[5]} | x@air {r[6]} H {r[7]}")
print(len(res), "variants reach 192")
e.close()
