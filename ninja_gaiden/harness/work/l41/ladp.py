"""room-14 ladder cycle scan on Mesen: python work/l41/ladp.py <rows> <room14 frame> <out>"""
import sys
sys.path.insert(0, 'work/l41')
from psearch import *
rf, R14, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
base = list(C.rows_of(rf))
S = R14 - 12; E = R14 + 150
pre = base[:S - F0]
cyc = [('Right',), ('Right', 'Up'), ('Right', 'Up'), ('A', 'Left', 'Up'), ('A', 'Left')]
cands = []; desc = []
for s in range(S + 1, R14 + 30):
    for ph in range(5):
        for drop in ('', 'Right', 'Up', 'RU'):
            r = list(base[S - F0:s - 1 - F0]); k = ph; first = True
            while len(r) < E - S:
                c = list(cyc[k % 5])
                if first:
                    for b in (('Right', 'Up') if drop == 'RU' else ((drop,) if drop else ())):
                        if b in c: c.remove(b)
                r.append(tuple(sorted(c))); k += 1
                if k % 5 == 0: first = False
            if legal(pre, r): cands.append(r); desc.append((s, ph, drop))
print('cands', len(cands), flush=True)
def metric(st, i):
    for s in st:
        if s['room'] == 15: return s['frame']
    return None
res = run(cands, pre, metric)
for v, i in res[:8]: print(v, desc[i], flush=True)
v, i = res[0]
C.write_inputs(out, pre + cands[i], f'{rf}[:{S}] + ladder cycle {desc[i]} -> room 15 at {v}')
close()
