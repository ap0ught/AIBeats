"""L12h stage 5, two launches (when the spring is too far from the poles for a direct grab): pump at once and launch straight up so that
face 3 spawns as early as the camera allows, come back down on the lower spring (it moves Left 2 px/frame), ride, pump again and launch
to a pole (x 96 / 32, H 4888) - the wind of face 3 blows Left, toward the poles.
    python l12h_s5b.py <piece> <out>  -> piece <out> / bookmark L12h_<out> (hanging on the pole) with face3 = spawn frame"""
import sys, json
from l12h_lib import *
pn, out = sys.argv[1], sys.argv[2]
p = load_piece(pn); k0 = p["base_k"] + len(p["inputs"])
e = BizHawk(log_name=f"fix_l12h_{out}.log"); e.load(p["base"]); run(e, p["inputs"]); root = e.msave()
def lsp(s): return (ob(s, 0x36, 4800, 40) or [None])[0]
def onspring(s):
    sp = lsp(s)
    return sp is not None and s["z"] == 0 and 4798 <= s["H"] <= 4812 and abs(dx(s["x"], sp)) <= 15
class Run:
    def __init__(self, sid, k, seq): e.mload(sid); self.k = k; self.seq = list(seq); self.s = rd(e)
    def st(self, b):
        e.step(bt(b), 1); self.k += 1; self.seq.append(b); self.s = rd(e); return self.s
    def ok(self): return alive(self.s)
s = rd(e); print("start", k0, s["x"], s["H"], s["z"], s["an"], "spring", lsp(s), "cam", s["cam"], flush=True)
def pump(r):
    """A held from now: returns the launch frame (first z=8) without changing r"""
    e2 = e.msave(); L = None
    for i in range(45):
        e.step(("A",), 1)
        if rd(e)["z"] == 8: L = r.k + i + 1; break
    e.mload(e2); e.mfree(e2); return L
# ---- phase 1: first launch, face 3, back onto the spring
ph1 = []
for w0 in range(0, 6):
    r = Run(root, k0, [])
    for i in range(w0): r.st("")
    if r.s["z"] != 0: continue
    L = pump(r)
    if L is None: continue
    ws = e.msave(); kw = r.k; sw = list(r.seq)
    for dash in (False, True):
        for a in (0, 6, 12, 18, 24, 30):                  # frames of plain A after the launch before steering Left
            for b in (70, 40, 30, 20):                    # then Left+A for b frames, then A
                r = Run(ws, kw, sw)
                while r.k < L - 3: r.st("A")
                for x in (["Left+A", "A", "Left+A"] if dash else ["A", "A", "A"]): r.st(x)
                if r.s["z"] != 8: continue
                face = None; land = None
                for i in range(120):
                    s = r.st("A" if i < a else ("Left+A" if i < a + b else "A"))
                    if not r.ok(): break
                    if s["faces"] and face is None: face = r.k
                    if s["z"] == 0:
                        if onspring(s): land = (r.k, s["x"], lsp(s))
                        break
                if face and land: ph1.append((face, land[0], e.msave(), r.k, list(r.seq), dict(w0=w0, L=L, dash=dash, a=a, b=b), land))
    e.mfree(ws)
ph1.sort(key=lambda t: (t[0], t[1]))
print("phase 1:", [(t[0], t[1], t[6], t[5]) for t in ph1[:6]], flush=True)
if not ph1: raise SystemExit("phase 1 failed")
# ---- phase 2: second launch to a pole
fin = []
for face, lk, sid, k, seq, par, land in ph1[:3]:
    for w in range(0, 90):
        r = Run(sid, k, seq)
        for i in range(w): r.st("")
        if not r.ok() or r.s["z"] != 0 or not onspring(r.s): break
        L = pump(r)
        if L is None: continue
        ws = e.msave(); kw = r.k; sw = list(r.seq)
        for d in ("Left", "", "Right"):
            for dash in ((True, False) if d else (False,)):
                r = Run(ws, kw, sw)
                while r.k < L - 3: r.st("A")
                for x in ([d + "+A", "A", d + "+A"] if dash else ["A", "A", (d + "+A").strip("+")]): r.st(x)
                if r.s["z"] != 8 or not r.ok(): continue
                la = e.msave(); kl = r.k; sl = list(r.seq)
                for hd in ((0,) if not d else (6, 12, 18, 24, 32, 40, 50, 70)):
                    r = Run(la, kl, sl)
                    for i in range(110):
                        s = r.st((d + "+A").strip("+") if i < hd else "A")
                        if not r.ok(): break
                        if s["an"] in (94, 95, 96): fin.append((face, r.k, s["x"], list(r.seq), dict(par, w=w, L2=L, d=d, dash2=dash, hd=hd))); break
                        if s["z"] == 0: break
                e.mfree(la)
        e.mfree(ws)
        if fin and w > min(f[4]["w"] for f in fin) + 12: break
    print("phase 2 from face", face, "landing", lk, ": pole grabs so far", len(fin), flush=True)
    if fin: break
fin.sort(key=lambda t: (t[0], t[1]))
for t in fin[:8]: print("face3", t[0], "pole", t[1], "x", t[2], t[4])
if not fin: raise SystemExit("no pole")
for i, t in enumerate([fin[0]] + [x for x in fin if x[2] != fin[0][2]][:1]):
    name = out if i == 0 else out + "b"
    save_piece(name, p["base"], p["base_k"], p["inputs"] + t[3], face3=t[0], pole=t[1], polex=t[2])
    e.load(p["base"]); run(e, p["inputs"] + t[3]); e.save("L12h_" + name); print("saved", name, "face3", t[0], "pole", t[1], "x", t[2], flush=True)
e.close()
