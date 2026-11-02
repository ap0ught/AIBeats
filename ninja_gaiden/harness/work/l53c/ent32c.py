"""l53c room-32 entry grid, stage 1 (from TAS state 28652 = room-32 control - 1):
climb (cycle x n rows) -> A+Left x2 -> Left*m -> Right*r -> A+Right x2 -> Right*.
metric: first frame standing on the right column top (y 160, X >= 112); prints the best (frame, X, xsub).
python work/l53c/ent32.py [N 80]"""
import sys
sys.path.insert(0, 'work/l53p')
from lib import *
N = int(sys.argv[1]) if len(sys.argv) > 1 else 80
F0 = 28652
hist = [row(l.strip()) for l in open('work/l53c/hist_tas28652.txt') if l.strip()]
U, L, R, AL, AR = ('Up',), ('Left',), ('Right',), ('A', 'Left'), ('A', 'Right')
CYC = {'c2': [AL, AL, R, R, R, R, R, R], 'c2u': [AL, AL, R, R, R, R, R, R, U, U], 'c7': [AL, AL, R, R, R, R, R]}
cands = []
for cname, cyc in CYC.items():
    for n in range(6, 28):
        climb = (cyc * 60)[:n]
        for m in range(9, 25):
            for r in (2, 3):
                rows = climb + [AL, AL] + [L] * m + [R] * r + [AR, AR]
                rows = (rows + [R] * N)[:N]
                if legal_ok(rows, hist): continue
                cands.append(((cname, n, m, r), rows))
print('cands', len(cands), flush=True)
fc = core('states/mesen/l53c_tas28652.mst'); fc.save('b'); fc._ka_slot = 'b'
res = []
for i in range(0, len(cands), 64):
    ch = cands[i:i+64]
    rr = fc.run_batch('b', [c[1] for c in ch], record='all')
    for (k, rows), r in zip(ch, rr):
        for t, s in enumerate(r.states):
            if s['hp65'] < 2 or s['hp65'] > 100: break
            X, y = RXY(s)
            if y == 160 and X >= 112 and s['coll'] & 0x10:
                res.append((F0 + 1 + t, -X, -s['xsub'], k)); break
fc.close()
res.sort()
for q in res[:30]: print(q)
print('TAS: 28714 X 122 (lands), TAS tail from 28714 is legal')
