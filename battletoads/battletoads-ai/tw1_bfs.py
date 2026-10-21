"""TOWER1: breadth-first search over inputs from one state, deduplicated on the toad's own bytes, for the earliest
frame the toad is airborne at sprint speed (192) in direction D.   python tw1_bfs.py <K:idx or piece> <Left|Right> [depth=22]
Used for the legal replacement of the TAS's Left+Right dash jump. Nothing is written but the result line."""
import sys, hashlib
from tw1_lib import *
src, D = sys.argv[1], sys.argv[2]; depth = int(sys.argv[3]) if len(sys.argv) > 3 else 22
O = "Right" if D == "Left" else "Left"
ALPHA = ["", D, D + "+A", "A", O, "Down"]
A = seg("A12r")
e = BizHawk(log_name="tw1_bfs.log")
if src.startswith("K:"):
    k0 = int(src[2:]); b0 = (k0 // 250) * 250; e.load(f"tw1_a_f{b0}"); run(e, A[b0:k0])
else:
    p = load_piece(src); e.load(p["base"]); run(e, p["inputs"]); k0 = p["base_k"] + len(p["inputs"])
def key(m):
    b = bytes(m[0x3B5 + 15 * 0:0x3B6]) + bytes(m[a] for a in range(0x3C1, 0x5B0, 15)) + bytes(m[0x29:0x30]) + bytes(m[0x3B5:0x3B6])
    return hashlib.md5(b).digest()
m = e.ram(0, 0x800); s = rdm(m); print("start", fmt(k0, "", s)[:100], flush=True)
front = [(e.msave(), [])]; seen = {key(m)}; found = []
for d in range(1, depth + 1):
    nxt = []
    for sid, path in front:
        for b in ALPHA:
            e.mload(sid); e.step(bt(b), 1); m = e.ram(0, 0x800); s = rdm(m)
            if s["hp"] < 47: continue
            if s["z"] == 8 and s["spd"] == 192 and (s["face"] == 64) == (D == "Left"):
                found.append((d, s["x"], s["H"], path + [b])); continue
            if s["z"] == 8: continue                           # airborne without the sprint: not wanted
            kk = key(m)
            if kk in seen: continue
            seen.add(kk); nxt.append((e.msave(), path + [b]))
        e.mfree(sid)
    print("depth", d, "states", len(nxt), "found", len(found), flush=True)
    front = nxt
    if found: break
    if len(front) > 6000: front = front[:6000]
for f in found[:12]:
    print(f"airborne at +{f[0]} x={f[1]} H={f[2]}:", ",".join(x or "-" for x in f[3]))
e.close()
