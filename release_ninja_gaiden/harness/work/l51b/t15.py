"""Tosser-3 area repair: from a state at our F0 (lag L), legal TAS rows with the 23,544 jump moved / a pause / a 2nd jump.
python work/l51b/t15.py <mst> F0 <hist> L [--end 23670]"""
import sys
sys.path.insert(0, 'work/l51b')
from lb import *
a = sys.argv[1:]
END = 23670
if '--end' in a: i = a.index('--end'); END = int(a[i+1]); del a[i:i+2]
mst, F0, H, L = a[0], int(a[1]), a[2], int(a[3])
hist = [tuple(sorted(r)) for r in C.rows_of(H)]
T1 = F0 + 1 - L
cands = []
for p in (0, 2, 4, 8):
    for pt in range(23520, 23545, 8) if p else [0]:
        for j in range(23536, 23560):
            for j2 in (0, 23572, 23578, 23584, 23590):
                m = {23544: {'Right'}, 23545: {'Right'}, j: {'A', 'Right'}, j + 1: {'A', 'Right'}}
                if j2: m[j2] = m[j2 + 1] = {'A', 'Right'}
                w = tasleg(T1, END, m)
                if p:
                    k = pt - T1; w = w[:k] + [set()] * p + w[k:]
                rows = enforce(w, hist)
                if legal_ok(rows, hist): continue
                cands.append(((p, pt, j, j2), rows))
print('cands', len(cands), flush=True)
fc = core(mst); fc.save('b'); fc._ka_slot = 'b'
TX, TY = tas_xy(END)
res = []
for i in range(0, len(cands), 100):
    ch = cands[i:i+100]
    rr = fc.run_batch('b', [r for _, r in ch], record='all')
    for (k, rows), r in zip(ch, rr):
        st = r.states; hp = min(s['hp65'] for s in st)
        # frame at which X >= 2336 and y <= 160 (on the y-160 step or above)
        g = next((t for t, s in enumerate(st) if RXY(s)[0] >= 2336 and s['y8a'] <= 160), None)
        res.append((-hp, F0 + 1 + g if g is not None else 99999, k))
res.sort()
for x in res[:25]: print(x, flush=True)
print('TAS-eq goal', 23670 + L, 'TAS X,y', (TX, TY))
fc.close()
