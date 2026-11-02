"""l53b: rightward-room entry grid (rooms 28/30/32 share the entry). From an .mst at the room control - 1 (F0):
climb (Up*u | cycle c x n) -> A+Left x2 -> Left*m -> [blank*b] -> Right*r -> A+Right*j -> Right ... ; metric = first frame
with X >= XT and y <= YT. python work/l53b/ent.py <mst> F0 <hist file> [XT 200] [YT 144] [N 130]"""
import sys, itertools
sys.path.insert(0, 'work/l53p'); sys.path.insert(0, 'work/l53b')
from lb import *
mst, F0, HF = sys.argv[1], int(sys.argv[2]), sys.argv[3]
XT = int(sys.argv[4]) if len(sys.argv) > 4 else 200
YT = int(sys.argv[5]) if len(sys.argv) > 5 else 144
N = int(sys.argv[6]) if len(sys.argv) > 6 else 130
hist = [row(l.strip()) for l in open(HF) if l.strip() and not l.startswith('#')]
CYC = {

       'c2': [('A', 'Left'), ('A', 'Left'), ('Right',), ('Right',), ('Right',), ('Right',), ('Right',), ('Right',)],
}
cands = []
for cname, cyc in CYC.items():
    for nclimb in range(10, 31, 1):
        climb = (cyc * 60)[:nclimb]
        for m in range(4, 19, 1):
            for b in (0,):
                for r in (1, 2):
                    for j in (2,):
                        rows = climb + [('A', 'Left')] * 2 + [('Left',)] * m + [()] * b + [('Right',)] * r + [('A', 'Right')] * j
                        rows = (rows + [('Right',)] * N)[:N]
                        if legal_ok(rows, hist): continue
                        cands.append(((cname, nclimb, m, b, r, j), rows))
print('cands', len(cands), flush=True)
fc = core(mst); fc.save('b'); fc._ka_slot = 'b'
res = []
for i in range(0, len(cands), 64):
    ch = cands[i:i+64]
    rr = fc.run_batch('b', [c[1] for c in ch], record='all')
    for (k, rows), r in zip(ch, rr):
        hit = None
        for t, s in enumerate(r.states):
            if s['hp65'] < 3: break
            X, y = RXY(s)
            if X >= XT and y <= YT: hit = t; break
        if hit is not None:
            s = r.states[hit]
            res.append((F0 + 1 + hit, k, RXY(s), s['xsub'], s['vy']))
fc.close()
res.sort(key=lambda q: q[0])
for q in res[:25]: print(q)
