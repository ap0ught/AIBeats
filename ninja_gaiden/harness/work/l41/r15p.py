"""room 15 parametric: ladder cycle until c, then A + dir1 for n1 frames, Right after; optional 2nd A at t2.
python work/l41/r15p.py <rows with cycle> <start frame S> <out json>   metric: first frame X>=250, y==96 (on top)"""
import sys, json
sys.path.insert(0, 'work/l41')
from psearch import *
rf, S, outj = sys.argv[1], int(sys.argv[2]), sys.argv[3]
base = list(C.rows_of(rf)); pre = base[:S - F0]; E = S + 190
cands = []; desc = []
for c in range(S + 8, S + 95):
    for d1 in ('Left', 'Right'):
        for n1 in (2, 6, 12, 20):
            for t2 in [0] + list(range(c + 8, c + 44, 4)):
                r = list(base[S - F0:c - F0])
                rest = [(d1,)] * n1
                rest[0] = rest[1] = ('A', d1)
                r += rest
                while len(r) < E - S: r.append(('Right',))
                if t2:
                    for f in (t2, t2 + 1): r[f - S - 1] = tuple(sorted(set(r[f - S - 1]) | {'A'}))
                if legal(pre, r): cands.append(r); desc.append((c, d1, n1, t2))
print('cands', len(cands), flush=True)
def metric(st, i):
    for s in st:
        if s['hp'] == 0 or s['item'] != 133: return None
        if s['room'] == 15 and C.abs_x(s) >= 250 and s['y'] == 96: return s['frame']
    return None
t = time.time(); res = run(cands, pre, metric)
print('time', round(time.time() - t), flush=True)
for v, i in res[:20]: print(v, desc[i], flush=True)
json.dump([(v, desc[i]) for v, i in res if v], open(outj, 'w'))
if res and res[0][0]:
    C.write_inputs(outj.replace('.json', '_best.txt'), pre + cands[res[0][1]], f'r15p best {desc[res[0][1]]}')
close()
