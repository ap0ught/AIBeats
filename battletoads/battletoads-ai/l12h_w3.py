"""L12h stage 4 v3 (walker juggle with landing control): hits 1-2 running kick + B held; hits 3-4 dash-jump air kicks (direction gap ->
anim 38) with the Left hold after the hit scanned so that the toad comes down on the floor to the RIGHT of the stunned walker; hit 5 =
sprint ram Left (dash + Left+B): the kill carries the toad on Left onto the lower spring as it passes.
    python l12h_w3.py   -> piece w3 / bookmark L12h_w3 (standing on the lower spring, walker dead), logs/fix/L12h_w3_results.json"""
import json, sys
from l12h_lib import *
p = load_piece("s3c"); k0 = p["base_k"] + len(p["inputs"])
e = BizHawk(log_name="fix_l12h_w3.log"); e.load(p["base"]); run(e, p["inputs"]); root = e.msave()
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
for n in range(38, 46):
    r = Run(root, k0, []); r.st("Left+A")
    for i in range(n): r.st("Left")
    if not foe(r.s): continue
    r.st("")
    h1 = h2 = None
    for i in range(70):
        s = r.st("Left+B")
        if not r.ok(): break
        h = hpw(s)
        if h1 is None and h is not None and h <= 63: h1 = r.k
        if h is not None and h <= 47: h2 = r.k; break
    if h2 is None: continue
    st12.append((h2, e.msave(), r.k, list(r.seq), (n,)))
    print("stage 1-2: n", n, "hit1", h1, "hit2", h2, "toad", r.s["x"], "walker", foe(r.s), flush=True)
def kick_stage(nodes, target, label, keep):
    out = []
    for _, sid, k, seq, par in nodes:
        for gh in ("", "Left"):
            r = Run(sid, k, seq)
            if not to_ground(r, gh): continue
            g = e.msave(); kg = r.k; sg = list(r.seq)
            for pre in (("Left", ""), (), ("",)):
                for ja in (1, 2, 4, 9):
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
                        for hl in (0, 4, 8, 12, 18, 99):
                            r = Run(h, kh, sh)
                            if not to_ground(r, "Left", nleft=hl) or not r.ok(): continue
                            f = foe(r.s)
                            out.append((r.k, e.msave(), r.k, list(r.seq), par + ((gh, pre, ja, bd, hl),), r.s["x"], r.s["H"], f[0][0] if f else None, spring(r.s)))
                        e.mfree(h)
            e.mfree(g)
    out.sort(key=lambda t: t[0])
    kept = []; seenk = set()
    for t in out:
        key = (t[5] // 6, t[6])
        if key in seenk or t[0] > out[0][0] + 10: e.mfree(t[1]); continue
        seenk.add(key); kept.append(t)
        if len(kept) >= keep: break
    print(label, [(t[0], "x", t[5], "H", t[6], "walker", t[7], "spring", t[8], t[4][-1]) for t in kept], flush=True)
    return kept
st3 = kick_stage(st12, 31, "stage 3:", 8)
if not st3: raise SystemExit("no third hit")
st4 = kick_stage([(t[0], t[1], t[2], t[3], t[4]) for t in st3], 15, "stage 4:", 24)
if not st4: raise SystemExit("no fourth hit")
res = []
for t in st4:
    sid, k, seq, par = t[1], t[2], t[3], t[4]
    f0 = t[7]; x0 = t[5]
    d = "Left" if (f0 is None or dx(f0, x0) <= 0) else "Right"
    o = "Right" if d == "Left" else "Left"
    for pre in ((), (o,), ("",), (o, ""), (d, ""), ("", ""), (d, "", d), (d, "", d, d, d)):
        for jump in (("A", d + "+B"), (d + "+A", d + "+B"), (d + "+B",), (d + "+A+B",), (d + "+A", d + "+A", d + "+B"), ("B",), (d + "+A", "", d + "+B")):
            for hold in ("Left", "", d):
                r = Run(sid, k, seq)
                for b in pre: r.st(b)
                for b in jump: r.st(b)
                kill = None
                for i in range(36):
                    s = r.st(hold)
                    if not r.ok(): break
                    if hpw(s) == 0: kill = r.k; break
                if kill is None: continue
                board = None
                for i in range(70):
                    if onspring(r.s) and r.s["an"] not in (38, 39): board = r.k; break
                    if r.s["z"] == 0 and r.s["an"] in IDLE: break
                    r.st(hold)
                    if not r.ok(): break
                if not r.ok(): continue
                res.append((board if board else 99999, kill, list(r.seq), par + ((pre, jump, hold),), r.s["x"], r.s["H"], spring(r.s), r.s["an"]))
res.sort(key=lambda t: (t[0], t[1]))
for t in res[:14]: print("on the spring at", t[0], "kill", t[1], "toad", t[4], t[5], "an", t[7], "spring", t[6], t[3][-3:], flush=True)
json.dump([dict(board=t[0], kill=t[1], seq=t[2], x=t[4], H=t[5]) for t in res[:40]], open(FIX / "L12h_w3_results.json", "w"))
if res and res[0][0] < 99999:
    b = res[0]
    save_piece("w3", p["base"], p["base_k"], p["inputs"] + b[2], kill=b[1], board=b[0])
    e.load(p["base"]); run(e, p["inputs"] + b[2]); e.save("L12h_w3"); s = rd(e); print("saved L12h_w3", b[0], b[1], s["x"], s["H"], s["z"], s["an"], spring(s))
e.close()
