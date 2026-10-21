"""TOWER1 probe: the legal replacement for the TAS's Left+Right dash jump. From an A12r state (or a piece end): w idle
frames, then tap the direction a frames, release b frames, direction+A -> report the first airborne frame and speed.
    python tw1_dash.py <K:idx or piece> <Left|Right> [maxw]"""
import sys
from tw1_lib import *
src, D = sys.argv[1], sys.argv[2]; maxw = int(sys.argv[3]) if len(sys.argv) > 3 else 7
A = seg("A12r")
e = BizHawk(log_name="tw1_dash.log")
if src.startswith("K:"):
    k0 = int(src[2:]); b0 = (k0 // 250) * 250; e.load(f"tw1_a_f{b0}"); run(e, A[b0:k0])
else:
    p = load_piece(src); e.load(p["base"]); run(e, p["inputs"]); k0 = p["base_k"] + len(p["inputs"])
root = e.msave(); s = rd(e); print("start", fmt(k0, "", s)[:110])
res = []
for w in range(0, maxw + 1):
    for pre in ([], ["Down"], [D + "+A"], ["A"]):
      for a in range(0, 5):
        for b in range(0, 4):
            seq = [""] * w + pre + [D] * a + [""] * b + [D + "+A"] * 14
            e.mload(root); air = None
            for i, x in enumerate(seq):
                e.step(bt(x), 1); s = rd(e)
                if s["z"] == 8 and air is None: air = i + 1; xa = s["x"]; ha = s["H"]; sp = s["spd"]
            if air is not None:
                res.append((air, -sp, w, pre, a, b, xa, ha, s["x"], s["H"], s["spd"], s["face"]))
res.sort(key=lambda r: (r[1], r[0]))
for r in res[:40]:
    print(f"airborne at +{r[0]} spd {-r[1]} | w={r[2]} pre={r[3]} tap={r[4]} gap={r[5]} | x@air {r[6]} H {r[7]} | after {r[8]},{r[9]} spd {r[10]} face {r[11]}")
e.close()
