"""Wall/pillar climb enumeration (Mesen) from a state: python work/l51b/climb.py <mst> F0 <hist> [--goal 'X>=1530 and y<=100']
 [--n 120] [--pre rowsfile]. Families: lead (w rows of R/-/L) + cycles [A+R x2, L x n] or [A+L x2, R x n] or chimney
 [A+R x2, R x a, A+L x2, L x b], cut at ph rows, + RW Right + A+Right x2 + Right. Prints the best by goal frame."""
import sys
sys.path.insert(0, 'work/l51b')
from lb import *
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return type(d)(v)
    return d
GOAL = opt('--goal', 'X>=1530 and y<=100'); N = opt('--n', 120); PRE = opt('--pre', ''); TOP = opt('--top', 15)
LEADS = opt('--leads', '0,4,8'); OUT = opt('--out', ''); PHM = opt('--phm', 36)
mst, F0, H = a[0], int(a[1]), a[2]
hist = [tuple(sorted(r)) for r in C.rows_of(H)]
pre = [tuple(sorted(r)) for r in C.rows_of(PRE)] if PRE else []
GC = compile(GOAL, 'g', 'eval')
fc = core(mst)
if pre: fc.step(pre, record='last')
fc.save('b'); fc._ka_slot = 'b'
AR, AL_, R_, L_, N_ = ('A', 'Right'), ('A', 'Left'), ('Right',), ('Left',), ()
cyc = {}
for n in range(3, 10):
    cyc[f'pil{n}'] = [AR] * 2 + [L_] * n
    cyc[f'wal{n}'] = [AL_] * 2 + [R_] * n
CHS = [int(x) for x in opt('--ch', '2,3,4,6').split(',')]
for a_ in CHS:
    for b_ in CHS:
        cyc[f'ch{a_}{b_}'] = [AR] * 2 + [R_] * a_ + [AL_] * 2 + [L_] * b_
        cyc[f'hc{a_}{b_}'] = [AL_] * 2 + [L_] * a_ + [AR] * 2 + [R_] * b_
res = []
H0 = list(hist) + list(pre)
cands = []; SEEN = set()
for lead in [int(x) for x in LEADS.split(',')]:
    for lr in (R_, N_, L_):
        if lead == 0 and lr != R_: continue
        for name, cy in cyc.items():
            for ph in range(0, PHM, 1):
                for RW in (0, 2):
                    rows = [lr] * lead + (cy * 12)[:ph] + [R_] * RW + [AR] * 2 + [R_] * (N - lead - ph - RW - 2)
                    k_ = tuple(rows)
                    if k_ in SEEN: continue
                    SEEN.add(k_); cands.append((name, lead, P(lr), ph, RW, rows))
print('cands', len(cands), flush=True)
ok = []
for cd in cands:
    L = K.Legal(H0[-1900:]); good = True
    for r in cd[5]:
        if L.why(tuple(sorted(r))): good = False; break
        L.push(tuple(sorted(r)))
    if good: ok.append(cd)
print('legal', len(ok), flush=True)
B = 200
for i in range(0, len(ok), B):
    ch = ok[i:i+B]
    rr = fc.run_batch('b', [c_[5] for c_ in ch], record='all')
    for c_, r in zip(ch, rr):
        g = None; by = 999
        for j, s in enumerate(r.states):
            X, y = RXY(s)
            if s['hp65'] == 0 or y >= 232: break
            by = min(by, y)
            if eval(GC, dict(X=X, y=y, s=s)): g = F0 + len(pre) + 1 + j; break
        res.append((g or 99999, by, c_[0], c_[1], c_[2], c_[3], c_[4], c_[5] if g else None))
res.sort(key=lambda q: q[:2])
for r in res[:TOP]: print(r[:7], flush=True)
if OUT and res and res[0][7]:
    g = res[0][0]; rows = pre + list(res[0][7])[:g - F0 - len(pre)]
    C.write_inputs(OUT, rows, f'climb best {res[0][:7]}')
    print('wrote', OUT)
fc.close()
