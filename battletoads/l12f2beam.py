"""Follow the TAS's path from our spring landing (5346) to the face-2 pole: 2-frame macros, width W, score = distance to the
TAS toad at the aligned frame (TAS j = our f + 74091 - 5218 - LAG). Goal: hanging (an 94) on the pole at x 480 with the face out.
-> knowledge/l12f2beam.json (inputs from 5346), bookmark F2B_pole"""
import json, os
from toads.emulator import BizHawk
import l12f2full as L
LAG = int(os.environ.get("LAG", 8)); W = int(os.environ.get("W", 300))
T = L.T
e = BizHawk(log_name="l12f2beam.log"); e.load("L12p_f5000")
for f in range(5000, 5225): e.step(tuple(v for v in L.ins[f].split('+') if v), 1)
f = 5225
for b in L.build({}):
    e.step(b, 1); f += 1
    if f == 5346: break
e.save("F2B_spring5346")
def rd():
    m = e.ram(0, 0x800)
    return dict(x=m[0x3FD] | m[0x3EE] << 8, h=m[0x439], H=m[0x439] | m[0x42A] << 8, z=m[0x475], an=m[0x3B5], hp=m[0x51A], lives=m[0x11],
                face=any(m[0x3C1+q]==0x60 for q in range(2,15)))
ACTS = [(), ("A",), ("Right",), ("Left",), ("Right","A"), ("Left","A")]
frontier = [(e.msave(), [], None)]; goal = None
for step in range(110):
    nxt = []; seen = set(); f = 5346 + 2 * (step + 1)
    j = f + 74091 - 5218 - LAG; t = T.get(j, T[max(T)])
    for sid, path, face in frontier:
        for a in ACTS:
            e.mload(sid); e.step(a, 2); s = rd()
            if s["hp"] < 47 or s["lives"] < 4: continue
            fc = face if face else (f if s["face"] else None)
            if s["an"] in (94, 95, 96) and s["x"] == 480 and fc: goal = (e.msave(), path + ["+".join(a)] * 2, fc, f); break
            k = (s["x"], s["H"], s["z"], s["an"] // 4, fc is not None)
            if k in seen: continue
            seen.add(k)
            dx = min((s["x"] - t["x"]) % 512, (t["x"] - s["x"]) % 512); dh = abs(((s["h"] - t["h"]) + 128) % 256 - 128)
            nxt.append((dx + dh + (0 if fc else 30), e.msave(), path + ["+".join(a)] * 2, fc))
        if goal: break
    for sid, _, _ in frontier: e.mfree(sid)
    if goal: break
    nxt.sort(key=lambda n: n[0])
    for n in nxt[W:]: e.mfree(n[1])
    frontier = [(n[1], n[2], n[3]) for n in nxt[:W]]
    if step % 10 == 0: print("step", step, "f", f, "best", nxt[0][0] if nxt else None, "TAS", j, t["x"], t["h"], flush=True)
    if not frontier: print("died out"); break
if goal:
    sid, path, fc, f = goal
    print("POLE at", f, "face spawned", fc, "(old: face 5524, pole 5514)", flush=True)
    e.mload(sid); e.save("F2B_pole")
    json.dump({"from": "F2B_spring5346", "f0": 5346, "inputs": path, "pole": f, "face": fc}, open("knowledge/l12f2beam.json", "w"))
e.close()
