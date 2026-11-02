"""room 15 r2c-like branch route scan: cycle to c, A+Left x2, Right x k1, '-' x k0, A+d2 x2 at t2, Right after.
metric: first frame on top (y==96, X>=140). python work/l41/r15q.py <rows> <S> <out json>"""
import sys, json
sys.path.insert(0, 'work/l41')
from psearch import *
rf, S, outj = sys.argv[1], int(sys.argv[2]), sys.argv[3]
base = list(C.rows_of(rf)); pre = base[:S - F0]; E = S + 160
cands = []; desc = []
for c in range(S + 30, S + 90):
    for k1 in (1, 2, 3, 4):
        for k0 in (0, 1, 2):
            for d2 in ('Left', 'Right', ''):
                for gap in (0, 1, 2, 3, 4):
                    r = list(base[S - F0:c - F0])
                    r += [('A', 'Left')] * 2 + [('Right',)] * k1 + [()] * k0 + [()] * gap
                    r += [tuple(sorted(('A',) + ((d2,) if d2 else ())))] * 2
                    while len(r) < E - S: r.append(('Right',))
                    if legal(pre, r): cands.append(r); desc.append((c, k1, k0, d2, gap))
print('cands', len(cands), flush=True)
def metric(st, i):
    for s in st:
        if s['hp'] == 0 or s['item'] != 133: return None
        if s['room'] == 15 and C.abs_x(s) >= 140 and s['y'] == 96: return s['frame']
    return None
t = time.time(); res = run(cands, pre, metric)
print('time', round(time.time() - t), flush=True)
for v, i in res[:20]: print(v, desc[i], flush=True)
json.dump([(v, desc[i]) for v, i in res if v], open(outj, 'w'))
if res and res[0][0]:
    C.write_inputs(outj.replace('.json', '_best.txt'), pre + cands[res[0][1]], f'r15q best {desc[res[0][1]]}')
close()
