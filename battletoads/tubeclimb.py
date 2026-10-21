"""Beam up the warp-room tube (2026-10-06): from the old climb start, 2-frame macros over grab/jump inputs; goal = h in 240..250
(the top); then the old finish (Right+A x14, Right) must still land on the far ledge (x >= 400, z 0)."""
import json
from toads.emulator import BizHawk
l6 = [x.replace(",", "+") for x in json.load(open("logs/pbeam_L6c.json"))["inputs"]]
e = BizHawk(log_name="tubeclimb.log"); e.load("L4c5_end0")
for b in l6[:2127]: e.step(tuple(v for v in b.split("+") if v), 1)
def rd():
    m = e.ram(0, 0x800); return dict(x=m[0x3FD] | m[0x3EE] << 8, h=m[0x439], z=m[0x475], an=m[0x3B5], lives=m[0x11], hp=m[0x51A], st=m[0x4B1])
root = e.msave(); s0 = rd(); L0 = s0["lives"]; print("root", s0, flush=True)
ACTS = [(), ("A",), ("Left", "A"), ("Right", "A"), ("Up", "A"), ("Up",), ("Left",), ("Right",), ("Up", "Left", "A"), ("Up", "Right", "A"), ("Down", "A")]
layer = [(root, [], s0)]
best = None
for depth in range(1, 60):
    cand = {}
    for sid, path, s in layer:
        for act in ACTS:
            e.mload(sid); e.step(act, 2); q = rd()
            if q["lives"] < L0 or q["hp"] < 47: continue
            if 240 <= q["h"] < 252 and q["z"] == 8 and q["an"] in (88, 89, 45):
                best = (depth * 2, path + [act], q); break
            key = (q["x"], q["h"], q["z"], q["an"] // 2)
            if key in cand: continue
            cand[key] = (-(q["h"] if q["h"] < 252 else 0) * 2 - (1 if q["an"] in (88, 89) else 0), e.msave(), path + [act], q)
        if best: break
    for sid, _, _ in layer:
        if sid != root: e.mfree(sid)
    if best: break
    layer = sorted(cand.values(), key=lambda c: c[0])[:250]
    layer = [(sid, p, q) for _, sid, p, q in layer]
    if depth % 5 == 0: print("depth", depth, "best h", max(q["h"] if q["h"] < 252 else 0 for _, _, q in layer), flush=True)
if best:
    print("TOP after", best[0], "frames (old 83):", best[2], flush=True)
    ins = [b for act in best[1] for b in ["+".join(act)] * 2]
    e.mload(root)
    for b in ins: e.step(tuple(v for v in b.split("+") if v), 1)
    for i in range(14): e.step(("Right", "A"), 1)
    land = None
    for i in range(320):
        e.step(("Right",), 1); q = rd()
        if q["lives"] < L0 or q["hp"] < 47: print("hurt in the finish", q); break
        if q["x"] >= 400 and q["z"] == 0: land = best[0] + 14 + i + 1; break
    print("landed at", land, "(old 244)", rd(), flush=True)
    json.dump({"inputs": ins, "top": best[0], "landed": land}, open("knowledge/tubeclimb.json", "w"))
else:
    print("no top found", flush=True)
e.close()
