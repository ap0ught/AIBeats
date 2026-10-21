"""L12h stage 4, last blow: from the state after the walker's fourth hit (piece w2h4_N: toad riding the lower spring, walker at 15 hp)
find the input line that kills it and has the toad STANDING on the lower spring again as early as possible.
Layered search over 2-frame actions; phase A = to the kill (many distinct kill states kept), phase B = back onto the spring.
    python l12h_w5.py [piece=w2h4_0] [out=w3]  -> piece <out> / bookmark L12h_<out>"""
import sys, json
from l12h_lib import *
pn = sys.argv[1] if len(sys.argv) > 1 else "w2h4_0"; out = sys.argv[2] if len(sys.argv) > 2 else "w3"
p = load_piece(pn); k0 = p["base_k"] + len(p["inputs"])
e = BizHawk(log_name=f"fix_l12h_{out}.log"); e.load(p["base"]); run(e, p["inputs"]); root = e.msave()
def foe(s): return [(d[1], d[2], d[3]) for d in s["objs"] if d[0] == 0x62]
def hpw(s):
    f = foe(s); return f[0][2] if f else None
def spring(s): return (ob(s, 0x36, 4800, 40) or [None])[0]
def onspring(s):
    sp = spring(s)
    return sp is not None and s["z"] == 0 and 4798 <= s["H"] <= 4812 and abs(dx(s["x"], sp)) <= 15 and s["an"] in (1, 2, 3, 4, 5, 6, 7, 8)
ACTA = ["", "Left", "Right", "A", "Left+A", "Right+A", "B", "Left+B", "Right+B", "A+B"]
ACTB = ["", "Left", "Right", "A", "Left+A", "Right+A"]
def key(s):
    f = foe(s); sp = spring(s)
    return (dx(s["x"], sp) if sp is not None else s["x"], s["H"], s["z"], s["an"], s["face"], s["spd"] // 16, f[0] if f else None)
s0 = rd(e); print("root", k0, s0["x"], s0["H"], s0["z"], s0["an"], "spring", spring(s0), "walker", foe(s0), flush=True)
# ---- phase A
layer = [(root, [], s0)]; seen = {key(s0)}; kills = []
for depth in range(1, 40):
    nxt = []
    for sid, path, s in layer:
        for a in ACTA:
            e.mload(sid); dead = False; s2 = None
            for i in range(2):
                e.step(bt(a), 1); s2 = rd(e)
                if not alive(s2) or s2["H"] < 4700: dead = True; break
            if dead: continue
            if hpw(s2) == 0 or (not foe(s2) and hpw(s) is not None):
                kills.append((depth * 2, e.msave(), path + [a, a], s2)); continue
            kk = key(s2) + (depth,)
            if kk in seen: continue
            seen.add(kk); nxt.append((e.msave(), path + [a, a], s2))
    for sid, _, _ in layer:
        if sid != root: e.mfree(sid)
    # prefer states near the walker, cap
    def rk(n):
        s = n[2]; f = foe(s)
        return abs(dx(s["x"], f[0][0])) + abs(s["H"] - f[0][1]) / 2 if f else 999
    nxt.sort(key=rk); 
    for n in nxt[500:]: e.mfree(n[0])
    layer = nxt[:500]
    print("A depth", depth, "states", len(layer), "kills", len(kills), flush=True)
    if len(kills) >= 60 or (kills and depth * 2 >= kills[0][0] + 12) or not layer: break
print("kill frames:", sorted(set(k0 + k[0] for k in kills))[:10], flush=True)
json.dump([dict(kf=k[0], path=k[2], x=k[3]["x"], H=k[3]["H"], an=k[3]["an"], z=k[3]["z"]) for k in kills], open(FIX / f"L12h_{out}_kills.json", "w"))
for k in kills[:10]: print("  kill path", k[2], "toad", k[3]["x"], k[3]["H"], k[3]["z"], k[3]["an"], "spring", spring(k[3]), flush=True)
# ---- phase B: from every kill state, onto the spring
best = None
kills.sort(key=lambda k: k[0])
uniq = []; seenu = set()
for kk_ in kills:
    ku = key(kk_[3])
    if ku in seenu: continue
    seenu.add(ku); uniq.append(kk_)
print(len(uniq), "distinct kill states", flush=True)
for kf, sid, path, s in uniq[:12]:
    layer = [(sid, [])]; seenb = set(); found = None
    lim = (best[0] - k0 - kf) // 2 if best else 70
    for depth in range(1, max(lim, 1) + 1):
        nxt = []
        for bsid, bpath in layer:
            for a in ACTB:
                e.mload(bsid); ok = True; s2 = None
                for i in range(2):
                    e.step(bt(a), 1); s2 = rd(e)
                    if not alive(s2) or s2["H"] < 4700: ok = False; break
                    if onspring(s2): found = (kf + (depth - 1) * 2 + i + 1, bpath + [a] * (i + 1)); break
                if found: break
                if not ok: continue
                kk = key(s2) + (depth,)
                if kk in seenb: continue
                seenb.add(kk); nxt.append((e.msave(), bpath + [a, a], s2))
            if found: break
        for bsid, _ in layer:
            if bsid != sid: e.mfree(bsid)
        if found: 
            for n in nxt: e.mfree(n[0])
            break
        def rkb(n):
            s = n[2]; sp = spring(s)
            return (abs(dx(s["x"], sp)) if sp is not None else 999) + abs(s["H"] - 4805) / 2
        nxt.sort(key=rkb)
        for n in nxt[300:]: e.mfree(n[0])
        layer = [(n[0], n[1]) for n in nxt[:300]]
        if not layer: break
    print("  phase B from kill", k0 + kf, "found", found[0] if found else None, "states seen", len(seenb), flush=True)
    if found and (best is None or k0 + found[0] < best[0]):
        best = (k0 + found[0], k0 + kf, path + found[1]); print("kill at", k0 + kf, "-> on the spring at", best[0], flush=True)
if best:
    save_piece(out, p["base"], p["base_k"], p["inputs"] + best[2], kill=best[1], board=best[0])
    e.load(p["base"]); run(e, p["inputs"] + best[2]); e.save("L12h_" + out); s = rd(e)
    print("saved", out, "kill", best[1], "on the spring", best[0], s["x"], s["H"], s["z"], s["an"], "spring", spring(s), "walker", foe(s), "cam", s["cam"])
e.close()
