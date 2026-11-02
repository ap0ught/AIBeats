"""Room-19 entry -> pillar top, macro enumeration on a Mesen state (TAS research; same macros for real states).
Wall jump off the pillar face (A+L at w), Left, floor jump at j (A+L 2f), air Left from l, land on the box, turn Right
t frames, A+Right 2f, Right. Score: first frame grounded on y 128 with X >= 170 -> eff = f - X/1.5.
python work/r1920/e19.py <mst> <f0> [--hist rows] [--w0 a:b] [--j0 a:b]"""
import sys, itertools
sys.path.insert(0, '.'); sys.path.insert(0, 'work/l31t'); sys.path.insert(0, 'work/r1920')
import fcka
from ng import fastcore as F
from ng.solve import common as C
from gbeam import FL, X, Leg
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i + 1]; del a[i:i + 2]; return type(d)(v)
    return d
HIST = opt('--hist', ''); W0 = opt('--w0', '0:20'); J0 = opt('--j0', '5:40'); N = opt('--n', 110); OUT = opt('--out', '')
mst, f0 = a[0], int(a[1])
hist = [tuple(r) for r in C.rows_of(HIST)][-60:] if HIST else [()] * 30
fc = F.FastCore(boot_rows=None, ticks=True, fields=FL)
fc.put('s', open(mst, 'rb').read()); fc._ka_slot = 's'
w0, w1 = map(int, W0.split(':')); j0, j1 = map(int, J0.split(':'))
cands = []; desc = []
UMAX = opt('--umax', 4)
for w in range(w0, w1):
  for u in range(0, UMAX + 1):
    if u and w - u < 0: continue
    for j in range(w + 6, w + j1):
        for l in range(j + 2, j + 12):
            rows = [()] * (w - u) + [('Up',)] * u + [('A', 'Left')] * 2 + [('Left',)] * (j - w - 2) + [('A', 'Left')] * 2
            rows += [()] * (l - j - 2) + [('Left',)] * 30
            if u == 1: continue
            cands.append((w, j, l, u, 0, rows))
# the box landing frame is found by simulation: rows up to landing, then turn/jump
print(len(cands), 'base candidates', flush=True)
best = []
CH = 60
base_rows = {}
for i in range(0, len(cands), CH):
    chunk = cands[i:i + CH]
    res = fc.run_batch('s', [c[5] for c in chunk], record='all')
    for c, r in zip(chunk, res):
        w, j, l, u, k, rows = c
        # first frame after the floor jump where Ryu is grounded on y 160 (box)
        land = next((q for q in range(j + 3, len(r.states)) if r.states[q]['coll'] & 16 and r.states[q]['y'] == 160), None)
        if land is None: continue
        base_rows[(w, u, j, l, land)] = rows[:land + 1]
print(len(base_rows), 'box landings', flush=True)
full = []; fdesc = []
for (w, u, j, l, land), pre in base_rows.items():
    for t in (1, 2):
        for k in (0, 1):
            rows = pre + [('Left',)] * k + [('Right',)] * t + [('A', 'Right')] * 2 + [('Right',)] * 60
            L = Leg(hist); ok = True
            for q, rr in enumerate(rows):
                e = tuple(sorted(L.emit(rr)))
                if e != tuple(sorted(rr)): ok = False; break
            if not ok: continue
            full.append(rows[:N]); fdesc.append((w, u, j, l, land, k, t))
print(len(full), 'legal full candidates', flush=True)
out = []
for i in range(0, len(full), CH):
    res = fc.run_batch('s', full[i:i + CH], record='all')
    print(i, flush=True) if i % 600 == 0 else None
    for d, rows, r in zip(fdesc[i:i + CH], full[i:i + CH], res):
        g = next((q for q, s in enumerate(r.states) if s['coll'] & 16 and s['y'] == 128 and X(s) >= 165), None)
        if g is None: continue
        s = r.states[-1]
        out.append((len(r.states) - X(s) / 1.5 if False else f0 + len(r.states) - X(s) / 1.5, f0 + g + 1, X(s), s['hp'], d, rows))
out.sort(key=lambda z: z[0])
for z in out[:10]: print('eff', round(z[0], 1), 'pillar', z[1], 'endX', z[2], 'hp', z[3], 'w u j l land k t', z[4])
if OUT and out:
    C.write_inputs(OUT, out[0][5], f'e19 {mst} {f0} eff {out[0][0]:.1f}'); print('wrote', OUT)
fc.close()
