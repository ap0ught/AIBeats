"""L12h stage 4 v5 (walker juggle, finish variants): hits 1-2 (opening hop scanned), hit 3 with the landing spot varied, hit 4,
then by where the toad stands:  L = on the floor LEFT of the walker with the spring still coming -> jump + kick Right, drift Left, come
down on the spring;  R = on the floor right of it -> sprint ram Left (the kill carries the toad on), then catch the spring.
    python l12h_w7.py [out=w7]  -> piece <out> / bookmark L12h_<out> (standing on the lower spring, walker dead)"""
import json, sys
from l12h_lib import *
out = sys.argv[1] if len(sys.argv) > 1 else "w7"
p = load_piece("s3c"); k0 = p["base_k"] + len(p["inputs"])
e = BizHawk(log_name=f"fix_l12h_{out}.log"); e.load(p["base"]); run(e, p["inputs"]); root = e.msave()
def foe(s): return [(d[1], d[2], d[3]) for d in s["objs"] if d[0] == 0x62]
def hpw(s):
    f = foe(s); return f[0][2] if f else None
def spring(s): return (ob(s, 0x36, 4800, 40) or [None])[0]
IDLE = (1, 2, 3, 4, 5, 6, 7, 8)
def onspring(s):
    sp = spring(s)
    return sp is not None and s["z"] == 0 and 4798 <= s["H"] <= 4812 and abs(dx(s["x"], sp)) <= 15
class Run:
    def __init__(self, sid, k, seq): e.mload(sid); self.k = k; self.seq = list(seq); self.s = rd(e)
    def st(self, b):
        e.step(bt(b), 1); self.k += 1; self.seq.append(b); self.s = rd(e); return self.s
    def ok(self): return alive(self.s) and self.s["H"] >= 4700
def to_ground(r, hold="", maxf=70, nleft=99):
    for i in range(maxf):
        if r.s["z"] == 0 and r.s["an"] in IDLE: return True
        r.st(hold if i < nleft else "")
        if not r.ok(): return False
    return False
st12 = []
for a in (2, 4, 7, 10):
    for n in range(28, 42):
        r = Run(root, k0, [])
        for i in range(a): r.st("Left+A")
        for i in range(n): r.st("Left")
        if not foe(r.s): continue
        r.st("")
        h1 = h2 = None
        for i in range(60):
            s = r.st("Left+B")
            if not r.ok(): break
            h = hpw(s)
            if h1 is None and h is not None and h <= 63: h1 = r.k
            if h is not None and h <= 47: h2 = r.k; break
        if h2 is None: continue
        st12.append((h2, e.msave(), r.k, list(r.seq), ((a, n),), r.s["x"], foe(r.s)[0][0], h1))
st12.sort(key=lambda t: t[0])
best12 = st12[0][0]; keep12 = [t for t in st12 if t[0] == best12][:6]
print("stage 1-2:", [(t[0], t[7], t[4], "toad", t[5], "walker", t[6]) for t in keep12], flush=True)
def kick_stage(nodes, target, hls):
    out_ = []
    for node in nodes:
        sid, k, seq, par = node[1], node[2], node[3], node[4]
        for gh in ("", "Left"):
            r = Run(sid, k, seq)
            if not to_ground(r, gh): continue
            g = e.msave(); kg = r.k; sg = list(r.seq)
            for pre in (("Left", ""), (), ("",)):
                for ja in (1, 2, 4, 7):
                    for bd in (2, 3, 4):
                        r = Run(g, kg, sg)
                        for b in pre: r.st(b)
                        r.st("Left+A")
                        for i in range(1, bd): r.st("A" if i < ja else "")
                        r.st("Left+B+A" if bd < ja else "Left+B")
                        hit = None
                        for i in range(30):
                            s = r.st("Left+A" if bd + 1 + i < ja else "Left")
                            if not r.ok(): break
                            if hpw(s) is not None and hpw(s) <= target: hit = r.k; break
                        if hit is None: continue
                        h = e.msave(); kh = r.k; sh = list(r.seq)
                        for hl in hls:
                            r = Run(h, kh, sh)
                            if not to_ground(r, "Left", nleft=hl) or not r.ok(): continue
                            f = foe(r.s); s = r.s
                            if not f: continue
                            out_.append(dict(ready=r.k, sid=e.msave(), k=r.k, seq=list(r.seq), par=par + ((gh, pre, ja, bd, hl),), x=s["x"], H=s["H"], wx=f[0][0], sp=spring(s)))
                        e.mfree(h)
            e.mfree(g)
    return out_
