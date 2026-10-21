"""L12h stage 6: face 3's exit. From the pole (piece with face3 = spawn frame S3): drop when the lower spring (0x36 H 4800) passes below
(release is possible from S3+351), pump so that the launch tops out as the camera unlocks (face gone S3+481, +10), land on the upper spring
(0x36 H 4857, spawns when the camera reaches 1104), pump again, launch to a face-4 pole (x 352 / 288, H 4944); face 4 spawns at camera 1056.
    python l12h_s6.py <piece> <out>   -> piece <out> / bookmark L12h_<out> (hanging on the face-4 pole) with face4 = spawn frame."""
import sys, json
from l12h_lib import *
pn, out = sys.argv[1], sys.argv[2]
p = load_piece(pn); S3 = p["face3"]; k0 = p["base_k"] + len(p["inputs"])
e = BizHawk(log_name=f"fix_l12h_{out}.log"); e.load(p["base"]); run(e, p["inputs"]); root = e.msave()
s = rd(e); print("start", k0, "pole", s["x"], s["H"], s["an"], "S3", S3, flush=True)
def lsp(s): return (ob(s, 0x36, 4800, 40) or [None])[0]
def usp(s): return (ob(s, 0x36, 4857, 40) or [None])[0]
class Run:
    def __init__(self, sid, k, seq): e.mload(sid); self.k = k; self.seq = list(seq); self.s = rd(e)
    def st(self, b):
        e.step(bt(b), 1); self.k += 1; self.seq.append(b); self.s = rd(e); return self.s
    def ok(self): return alive(self.s)
def launch_variants(sid, k, seq, waits, accept, maxfl=110, dirs=("Left", "Right", ""), hds=(6, 12, 20, 28, 36, 48, 70)):
    """from a standing-on-a-spring state: wait w, hold A (pump), launch (dash or not) in dir, hold dir hd frames; accept(run) -> result or None"""
    res = []
    for w in waits:
        r = Run(sid, k, seq)
        for i in range(w): r.st("")
        if not r.ok() or r.s["z"] != 0: continue
        e2 = e.msave(); L = None
        for i in range(45):
            e.step(("A",), 1)
            if rd(e)["z"] == 8: L = r.k + i + 1; break
        e.mload(e2); e.mfree(e2)
        if L is None: continue
        base_seq = list(r.seq); kb = r.k; wsid = e.msave()
        for d in dirs:
            for dash in ((True, False) if d else (False,)):
                r = Run(wsid, kb, base_seq)
                while r.k < L - 3: r.st("A")
                for b in ([d + "+A", "A", d + "+A"] if dash else ["A", "A", (d + "+A").strip("+")]): r.st(b)
                if r.s["z"] != 8: continue
                la = e.msave(); kl = r.k; sl = list(r.seq)
                for hd in (hds if d else (0,)):
                    r = Run(la, kl, sl); ev = {}
                    for i in range(maxfl):
                        s = r.st((d + "+A").strip("+") if i < hd else "A")
                        if not r.ok(): break
                        got = accept(r, ev)
                        if got is not None:
                            res.append((got, dict(w=w, L=L, d=d, dash=dash, hd=hd), e.msave(), r.k, list(r.seq))); break
                        if s["z"] == 0: break
                e.mfree(la)
        e.mfree(wsid)
    return res
# ---- 6a: the drop onto the lower spring
drops = []
for t in range(max(S3 + 351, k0), S3 + 351 + 262):
    r = Run(root, k0, [])
    while r.k < t: r.st("")
    r.st("Down")
    if r.s["an"] in (94, 95, 96): r.st("Down")
    land = None
    for i in range(70):
        s = r.st("")
        if not r.ok(): break
        if s["z"] == 0: land = (r.k, s["x"], s["H"], lsp(s)); break
    if land and 4798 <= land[2] <= 4812 and land[3] is not None and abs(dx(land[1], land[3])) <= 15:
        drops.append((land[0], t, e.msave(), r.k, list(r.seq)))
