"""Wall climb (no boost) from a state on the approach: rows = R:j A+R:h R:k [A+L:2 R:n]*m R:...
python work/l51b/wclimb.py <mst> F0 <hist> [--j 0:16] [--k 4:22] [--ns 5,6,7] [--hs 2,10] [--goal 'X>=1530 and y<=100']"""
import sys
sys.path.insert(0, 'work/l51b')
from lb import *
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return type(d)(v)
    return d
J = opt('--j', '0:16'); KK = opt('--k', '4:22'); NS = opt('--ns', '5,6,7'); HS = opt('--hs', '2,10'); OUT = opt('--out', '')
GOAL = opt('--goal', 'X>=1530 and y<=100'); NR = opt('--nr', 130); TOP = opt('--top', 15)
mst, F0, H = a[0], int(a[1]), a[2]
hist = [tuple(sorted(r)) for r in C.rows_of(H)]
GC = compile(GOAL, 'g', 'eval')
AR, AL_, R_ = ('A', 'Right'), ('A', 'Left'), ('Right',)
j1, j2 = map(int, J.split(':')); k1, k2 = map(int, KK.split(':'))
cands = []
for j in range(j1, j2):
    for h in [int(x) for x in HS.split(',')]:
        for k in range(k1, k2):
            for n in [int(x) for x in NS.split(',')]:
                rows = [R_] * j + [AR] * h + [R_] * k + ([AL_] * 2 + [R_] * n) * 12
                rows = enforce([set(x) for x in (rows + [R_] * NR)[:NR]], hist)
                if legal_ok(rows, hist): continue
                cands.append(((j, h, k, n), rows))
print('cands', len(cands), flush=True)
fc = core(mst); fc.save('b'); fc._ka_slot = 'b'
res = []
for i in range(0, len(cands), 100):
    ch = cands[i:i+100]
    rr = fc.run_batch('b', [r for _, r in ch], record='all', stops=[(0x8A, '<=', 90)])
    for (key, rows), r in zip(ch, rr):
        g = None
        for t, s in enumerate(r.states):
            X, y = RXY(s)
            if eval(GC, dict(X=X, y=y, s=s)): g = t; break
        top = next((t for t, s in enumerate(r.states) if s['y8a'] <= 100 and RXY(s)[0] >= 1505), None)
        res.append((F0 + 1 + g if g is not None else 99999, F0 + 1 + top if top is not None else 99999, key, r.states[-1]['hp65']))
res.sort()
for x in res[:TOP]: print(x, flush=True)
if OUT and res[0][1] < 99999:
    key = res[0][2]; rows = [rw for kk, rw in cands if kk == key][0]
    n = res[0][1] - F0
    C.write_inputs(OUT, rows[:n], f'wclimb {mst} best {res[0]}')
fc.close()
