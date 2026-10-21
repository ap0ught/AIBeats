"""From the ledge landing after the face-spawning launch, reach either face-2 pole (x 32 or 480, H 4504) before the wind.
4-frame macros incl. a double-tap run, width W, score = distance to the nearest pole (+ to the spring while low)."""
import json, os
from toads.emulator import BizHawk
import l12f2full as L
T = L.T; W = int(os.environ.get("W", 600)); SKIP = int(os.environ.get("SKIP", 0))
def tasbtn(j):
    p = T[j]["p"]
    if 'le' in p and 'ri' in p:
        p = p.replace('le', '').replace('ri', ''); p = '-' if p == '' else p
    return L.btn(p) if p != '-' else ()
e = BizHawk(log_name=f"l12f2topole_{SKIP}.log"); e.load("F2B_spring5346")
def rd():
    m = e.ram(0, 0x800)
    sp=[(m[0x3FD+q]|m[0x3EE+q]<<8, m[0x439+q]|m[0x42A+q]<<8) for q in range(2,15) if m[0x3C1+q]==0x36]
    return dict(x=m[0x3FD] | m[0x3EE] << 8, H=m[0x439] | m[0x42A] << 8, z=m[0x475], an=m[0x3B5], hp=m[0x51A], lives=m[0x11],
                face=any(m[0x3C1+q]==0x60 for q in range(2,15)), wind=any(m[0x3C1+q]==0x61 for q in range(2,15)), sp=sp)
f = 5346; j = 74214; face = None; pre = []
if SKIP < 0:
    for i in range(-SKIP): e.step((), 1); f += 1; pre.append("")
j += max(0, SKIP)
while True:
    b = tasbtn(j); e.step(b, 1); f += 1; j += 1; pre.append("+".join(b)); s = rd()
    if s["face"] and face is None: face = f
    if j > 74300 and s["z"] == 0: break
print("ledge landing", f, s, "face", face, flush=True)
SEQ = {"RunR": [("Right",), (), ("Right",), ("Right",)], "RunL": [("Left",), (), ("Left",), ("Left",)]}
ACTS = [(), ("A",), ("Right",), ("Left",), ("Right","A"), ("Left","A"), "RunR", "RunL"]
frontier = [(e.msave(), [])]; goal = None; f0 = f
for step in range(40):
    nxt = []; seen = set()
    for sid, path in frontier:
        for a in ACTS:
            e.mload(sid)
            fr = SEQ[a] if isinstance(a, str) else [a] * 4
            ok = True
            for b in fr:
                e.step(b, 1); s = rd()
                if s["hp"] < 47 or s["lives"] < 4: ok = False; break
                if s["an"] in (94, 95, 96): break
            if not ok: continue
            p2 = path + ["+".join(b) for b in fr]
            if s["an"] in (94, 95, 96): goal = (e.msave(), p2, s); break
            k = (s["x"], s["H"], s["z"], s["an"] // 4)
            if k in seen: continue
            seen.add(k)
            dpole = min(min((s["x"] - px) % 512, (px - s["x"]) % 512) for px in (32, 480)) + abs(4504 - s["H"])
            dsp = min((min((s["x"] - sx) % 512, (sx - s["x"]) % 512) for sx, sh in s["sp"]), default=200) if s["H"] < 4450 else 0
            nxt.append((dpole + 2 * dsp, e.msave(), p2))
        if goal: break
    for sid, _ in frontier: e.mfree(sid)
    if goal: break
    nxt.sort(key=lambda n: n[0])
    for n in nxt[W:]: e.mfree(n[1])
    frontier = [(n[1], n[2]) for n in nxt[:W]]
    if step % 5 == 0: print("step", step, "f", f0 + 4 * (step + 1), "best", nxt[0][0] if nxt else None, flush=True)
if goal:
    sid, p2, s = goal; fp = f0 + len(p2)
    e.mload(sid); w = rd()
    print("POLE at", fp, "x", s["x"], "face", face, "wind already?", w["wind"], flush=True)
    e.save(f"F2P_pole_{SKIP}")
    json.dump({"from": "F2B_spring5346", "inputs": pre + p2, "face": face, "pole": fp, "polex": s["x"]}, open(f"knowledge/l12f2topole_{SKIP}.json", "w"))
else: print("no pole", flush=True)
e.close()
