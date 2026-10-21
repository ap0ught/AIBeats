"""L12h stage 7: face 4's exit and the top. From the face-4 pole (piece with face4 = spawn frame S4): drop onto the upper spring when it
passes below (release from S4+351), pump at once, dash launch Right to the static spring ledge (64, H 4936), then L12g's own inputs from its
ledge landing (old frame 8085) re-synchronised landing by landing (standing waits scanned), to the level's end (level byte 13).
    python l12h_s7.py <piece> <out>   -> piece <out> (inputs to the frame the level byte turns 13), bookmark L12h_<out>_end0"""
import sys, json
from l12h_lib import *
pn, out = sys.argv[1], sys.argv[2]
p = load_piece(pn); S4 = p["face4"]; k0 = p["base_k"] + len(p["inputs"])
G = seg("L12g")
REF = json.load(open(FIX / "L12h_topref.json"))          # the improved top line (l12h_topref.py): inputs from the ledge landing, its landings
T = REF["inputs"]; lands = [tuple(l) for l in REF["landings"]]
print("reference top:", len(T), "frames from the ledge to the level end; landings", lands, flush=True)
e = BizHawk(log_name=f"fix_l12h_{out}.log"); e.load(p["base"]); run(e, p["inputs"]); root = e.msave()
s = rd(e); print("start", k0, "pole", s["x"], s["H"], s["an"], "S4", S4, flush=True)
def usp(s): return (ob(s, 0x36, 4857, 40) or [None])[0]
class Run:
    def __init__(self, sid, k, seq): e.mload(sid); self.k = k; self.seq = list(seq); self.s = rd(e)
    def st(self, b):
        e.step(bt(b), 1); self.k += 1; self.seq.append(b); self.s = rd(e); return self.s
    def ok(self): return alive(self.s)
# ---- 7a: drop onto the upper spring
drops = []
for t in range(max(S4 + 351, k0), S4 + 351 + 262):
    r = Run(root, k0, [])
    while r.k < t: r.st("")
    r.st("Down")
    if r.s["an"] in (94, 95, 96): r.st("Down")
    land = None
    for i in range(70):
        s = r.st("")
        if not r.ok(): break
        if s["z"] == 0: land = (r.k, s["x"], s["H"], usp(s)); break
    if land and 4858 <= land[2] <= 4872 and land[3] is not None and abs(dx(land[1], land[3])) <= 15:
        drops.append((land[0], t, e.msave(), r.k, list(r.seq)))
print("7a: drops landing on the upper spring:", [(d[1], d[0]) for d in drops][:30], flush=True)
if not drops: raise SystemExit("no drop lands on the upper spring")
# ---- 7b: pump, launch Right to the ledge
ledge = []
for land_k, t, sid, k, seq in drops[:3]:
    for w in range(0, 24, 2):
        r = Run(sid, k, seq)
        for i in range(w): r.st("")
        if r.s["z"] != 0: continue
        e2 = e.msave(); L = None
        for i in range(45):
            e.step(("A",), 1)
            if rd(e)["z"] == 8: L = r.k + i + 1; break
        e.mload(e2); e.mfree(e2)
        if L is None: continue
        ws = e.msave(); kw = r.k; sw = list(r.seq)
        for dash in (True, False):
            for walk in (0, 12):                      # frames of Right+A at the start of the pump (creep Right on the spring)
                r = Run(ws, kw, sw)
                while r.k < L - 3: r.st("Right+A" if r.k - kw < walk else "A")
                for b in (["Right+A", "A", "Right+A"] if dash else ["A", "A", "Right+A"]): r.st(b)
                if r.s["z"] != 8: continue
                la = e.msave(); kl = r.k; sl = list(r.seq)
                for hd in (36, 48, 60, 80):
                    r = Run(la, kl, sl)
                    for i in range(100):
                        s = r.st("Right+A" if i < hd else "A")
                        if not r.ok(): break
                        if s["z"] == 0:
                            if 4936 <= s["H"] <= 4946: ledge.append((r.k, s["x"], dict(t=t, w=w, L=L, dash=dash, walk=walk, hd=hd), e.msave(), list(r.seq)))
                            break
                e.mfree(la)
        e.mfree(ws)
    if ledge and min(x[0] for x in ledge) < land_k + 60: break
ledge.sort(key=lambda x: (x[0], abs(x[1] - 51)))
print("7b: ledge landings:", [(x[0], x[1], x[2]) for x in ledge[:6]], flush=True)
if not ledge: raise SystemExit("no ledge landing")
# ---- 7c: the old route from the ledge, re-synchronised at every landing
def walk_top(sid, k, seq):
    cur = sid; j = 0; kk = k; sq = list(seq); log = []
    for (j1, x1, H1) in lands:
        lead = 0
        while j + lead < j1 and T[j + lead] == "": lead += 1
        found = None
        for wv in list(range(0, 64, 1)) + list(range(-1, -lead - 1, -1)) + list(range(64, 262, 2)):
            e.mload(cur); pre = [""] * max(wv, 0); run(e, pre); sq2 = list(pre); hit = None
            for i in range(j - min(wv, 0), min(j1 + 14, len(T))):
                e.step(bt(T[i]), 1); sq2.append(T[i]); s = rd(e)
                if not alive(s): break
                if i + 1 >= j1 - 12 and s["z"] == 0 and abs(s["H"] - H1) <= 2 and abs(dx(s["x"], x1)) <= 8: hit = (i + 1, s["x"], s["H"]); break
            if hit: found = (wv, sq2, hit); break
        if not found: return None, f"STUCK before reference landing {j1} (from {j}, our frame {kk})", log
        wv, sq2, hit = found
        e.mload(cur); run(e, sq2); new = e.msave()
        if cur != sid: e.mfree(cur)
        cur = new; kk += len(sq2); sq += sq2; j = j1; log.append((j1, wv, kk))
    e.mload(cur); end = None
    for i in range(j, len(T) + 400):
        b = T[i] if i < len(T) else "A"
        e.step(bt(b), 1); sq.append(b); kk += 1
        m = e.ram(0, 0x800)
        if m[0x10] == 13: end = kk; break
        if m[0x10] == 5 and m[0x51A] < 47: return None, "hurt at the top", log
    if end is None: return None, "no level end", log
    return (end, sq, e.msave()), "ok", log
best = None
for lk, lx, par, sid, seq in ledge[:6]:
    r, msg, log = walk_top(sid, lk, seq)
    print("7c from ledge", lk, lx, par, "->", msg, (r[0] if r else None), "waits", [(a, b) for a, b, c in log if b != 0], flush=True)
    if r and (best is None or r[0] < best[0]): best = (r[0], r[1], r[2], par)
if not best: raise SystemExit("top walk failed")
end, seq, sid, par = best
save_piece(out, p["base"], p["base_k"], p["inputs"] + seq, face4=S4, end=end, params=par)
e.mload(sid); m = e.ram(0, 0x800); e.save(f"L12h_{out}_end0")
print("saved", out, "level byte 13 at", end, "| $0B,$0C", m[0x0B], m[0x0C], "hp", m[0x51A], "lives", m[0x11], "score", bytes(m[0x5F4:0x5FA]).hex(), flush=True)
e.close()
