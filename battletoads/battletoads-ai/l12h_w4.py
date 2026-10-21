"""L12h stage 4 v4 (walker juggle ending ON the lower spring): hits 1-2 running kick + B held (opening hop length scanned); hit 3 air
kick; hit 4 air kick while jumping PAST the walker so that the toad lands on the floor to its LEFT, ahead of the lower spring; hit 5 =
jump + kick to the Right (anim 38, normal jump physics), drifting Left so that the descent lands on the spring as it arrives.
    python l12h_w4.py [out=w4]   -> piece <out> / bookmark L12h_<out> (standing on the lower spring, walker dead)"""
import json, sys
from l12h_lib import *
out = sys.argv[1] if len(sys.argv) > 1 else "w4"
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
# ---- stage 1-2
st12 = []
for a in (1, 2, 4, 7, 10, 14):
    for n in range(30, 50):
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
print("stage 1-2:", [(t[0], t[7], t[4], "toad", t[5], "walker", t[6]) for t in st12[:10]], flush=True)
for t in st12[6:]: e.mfree(t[1])
st12 = st12[:6]
def kick_stage(nodes, target, keep, want_left, label):
    out_ = []
    for node in nodes:
        sid, k, seq, par = node[1], node[2], node[3], node[4]
        for gh in ("", "Left"):
            r = Run(sid, k, seq)
            if not to_ground(r, gh): continue
            g = e.msave(); kg = r.k; sg = list(r.seq)
            for pre in (("Left", ""), (), ("",)):
                for ja in (1, 2, 4, 7, 10):
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
                        for hl in ((0, 6, 12, 99) if not want_left else (6, 12, 18, 24, 99)):
                            r = Run(h, kh, sh)
                            if not to_ground(r, "Left", nleft=hl) or not r.ok(): continue
                            f = foe(r.s); s = r.s
                            if not f: continue
                            rel = dx(s["x"], f[0][0])                    # toad minus walker
                            if want_left and not (s["H"] <= 4770 and -45 <= rel <= -4): continue
                            if not want_left and not (s["H"] <= 4770 and rel >= 4): continue
                            out_.append((r.k, e.msave(), r.k, list(r.seq), par + ((gh, pre, ja, bd, hl),), s["x"], f[0][0], spring(s)))
                        e.mfree(h)
            e.mfree(g)
    out_.sort(key=lambda t: t[0])
    kept = []; seenk = set()
    for t in out_:
        key = (t[5] // 5, t[6] // 5, t[0] // 2)
        if key in seenk or len(kept) >= keep: e.mfree(t[1]); continue
        seenk.add(key); kept.append(t)
    print(label, len(out_), "results; kept", [(t[0], "toad", t[5], "walker", t[6], "spring", t[7]) for t in kept[:12]], flush=True)
    return kept
st3 = kick_stage(st12, 31, 10, False, "stage 3:")
if not st3: raise SystemExit("no third hit")
st4 = kick_stage(st3, 15, 30, True, "stage 4 (landing left of the walker):")
if not st4: raise SystemExit("no fourth hit with the toad left of the walker")
# ---- stage 5: jump + kick Right, drift Left onto the spring
res = []
for node in st4:
    sid, k, seq, par = node[1], node[2], node[3], node[4]
    for pre in (("Right",), (), ("Right", ""), ("",), ("Right", "Right")):
        for ja in (1, 2, 4, 7, 10):
            for bd in (1, 2, 3, 4):
                for jd in ("", "Right"):
                    r = Run(sid, k, seq)
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
                    for hold in ("Left", "", "Right"):
                        for hl in (99, 20, 10):
                            r = Run(h, kh, sh); board = None
                            for i in range(80):
                                s = r.st(hold if i < hl else "")
                                if not r.ok(): break
                                if onspring(s) and s["an"] in IDLE: board = r.k; break
                                if s["z"] == 0 and s["an"] in IDLE: break
                            if board: res.append((board, kill, list(r.seq), par + ((pre, ja, bd, jd, hold, hl),), r.s["x"], spring(r.s)))
                    e.mfree(h)
res.sort(key=lambda t: (t[0], t[1]))
for t in res[:12]: print("on the spring at", t[0], "kill", t[1], "x", t[4], "spring", t[5], t[3], flush=True)
if res:
    b = res[0]
    save_piece(out, p["base"], p["base_k"], p["inputs"] + b[2], kill=b[1], board=b[0])
    e.load(p["base"]); run(e, p["inputs"] + b[2]); e.save("L12h_" + out); s = rd(e); print("saved", out, b[0], b[1], s["x"], s["H"], s["z"], s["an"], spring(s), "cam", s["cam"])
else: print("no line ends on the spring")
e.close()
