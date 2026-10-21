"""L12h stage 4 v2 (walker, the TAS's juggle with air KICKS, not rams): hits 1-2 as l12h_w.py (running kick, B held); hits 3-4 = dash
jump with a one-frame direction gap, then Left+B (anim 38 kick: normal jump physics, short recovery); hit 5 = sprint ram (dash + Left+B):
when it kills, the toad flies on Left (anim 49) and should land on the lower spring. Ranks the final lines by the frame the toad stands
on the spring (chasing it along the ring floor if it has to).
    python l12h_w2.py [KEEP=4]   -> piece w2 / bookmark L12h_w2 (standing on the lower spring, walker dead), logs/fix/L12h_w2_results.json"""
import json, sys
from l12h_lib import *
KEEP = int(sys.argv[1]) if len(sys.argv) > 1 else 4
p = load_piece("s3c"); k0 = p["base_k"] + len(p["inputs"])
e = BizHawk(log_name="fix_l12h_w2.log"); e.load(p["base"]); run(e, p["inputs"]); root = e.msave()
def foe(s): return [(d[1], d[2], d[3]) for d in s["objs"] if d[0] == 0x62]
def hpw(s):
    f = foe(s); return f[0][2] if f else None
def spring(s): return (ob(s, 0x36, 4800, 40) or [None])[0]
def onspring(s):
    sp = spring(s)
    return sp is not None and s["z"] == 0 and 4798 <= s["H"] <= 4812 and abs(dx(s["x"], sp)) <= 15
class Run:
    def __init__(self, sid, k, seq): e.mload(sid); self.k = k; self.seq = list(seq); self.s = rd(e)
    def st(self, b):
        e.step(bt(b), 1); self.k += 1; self.seq.append(b); self.s = rd(e); return self.s
    def ok(self): return alive(self.s) and self.s["H"] >= 4700
IDLE = (1, 2, 3, 4, 5, 6, 7, 8)
def to_ground(r, hold="", maxf=70):
    for i in range(maxf):
        if r.s["z"] == 0 and r.s["an"] in IDLE: return True
        r.st(hold)
        if not r.ok(): return False
    return False
st12 = []
for n in range(36, 50):
    for gap in (0, 1):
        r = Run(root, k0, []); r.st("Left+A")
        for i in range(n): r.st("Left")
        if not foe(r.s): continue
        for i in range(gap): r.st("")
        h1 = h2 = None
        for i in range(70):
            s = r.st("Left+B")
            if not r.ok(): break
            h = hpw(s)
            if h1 is None and h is not None and h <= 63: h1 = r.k
            if h is not None and h <= 47: h2 = r.k; break
        if h2 is None: continue
        st12.append((h2, h1, (n, gap), e.msave(), r.k, list(r.seq)))
        print("stage 1-2: n", n, "gap", gap, "hit1", h1, "hit2", h2, "toad", r.s["x"], r.s["H"], "walker", foe(r.s), flush=True)
st12.sort(key=lambda t: t[0]); st12 = st12[:KEEP + 2]
def kick_stage(nodes, target, label):
    out = []
    for item in nodes:
        sid, k, seq, par = item[-4], item[-3], item[-2], item[-1] if isinstance(item[-1], tuple) and not isinstance(item[-1][0], str) else ()
        for gh in ("", "Left"):
            r = Run(sid, k, seq)
            if not to_ground(r, gh): continue
            g = e.msave(); kg = r.k; sg = list(r.seq)
            for pre in (("Left", ""), (), ("",), ("", "Left", "")):
                for ja in (1, 2, 4, 6, 9, 12):                 # total frames of A
                    for bd in (2, 3, 4, 5, 7):                 # the B frame, counted from the jump frame
                        r = Run(g, kg, sg)
                        for b in pre: r.st(b)
                        r.st("Left+A")                         # jump (dash when the tap-gap came before)
                        for i in range(1, bd):
                            r.st("A" if i < ja else "")        # the direction gap: no sprint -> B is a kick, not a ram
                        r.st("Left+B+A" if bd < ja else "Left+B")
                        hit = None; an_b = r.s["an"]
                        for i in range(30):
                            s = r.st("Left+A" if bd + 1 + i < ja else "Left")
                            if not r.ok(): break
                            if hpw(s) is not None and hpw(s) <= target: hit = r.k; break
                        if hit is None: continue
                        if not to_ground(r, "Left") or not r.ok(): continue
                        out.append((r.k, hit, e.msave(), r.k, list(r.seq), par + ((gh, pre, ja, bd, an_b),)))
            e.mfree(g)
    out.sort(key=lambda t: (t[0], t[1]))
    print(label, [(t[0], t[1], t[5][-1]) for t in out[:8]], flush=True)
    return out[:KEEP]
