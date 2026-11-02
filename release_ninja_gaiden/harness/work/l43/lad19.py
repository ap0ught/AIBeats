"""Room-19 / room-20 entry research: ladder cycle on the entry pillar's left face (X 160 column), then onto the top.
python -u work/l43/lad19.py <mesen state> <state frame> <ladder side R|L> [goalX 212] [ytop 128]
Grid: wait d, cycle rotation k, n cycles, then tails; report first frame with X >= goalX at y <= ytop."""
import sys, itertools, json
sys.path.insert(0, 'work/l43')
from lib import *
mst, F0 = sys.argv[1], int(sys.argv[2]); GX = int(sys.argv[4]) if len(sys.argv) > 4 else 212
YT = int(sys.argv[5]) if len(sys.argv) > 5 else 128
fc = core(mst); fc.save('b'); fc._ka_slot = 'b'
CYC = [('Right',), ('Right', 'Up'), ('Right', 'Up'), ('A', 'Left', 'Up'), ('A', 'Left')]
TAILS = {
    'R': [('Right',)] * 120,
    'AR': [('A', 'Right')] * 2 + [('Right',)] * 118,
    'UR': [('Right', 'Up')] * 8 + [('Right',)] * 112,
    'ALR': [('A', 'Left')] * 2 + [('Right',)] * 118,
    'ALUR': [('A', 'Left', 'Up')] * 2 + [('Right',)] * 118,
    'ALd3R': [('A', 'Left')] * 2 + [()] * 3 + [('Right',)] * 115,
    'ALL4R': [('A', 'Left')] * 2 + [('Left',)] * 4 + [('Right',)] * 114,
}
cands = []; meta = []
H0 = [()] * 40
for d in range(0, 10, 2):
    for k in range(5):
        for n in range(4, 13):
            for tn, tl in TAILS.items():
                cyc = CYC[k:] + CYC[:k]
                want = [()] * d + cyc * n + tl
                en = A.Enforcer(H0)
                cands.append([tuple(sorted(en.emit(w))) for w in want][:200]); meta.append((d, k, n, tn))
print(len(cands), 'candidates', flush=True)
res = []
B = 50
for i in range(0, len(cands), B):
    rr = fc.run_batch('b', cands[i:i + B], record='all')
    for j, r in enumerate(rr):
        top = gx = None; rm0 = None
        for q, s in enumerate(r.states):
            f = F0 + 1 + q
            if rm0 is None: rm0 = s['room']
            if s['room'] != rm0: break
            X_ = C.abs_x(s)
            if top is None and s['y'] <= YT and X_ >= 160 and s['y'] >= YT - 2: top = f
            if gx is None and X_ >= GX and s['y'] <= YT: gx = f; break
        res.append((gx or 99999, top or 99999, meta[i + j]))
res.sort()
for q in res[:20]: print(q)
json.dump(res[:60], open(f'work/l43/lad19_{F0}.json', 'w'))
fc.close()
