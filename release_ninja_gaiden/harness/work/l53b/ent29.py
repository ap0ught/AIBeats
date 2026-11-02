"""l53b: room-29 (and 31) entry: climb the '9' face on Ryu's right then jump off left and run left onto the floor.
python work/l53b/ent29.py <mst|tasF> F0 XT YT [N] ; metric = first frame with X <= XT and y <= YT on the floor (coll & 0x10)."""
import sys
sys.path.insert(0, 'work/l53p'); sys.path.insert(0, 'work/l53b')
from lb import *
src, F0, XT, YT = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
N = int(sys.argv[5]) if len(sys.argv) > 5 else 110
hist = []
for f in range(F0 - 150, F0 + 1):
    w = set(T(f))
    if 'Up' in w and 'Down' in w: w -= {'Up', 'Down'}
    if 'Left' in w and 'Right' in w: w -= {'Left'}
    hist.append(tuple(sorted(w)))
hist = [()] * 150   # transition rows are blank anyway
CYC = {'U': [('Up',)],
       'c1': [('Right',), ('Right',), ('Left',), ('A', 'Left'), ('A', 'Right')],
       'c1b': [('A', 'Left'), ('A', 'Right'), ('Right',), ('Right',), ('Left',)],
       'c1c': [('Left',), ('A', 'Left'), ('A', 'Right'), ('Right',), ('Right',)],
       'c2': [('A', 'Left'), ('A', 'Left'), ('Right',), ('Right',), ('Right',), ('Right',), ('Right',), ('Right',)],
       'c3': [('A', 'Left'), ('A', 'Left'), ('Right',), ('Right',), ('Right',)]}
cands = []
for cname, cyc in CYC.items():
    for nclimb in range(0, 61):
        climb = (cyc * 60)[:nclimb]
        for tail in ([('A', 'Left')] * 2, [('Left',)], [('A', 'Left')] * 3, [('Up', 'Left')]):
            rows = climb + tail
            rows = (rows + [('Left',)] * N)[:N]
            if legal_ok(rows, hist): continue
            cands.append(((cname, nclimb, P(tail[0]), len(tail)), rows))
print('cands', len(cands), flush=True)
fc = core(src) if src.endswith('.mst') else core_at(F0)
fc.poke(0x65, 3); fc.save('b'); fc._ka_slot = 'b'
res = []
for i in range(0, len(cands), 64):
    ch = cands[i:i+64]
    rr = fc.run_batch('b', [c[1] for c in ch], record='all')
    for (k, rows), r in zip(ch, rr):
        for t, s in enumerate(r.states):
            if s['hp65'] < 3: break
            X, y = RXY(s)
            if X <= XT and y <= YT and s['coll'] & 0x10:
                res.append((F0 + 1 + t, k, (X, y), s['xsub'])); break
fc.close()
res.sort(key=lambda q: q[0])
for q in res[:25]: print(q)