n12 = [(t[0], t[3], t[4], t[5], (t[2],)) for t in st12]
st3 = kick_stage(n12, 31, "stage 3 (ready, hit):")
if not st3: raise SystemExit("no third hit")
st4 = kick_stage(st3, 15, "stage 4 (ready, hit):")
if not st4: raise SystemExit("no fourth hit")
for i, item in enumerate(st4[:2]):
    save_piece(f"w2h4_{i}", p["base"], p["base_k"], p["inputs"] + item[4], ready=item[0], hit4=item[1])
    e.mload(item[2]); e.save(f"L12h_w2h4_{i}"); print("saved w2h4_%d" % i, item[0], item[1], item[5], flush=True)
if len(sys.argv) > 2 and sys.argv[2] == "stop4": e.close(); raise SystemExit(0)
# ---- stage 5: sprint ram, then get on the spring
res = []
for item in st4:
    sid, k, seq, par = item[2], item[3], item[4], item[5]
    for pre in ((), ("Right",), ("Left", ""), ("",), ("Right", ""), ("", ""), ("", "", ""), ("", "", "", "")):
        for jump in (("A", "Left+B"), ("Left+A", "Left+B"), ("Left+B",), ("Left+A+B",), ("Left+A", "Left+A", "Left+B"), ("Left", "Left+B"), ("Left", "Left", "Left+B")):
            for hold in ("Left", ""):
                r = Run(sid, k, seq)
                for b in pre: r.st(b)
                for b in jump: r.st(b)
                kill = None
                for i in range(40):
                    s = r.st(hold)
                    if not r.ok(): break
                    if hpw(s) == 0: kill = r.k; break
                if kill is None: continue
                board = None
                for i in range(60):                                  # the ram's flight: do we come down on the spring?
                    if onspring(r.s) and r.s["an"] not in (35, 38, 39): board = r.k; break
                    if r.s["z"] == 0 and r.s["an"] in IDLE: break
                    r.st(hold)
                    if not r.ok(): break
                if not r.ok(): continue
                if board is None:                                    # chase: sprint Left, dash-jump onto it when close behind it
                    c = e.msave(); kc = r.k; sc = list(r.seq)
                    for wj in range(0, 140, 2):
                        r = Run(c, kc, sc); r.st("Left"); r.st("")
                        for i in range(wj): r.st("Left")
                        if not r.ok() or r.s["z"] != 0: continue
                        r.st(""); r.st("Left"); r.st("")              # (re)tap for the dash jump
                        for i in range(60):
                            s = r.st("Left+A" if i < 6 else "Left")
                            if not r.ok(): break
                            if onspring(s): board = r.k; break
                            if s["z"] == 0 and i > 3: break
                        if board: break
                    e.mfree(c)
                if board is None: continue
                res.append((board, kill, list(r.seq), par + ((pre, jump, hold),), r.s["x"], spring(r.s)))
res.sort(key=lambda t: (t[0], t[1]))
for t in res[:12]: print("on the spring at", t[0], "kill", t[1], "x", t[4], "spring", t[5], t[3][-1], flush=True)
if res:
    b = res[0]
    save_piece("w2", p["base"], p["base_k"], p["inputs"] + b[2], kill=b[1], board=b[0])
    e.load(p["base"]); run(e, p["inputs"] + b[2]); e.save("L12h_w2"); s = rd(e); print("saved L12h_w2", b[0], b[1], s["x"], s["H"], s["z"], s["an"], spring(s))
    json.dump([dict(board=t[0], kill=t[1], seq=t[2]) for t in res[:20]], open(FIX / "L12h_w2_results.json", "w"))
e.close()