r3 = kick_stage([(t[0], t[1], t[2], t[3], t[4]) for t in keep12], 31, (0, 6, 12, 18, 24, 99))
r3 = [t for t in r3 if t["H"] <= 4770]
b3 = min(t["ready"] for t in r3); buckets = {}
for t in sorted(r3, key=lambda t: t["ready"]):
    if t["ready"] > b3 + 8: continue
    buckets.setdefault((t["x"] // 10, t["wx"] // 12), t)
st3 = sorted(buckets.values(), key=lambda t: (t["ready"], t["x"]))[:14]
print("stage 3:", len(r3), "floor landings; kept", [(t["ready"], "toad", t["x"], "walker", t["wx"], "spring", t["sp"]) for t in st3], flush=True)
r4 = kick_stage([(t["ready"], t["sid"], t["k"], t["seq"], t["par"]) for t in st3], 15, (4, 10, 16, 24, 99))
catL = [t for t in r4 if t["H"] <= 4770 and dx(t["x"], t["wx"]) <= -3 and t["sp"] is not None and dx(t["sp"], t["x"]) > 12]
catR = [t for t in r4 if t["H"] <= 4770 and dx(t["x"], t["wx"]) >= 3]
catS = [t for t in r4 if t["H"] >= 4798]
print("stage 4:", len(r4), "landings: L", len(catL), "R", len(catR), "on the spring", len(catS), flush=True)
print("  L:", sorted([(t["ready"], "toad", t["x"], "walker", t["wx"], "spring", t["sp"]) for t in catL])[:10], flush=True)
print("  R:", sorted([(t["ready"], "toad", t["x"], "walker", t["wx"], "spring", t["sp"]) for t in catR])[:10], flush=True)
res = []
# ---- finish L: jump + kick Right, then Left onto the spring
catL.sort(key=lambda t: t["ready"])
for t in catL[:25]:
    for pre in (("Right",), (), ("Right", "")):
        for jd in ("", "Right", "Left"):
            for ja in (1, 2, 4, 7):
                for bd in (1, 2, 3, 4):
                    r = Run(t["sid"], t["k"], t["seq"])
                    for b in pre: r.st(b)
                    r.st((jd + "+A").strip("+"))
                    for i in range(1, bd): r.st("A" if i < ja else "")
                    r.st("Right+B+A" if bd < ja else "Right+B")
                    kill = None
                    for i in range(30):
                        s = r.st("A" if bd + 1 + i < ja else "")
                        if not r.ok(): break
                        if hpw(s) == 0: kill = r.k; break
                    if kill is None: continue
                    h = e.msave(); kh = r.k; sh = list(r.seq)
                    for hold, hl in (("Left", 99), ("Left", 16), ("Left", 8), ("", 0), ("Right", 8)):
                        r = Run(h, kh, sh); board = None
                        for i in range(80):
                            s = r.st(hold if i < hl else "")
                            if not r.ok(): break
                            if onspring(s) and s["an"] in IDLE: board = r.k; break
                            if s["z"] == 0 and s["an"] in IDLE: break
                        if board: res.append((board, kill, list(r.seq), "L", t["par"] + ((pre, jd, ja, bd, hold, hl),), r.s["x"], spring(r.s)))
                    e.mfree(h)
print("finish L:", sorted([(x[0], x[1]) for x in res])[:6], flush=True)
# ---- finish R: sprint ram Left, then catch the spring
catR.sort(key=lambda t: t["ready"])
bestR = None
for t in catR[:25]:
    for pre in (("Left", ""), (), ("",), ("Left", "", "Left")):
        for jump in (("Left+B",), ("Left+A", "Left+B"), ("A", "Left+B"), ("Left+A+B",)):
            r = Run(t["sid"], t["k"], t["seq"])
            for b in pre: r.st(b)
            for b in jump: r.st(b)
            kill = None
            for i in range(30):
                s = r.st("Left")
                if not r.ok(): break
                if hpw(s) == 0: kill = r.k; break
            if kill is None: continue
            if not to_ground(r, "Left", maxf=60) or not r.ok(): continue
            sp = spring(r.s)
            if sp is None: continue
            gap = dx(r.s["x"], sp)                                # > 0: the spring is ahead (to the Left)
            est = r.k + max(gap, 0) + 12
            if bestR is not None and est >= bestR: continue
            c = e.msave(); kc = r.k; sc = list(r.seq); board = None
            for wj in range(max(0, gap - 30), gap + 40, 1):
                r = Run(c, kc, sc); r.st("Left"); r.st("")
                for i in range(wj): r.st("Left")
                if not r.ok() or r.s["z"] != 0: continue
                r.st(""); r.st("Left"); r.st("")
                for i in range(50):
                    s = r.st("Left+A" if i < 6 else "Left")
                    if not r.ok(): break
                    if onspring(s) and s["an"] in IDLE: board = r.k; break
                    if s["z"] == 0 and i > 3: break
                if board: break
            e.mfree(c)
            if board:
                res.append((board, kill, list(r.seq), "R", t["par"] + ((pre, jump),), r.s["x"], spring(r.s)))
                if bestR is None or board < bestR: bestR = board; print("  R: kill", kill, "on the spring at", board, flush=True)
res.sort(key=lambda t: (t[0], t[1]))
for t in res[:10]: print("on the spring at", t[0], "kill", t[1], t[3], "x", t[5], "spring", t[6], t[4][-1], flush=True)
if res:
    b = res[0]
    save_piece(out, p["base"], p["base_k"], p["inputs"] + b[2], kill=b[1], board=b[0])
    e.load(p["base"]); run(e, p["inputs"] + b[2]); e.save("L12h_" + out); s = rd(e); print("saved", out, b[0], b[1], s["x"], s["H"], s["z"], s["an"], spring(s), "cam", s["cam"])
else: print("no line ends on the spring")
e.close()
