"""L12h stage 4 (walker, the TAS's juggle): from the walker's platform (piece s3c) dash-hop Left (the walker spawns), sprint Left, running
kick as it flies in (79 -> 63), B held = second kick at once (-> 47), then dash-jump kicks while it hangs stunned (-> 31 -> 15) and a last
flying blow that carries the toad Left onto the lower spring. Staged scan; keeps the best few lines per stage.
    python l12h_w.py [KEEP=3]    -> piece w / bookmark L12h_w (walker dead; where the toad lands), logs/fix/L12h_w.json"""
import json, sys
from l12h_lib import *
KEEP = int(sys.argv[1]) if len(sys.argv) > 1 else 3
p = load_piece("s3c"); k0 = p["base_k"] + len(p["inputs"])
e = BizHawk(log_name="fix_l12h_w.log"); e.load(p["base"]); run(e, p["inputs"]); root = e.msave()
def foe(s): return [(d[1], d[2], d[3]) for d in s["objs"] if d[0] == 0x62]
def hpw(s):
    f = foe(s); return f[0][2] if f else None
class Run:
    def __init__(self, sid, k, seq): e.mload(sid); self.k = k; self.seq = list(seq); self.s = rd(e)
    def st(self, b):
        e.step(bt(b), 1); self.k += 1; self.seq.append(b); self.s = rd(e); return self.s
    def ok(self): return alive(self.s) and self.s["H"] >= 4700
def wait_hit(r, hold, target, maxf=40):
    """hold `hold` until the walker's health reaches `target`; -> frame of the hit or None"""
    for i in range(maxf):
        s = r.st(hold)
        if not r.ok(): return None
        h = hpw(s)
        if h is not None and h <= target: return r.k
    return None
def to_ground(r, hold="", maxf=60):
    for i in range(maxf):
        if r.s["z"] == 0 and r.s["an"] in (1, 2, 3, 4, 5, 6, 7, 8): return True
        r.st(hold)
        if not r.ok(): return False
    return False
# ---- stage 1+2: hop, sprint, running kick, B held for the second kick
st12 = []
for n in range(28, 52):                        # frames of Left after the 1-frame dash hop before the kick
    for gap in (0, 1):
        r = Run(root, k0, [])
        r.st("Left+A")
        for i in range(n): r.st("Left")
        if not foe(r.s): continue
        for i in range(gap): r.st("")
        h1 = wait_hit(r, "Left+B", 63, 30)
        if h1 is None: continue
        h2 = wait_hit(r, "Left+B", 47, 40)
        if h2 is None: continue
        st12.append((h2, h1, n, gap, e.msave(), r.k, list(r.seq), r.s["x"], foe(r.s)))
        print("stage 1-2: n", n, "gap", gap, "hit1", h1, "hit2", h2, "toad", r.s["x"], r.s["H"], "walker", foe(r.s), flush=True)
st12.sort(key=lambda t: t[0]); st12 = st12[:KEEP]
if not st12: raise SystemExit("no double kick found")
# ---- stage 3: land, (tap) dash-jump Left, air kick -> 31
st3 = []
for h2, h1, n, gap, sid, k, seq, x, f in st12:
    r = Run(sid, k, seq)
    if not to_ground(r, ""): continue
    g = e.msave(); kg = r.k; sg = list(r.seq)
    for pre in ((), ("Left", ""), ("Left",), ("",)):
        for ja in (1, 2, 4, 8):                # frames of A in the jump
            for bd in (1, 2, 3, 4, 6, 8):      # B this many frames after the jump starts
                r = Run(g, kg, sg)
                for b in pre: r.st(b)
                for i in range(bd): r.st("Left+A" if i < ja else "Left")
                r.st("Left+A+B" if bd < ja else "Left+B")
                h3 = None
                for i in range(34):
                    s = r.st("Left+A" if bd + 1 + i < ja else "Left")
                    if not r.ok(): break
                    if hpw(s) is not None and hpw(s) <= 31: h3 = r.k; break
                if h3 is None: continue
                st3.append((h3, h2, e.msave(), r.k, list(r.seq), (n, gap, pre, ja, bd)))
st3.sort(key=lambda t: t[0]); print("stage 3:", [(t[0], t[5]) for t in st3[:6]], flush=True); st3 = st3[:KEEP]
if not st3: raise SystemExit("no third hit")
# ---- stage 4: land, jump, air kick -> 15
st4 = []
for h3, h2, sid, k, seq, par in st3:
    r = Run(sid, k, seq)
    if not to_ground(r, "Left"):
        r = Run(sid, k, seq)
        if not to_ground(r, ""): continue
    g = e.msave(); kg = r.k; sg = list(r.seq)
    for pre in ((), ("Left", ""), ("",), ("Left",)):
        for ja in (1, 2, 4, 9, 14):
            for bd in (1, 2, 3, 4, 6, 8):
                r = Run(g, kg, sg)
                for b in pre: r.st(b)
                for i in range(bd): r.st("Left+A" if i < ja else "Left")
                r.st("Left+A+B" if bd < ja else "Left+B")
                h4 = None
                for i in range(34):
                    s = r.st("Left+A" if bd + 1 + i < ja else "Left")
                    if not r.ok(): break
                    if hpw(s) is not None and hpw(s) <= 15: h4 = r.k; break
                if h4 is None: continue
                st4.append((h4, e.msave(), r.k, list(r.seq), par + (pre, ja, bd)))
st4.sort(key=lambda t: t[0]); print("stage 4:", [(t[0], t[4]) for t in st4[:6]], flush=True); st4 = st4[:KEEP]
if not st4: raise SystemExit("no fourth hit")
# ---- stage 5: land, last blow (jump + Left+B = flying ram), keep Left: land on the lower spring?
res = []
for h4, sid, k, seq, par in st4:
    r = Run(sid, k, seq)
    if not to_ground(r, ""): continue
    g = e.msave(); kg = r.k; sg = list(r.seq)
    for pre in ((), ("Right",), ("",), ("Left", ""), ("Right", "")):
        for jump in (("A", "Left+B"), ("Left+A", "Left+B"), ("Left+B",), ("Left+A", "Left+A", "Left+B"), ("A", "A", "Left+B"), ("Left+A+B",), ("B",)):
            for hold in ("", "Left"):
                r = Run(g, kg, sg)
                for b in pre: r.st(b)
                for b in jump: r.st(b)
                h5 = None; land = None
                for i in range(70):
                    s = r.st(hold)
                    if not r.ok(): break
                    if h5 is None and (hpw(s) == 0): h5 = r.k
                    if h5 and s["z"] == 0: land = (r.k, s["x"], s["H"]); break
                if h5 is None or land is None: continue
                onspring = 4800 <= land[2] <= 4812
                res.append((0 if onspring else 1, land[0], h5, land, e.msave(), r.k, list(r.seq), par + (pre, jump, hold), ob(r.s, 0x36, 4800, 40)))
res.sort(key=lambda t: t[:3])
for t in res[:10]: print("kill", t[2], "landed", t[3], "on the spring" if t[0] == 0 else "", "spring at", t[8], t[7], flush=True)
if res:
    b = res[0]
    save_piece("w", p["base"], p["base_k"], p["inputs"] + b[6], kill=b[2], landed=b[3][0], onspring=(b[0] == 0))
    e.mload(b[4]); e.save("L12h_w"); print("saved L12h_w", b[2], b[3])
    json.dump([dict(kill=t[2], landed=t[3], onspring=t[0] == 0, spring=t[8], seq=t[6]) for t in res[:20]], open(FIX / "L12h_w_results.json", "w"))
e.close()