print("6a: drops landing on the lower spring:", [(d[1], d[0]) for d in drops][:40], flush=True)
drops = [d for d in drops if d[0] <= S3 + 470]
if not drops:
    # floor variant: the spring has just passed; drop as soon as the pole lets go, land on the ring floor (H 4766), sprint Left after
    # the spring (3 px/frame against its 2) and dash-jump onto it
    print("6a': no direct landing in time - dropping to the floor and chasing the spring", flush=True)
    IDLE = (1, 2, 3, 4, 5, 6, 7, 8)
    for t in range(max(S3 + 351, k0), S3 + 351 + 6):
        r = Run(root, k0, [])
        while r.k < t: r.st("")
        r.st("Down")
        if r.s["an"] in (94, 95, 96): r.st("Down")
        ok = False
        for i in range(80):
            s = r.st("Left")
            if not r.ok(): break
            if s["z"] == 0: ok = True; break
        if not ok or lsp(r.s) is None: continue
        c = e.msave(); kc = r.k; sc = list(r.seq); gap = dx(r.s["x"], lsp(r.s)); got = None
        print("   drop", t, "on the floor at", kc, "x", r.s["x"], "spring", lsp(r.s), "gap", gap, flush=True)
        for wj in range(max(0, gap - 40), gap + 60):
            r = Run(c, kc, sc); r.st(""); r.st("Left"); r.st("")
            for i in range(wj): r.st("Left")
            if not r.ok() or r.s["z"] != 0: continue
            r.st(""); r.st("Left"); r.st("")
            for i in range(50):
                s = r.st("Left+A" if i < 6 else "Left")
                if not r.ok(): break
                if s["z"] == 0 and 4798 <= s["H"] <= 4812 and lsp(s) is not None and abs(dx(s["x"], lsp(s))) <= 15:
                    for j in range(6):                                   # settle: walk in from the edge, then it must still carry the toad
                        s = r.st("Left" if dx(r.s["x"], lsp(r.s)) > 3 else "")
                    if r.ok() and r.s["z"] == 0 and 4798 <= r.s["H"] <= 4812 and abs(dx(r.s["x"], lsp(r.s))) <= 12: got = r.k
                    break
                if s["z"] == 0 and i > 3: break
            if got: break
        if got:
            drops.append((got, t, e.msave(), r.k, list(r.seq))); print("   on the spring at", got, "(S3+%d)" % (got - S3), flush=True)
        e.mfree(c)
    if not drops: raise SystemExit("floor variant failed")
    drops.sort(key=lambda d: d[0]); drops = drops[:2]
    save_piece(out + "_board", p["base"], p["base_k"], p["inputs"] + drops[0][4], face3=S3, board=drops[0][0])
    e.mload(drops[0][2]); e.save("L12h_" + out + "_board")
pick = [drops[0], drops[len(drops) // 2], drops[-1]] if len(drops) >= 3 else drops
# ---- 6b: lower spring -> upper spring
def acc_upper(r, ev):
    s = r.s
    if s["z"] == 0 and 4858 <= s["H"] <= 4872 and usp(s) is not None and abs(dx(s["x"], usp(s))) <= 15: return (r.k, s["x"])
    return None
ups = []
for land_k, t, sid, k, seq in pick:
    waits = [w for w in range(0, 80) if S3 + 436 <= land_k + w + 25][:34]
    rs = launch_variants(sid, k, seq, waits, acc_upper)
    rs.sort(key=lambda x: x[0])
    print("6b from drop", t, "landing", land_k, ":", [(x[0], x[1]) for x in rs[:4]], flush=True)
    ups += rs
ups.sort(key=lambda x: x[0])
if not ups: raise SystemExit("no upper-spring landing")
# ---- 6c: upper spring -> face-4 pole
def acc_pole(r, ev):
    s = r.s
    if s["faces"] and "f4" not in ev: ev["f4"] = r.k
    if s["an"] in (94, 95, 96) and s["H"] >= 4940 and "f4" in ev: return (ev["f4"], r.k, s["x"])
    return None
fin = []
for got, par, sid, k, seq in ups[:4]:
    rs = launch_variants(sid, k, seq, range(0, 14), acc_pole)
    rs.sort(key=lambda x: x[0])
    print("6c from upper landing", got, par, ":", [(x[0], x[1]) for x in rs[:4]], flush=True)
    fin += [(x[0], x[1], par, x[4]) for x in rs]
fin.sort(key=lambda x: x[0])
if not fin: raise SystemExit("no face-4 pole")
for i, (g, par2, par1, seq) in enumerate([fin[0]] + [x for x in fin if x[0][2] != fin[0][0][2]][:1]):
    name = out if i == 0 else out + "b"
    save_piece(name, p["base"], p["base_k"], p["inputs"] + seq, face3=S3, face4=g[0], pole=g[1], polex=g[2])
    e.load(p["base"]); run(e, p["inputs"] + seq); e.save("L12h_" + name)
    print("saved", name, "face4", g[0], "(S3+%d)" % (g[0] - S3), "pole", g[1], g[2], par1, par2, flush=True)
e.close()
