"""end brute force on the g3 line from 13540: jump (frame j, hold h), slash B at a (and b), Right otherwise.
python work/l32b/scan3.py <mst> <hist> <goalX>"""
import sys
sys.path.insert(0, 'work/l32b'); sys.path.insert(0, '.')
import xp
from ng.solve import common as C, legality as L
from ng import fastcore as F
mst, hf = sys.argv[1], sys.argv[2]; GX = int(sys.argv[3]) if len(sys.argv) > 3 else 3035
H = C.rows_of(hf); f0 = len(H); n = 125
specs = []
for j in range(int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6])):
    for h in (2, 3, 5):
        for a in [None] + list(range(j + 4, j + 46, 3)):
            for b in [None] + (list(range(a + 6, a + 30, 3)) if a else []):
                w = [('Right',)] * n
                for f in range(j, j + h): w[f - f0 - 1] = ('A', 'Right')
                for q in (a, b):
                    if q:
                        for f in (q, q + 1):
                            k = f - f0 - 1
                            w[k] = tuple(sorted(set(w[k]) | {'B'}))
                specs.append(((j, h, a, b), w))
print(len(specs), flush=True)
EN0 = L.Enforcer(H[-1900:])
fc = F.FastCore(boot_rows=None, ticks=True); fc.put('s', open(mst, 'rb').read()); fc.load('s')
res = []
for i in range(0, len(specs), 48):
    cs = []
    for k, w in specs[i:i+48]:
        en = EN0.copy(); cs.append([tuple(sorted(en.emit(x))) for x in w])
    rr = fc.run_batch('s', cs, record='all', stops=[(0x65, 'changed', 0)])
    for (k, w), r in zip(specs[i:i+48], rr):
        st = r.states
        reach = next((f0 + 1 + q for q, s in enumerate(st) if C.abs_x(s) >= GX), None)
        s = st[-1]
        res.append((reach or 99999, -C.abs_x(s), k, s['hp'], len(st)))
fc.close()
import json; json.dump([list(map(str,q)) for q in res], open('work/l32b/scan3_last.json','w'))
res.sort(key=lambda q: (q[0], q[1]))
for q in res[:12]: print(q)
