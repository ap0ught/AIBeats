"""Room-37 entry test: prefix (b_r37e rows to 32646) + Right*k + Left*m + A+Left*2 + Left*n ... trace X,y to the pillar cling."""
import sys
sys.path.insert(0, 'work/l61p')
from lib import *
pre = [row(l.strip()) for l in open('work/l61p/r37e_pre51.txt') if l.strip() and not l.startswith('#')]
fc = core_at(32595); fc.save('b'); fc._ka_slot = 'b'
best = []
cands = {}
for k in range(0, 30):
    for m in range(0, 30, 2):
        rows = pre + [('Right',)] * k + [('Left',)] * m + [('A', 'Left')] * 2 + [('Left',)] * 60
        cands[(k, m)] = rows
names = list(cands)
for i in range(0, len(names), 64):
    rr = fc.run_batch('b', [cands[n] for n in names[i:i+64]], record='all')
    for n, r in zip(names[i:i+64], rr):
        cam = None; cl = None
        for t, s in enumerate(r.states):
            if cam is None and (s['scr_hi'] * 256 + s['scr_lo']) < 768: cam = 32596 + t
            X, y = RXY(s)
            if cam and X <= 842 and y <= 160 and cl is None: cl = (32596 + t, X, y)
        if cl: best.append((cl, n, cam))
best.sort()
for b in best[:10]: print(b)
fc.close()
