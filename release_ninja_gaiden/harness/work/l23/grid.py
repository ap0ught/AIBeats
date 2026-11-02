"""Mesen grid for the 2-spin Bomberhead kill. python work/l23/grid.py <npre> [jlo-jhi] [blo-bhi] [slo-shi] [land offsets]
Rows from control (1-based): Left; Left+A at j,j+1; Left+B at b,b+1; from s: stop mode (- or Right) ; at j+44+o:
Left+A, then Up+Left+B+A, Up+Left+B, Left... Legalized after the power-on history (2-2 rows with npre Lefts)."""
import sys, itertools
sys.path.insert(0, 'work/l23')
from lib import *
npre = int(sys.argv[1])
def rng(a, d):
    lo, hi = (a.split('-') if a else d)
    return range(int(lo), int(hi) + 1)
J = rng(sys.argv[2] if len(sys.argv) > 2 else None, (24, 40))
B = rng(sys.argv[3] if len(sys.argv) > 3 else None, (58, 67))
S = rng(sys.argv[4] if len(sys.argv) > 4 else None, (64, 74))
O = [int(x) for x in (sys.argv[5] if len(sys.argv) > 5 else '-1,0,1').split(',')]
s22 = [tuple(r) for r in C.rows_of('logs/l22_art_t12.inputs.txt')]
s22 = s22[:-npre] + [('Left',)] * npre
hist = list(HIST[:L22.F0]) + s22
def cand(j, b, s, mode, o):
    n = 100
    r = [('Left',)] * n
    for i in range(1, n + 1):
        if i >= s: r[i - 1] = () if mode == '-' else ('Right',)
    for i in (j, j + 1): r[i - 1] = tuple(sorted(set(r[i - 1]) | {'A'}))
    for i in (b, b + 1): r[i - 1] = tuple(sorted(set(r[i - 1]) | {'B'}))
    L2 = j + 44 + o
    r[L2 - 1] = ('A', 'Left'); r[L2] = ('A', 'B', 'Left', 'Up'); r[L2 + 1] = ('B', 'Left', 'Up')
    for i in range(L2 + 2, n): r[i] = ('Left',)
    return r[:L2 + 8]
cands, meta = [], []
for j, b, s, mode, o in itertools.product(J, B, S, ('-', 'Right'), O):
    if b <= j + 2 or s < b: continue
    w = cand(j, b, s, mode, o)
    lg = legal_after([], w, hist)
    cands.append(lg); meta.append((j, b, s, mode, o, lg != [tuple(sorted(x)) for x in w]))
print('candidates', len(cands), flush=True)
fc = L22.core(); fc.step(s22); fc.save('b'); m = fc.ram(); print('control x', m[0x86], 'BF', m[0xBF]); fc.close()
blob = None
import ng.fastcore as F
fc = F.FastCore(boot_rows=None, ticks=True)
fc2 = L22.core(); fc2.step(s22); blob = fc2.get('b') if False else None
fc2.save('b'); data = fc2.get('b'); fc2.close()
P = F.FastPool(2, boot_rows=None, ticks=True); P.put_all('b', data)
fc.close()
best = []
CH = 40
for k in range(0, len(cands), CH):
    res = P.run_batch('b', cands[k:k + CH], record='last', stops=[(0x66, '==', 0)])
    for i, rr in enumerate(res):
        st = rr.states[-1] if rr.states else None
        if rr.status == 1:
            best.append((rr.rows_played, meta[k + i], st.get('ninpo') if st else None, st.get('hp') if st else None))
best.sort()
for x in best[:15]: print('kill row', x[0], 'j,b,s,mode,o,legalized', x[1], 'np', x[2], 'hp', x[3])
print('n kills', len(best), 'min', best[0][0] if best else None)
P.close()
