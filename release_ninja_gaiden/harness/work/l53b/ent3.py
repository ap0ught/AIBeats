"""l53b: rightward entry (rooms 28/30/32), conditional phases. From mst/TAS F0 (control row - 1):
 climb c2 x n -> A+Left x2 -> Left until landed on the ledge (+m extra Left) -> Right x r -> A+Right x2 -> Right until on the
 column top (+w) -> A+Right x2 -> Right... ; metric = first frame X >= XT, y <= YT (no hp loss).
python work/l53b/ent2.py <mst|tasF> F0 <hist|-> [XT 200] [YT 144] [--poke 65=3]"""
import sys, os
sys.path.insert(0, 'work/l53p'); sys.path.insert(0, 'work/l53b')
from lb import *
a = sys.argv[1:]
POKE = ''
if '--poke' in a: i = a.index('--poke'); POKE = a[i+1]; del a[i:i+2]
src, F0, HF = a[0], int(a[1]), a[2]
XT = int(a[3]) if len(a) > 3 else 200
YT = int(a[4]) if len(a) > 4 else 144
hist = [row(l.strip()) for l in open(HF) if l.strip() and not l.startswith('#')] if HF != '-' else [()] * 150
fc = core(src) if src.endswith('.mst') else core_at(F0)
for p in [q for q in POKE.split(',') if q]:
    k, v = p.split('='); fc.poke(int(k, 16), int(v))
fc.save('b'); fc._ka_slot = 'b'
C2 = [('A', 'Left'), ('A', 'Left')] + [('Right',)] * 6
C1 = [('Right',), ('Right',), ('Left',), ('A', 'Left'), ('A', 'Right')]
CYCS = {'c1r2': C1[2:] + C1[:2]} if os.environ.get('C1ONLY') else {'c2': C2, 'U': [('Up',)], 'c1r2': C1[2:] + C1[:2]}
if os.environ.get('C2ONLY'): CYCS = {'c2': C2}
FIXF = [int(x) for x in os.environ.get('FIXF', '').split(',') if x]
def fixok(rows): return all(rows[f - F0 - 1] == rows[f - F0 - 2] for f in FIXF if 0 <= f - F0 - 2 < len(rows))
DB = int(os.environ.get('DB', '0'))
TJ0, TJ1 = int(os.environ.get('TJ0', '0')), int(os.environ.get('TJ1', '0'))
KEYS = (0x86, 0x85, 0x8A, 0x89, 0x87, 0x84, 0x8C, 0x51, 0x52)
FN = {0x86: 'x86', 0x85: 'xsub', 0x8A: 'y8a', 0x89: 'vy', 0x87: 'vy_sub', 0x84: 'rf84', 0x8C: 'coll', 0x51: 'scr_lo', 0x52: 'scr_hi'}
TK = {}
for g in range(TJ0, TJ1 + 1): TK.setdefault(tuple(TM(g)[k] for k in KEYS), g)
def run(cands):
    out = []
    for i in range(0, len(cands), 48):
        out += fc.run_batch('b', cands[i:i+48], record='all')
    return [r.states for r in out]
# pass 1: climb + jump-off + Left*40 -> landing frame
p1 = []
for cn, cy in CYCS.items():
    for n in range(int(os.environ.get('N0', '8')), int(os.environ.get('N1', '40'))):
        for tl in (2, 1, 0):
          for d in range(DB + 1):
            rows = [()] * d + (cy * 20)[:n] + [('A', 'Left')] * tl + [('Left',)] * 40
            if legal_ok(rows, hist): continue
            p1.append(((cn, n + d, tl, d), rows))
S1 = run([r for _, r in p1])
p2 = []
for (k, rows), st in zip(p1, S1):
    n = k[1] + k[2]; land = None
    for t in range(n + 2, len(st)):
        if st[t]['coll'] & 0x10 and RXY(st[t])[1] == 192: land = t; break
    if land is None: continue
    for m in range(0, 7):
        for r in (1, 2):
            pre = rows[:land + 1] + [('Left',)] * m + [('Right',)] * r + [('A', 'Right')] * 2 + [('Right',)] * 50
            if legal_ok(pre, hist): continue
            p2.append((k + (m, r), pre, land + 1 + m + r + 2))
S2 = run([r for _, r, _ in p2])
p3 = []
for (k, rows, j0), st in zip(p2, S2):
    top = None
    for t in range(j0, len(st)):
        if st[t]['hp65'] < 3: break
        if st[t]['coll'] & 0x10 and RXY(st[t])[1] == 160: top = t; break
    if top is None: continue
    for w in range(0, 3):
        pre = rows[:top + 1] + [('Right',)] * w + [('A', 'Right')] * 2 + [('Right',)] * 90
        if legal_ok(pre, hist) or not fixok(pre): continue
        p3.append((k + (w,), pre))
print('pass sizes', len(p1), len(p2), len(p3), flush=True)
S3 = run([r for _, r in p3])
res = []
for (k, rows), st in zip(p3, S3):
    for t, s in enumerate(st):
        if s['hp65'] < 3: break
        X, y = RXY(s)
        if TK:
            key = tuple(s[FN[q]] for q in KEYS)
            if key in TK and t > 20:
                res.append((F0 + 1 + t - TK[key], k, (X, y), F0 + 1 + t, TK[key], rows[:t + 1])); break
        elif X >= XT and y <= YT:
            res.append((F0 + 1 + t, k, (X, y), s['xsub'], s['vy'], rows[:t + 1])); break
res.sort(key=lambda q: q[0])
for q in res[:15]: print(q[:5], flush=True)
if res:
    with open('work/l53b/ent3_best_%d.txt' % F0, 'w') as fo:
        fo.write(f'# ent2 best from {src} F0 {F0}: {res[0][:5]}\n')
        for r_ in res[0][5]: fo.write(P(r_) + '\n')
fc.close()
