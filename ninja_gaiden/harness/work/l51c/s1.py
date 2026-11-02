"""Search 1: insert w blank rows before our row s on the c1 line (after the climb, base 23,663), then the c1 rows to
24,200 (= legal TAS rows lag 530) + legal TAS rows from TAS 23,671. Does the WALL bird (kept alive, slot 7) take the
TAS's orbit and give the 23,714 boost? python work/l51c/s1.py s0 s1 sstep w0 w1 part nparts out"""
import sys, json; sys.path.insert(0, 'work/l51c')
from lc import *
s0, s1, ss, w0, w1, part, npart, out = sys.argv[1:9]
s0, s1, ss, w0, w1, part, npart = map(int, (s0, s1, ss, w0, w1, part, npart))
F0 = 23663; MST = 'states/mesen/l51c_c1_23663.mst'
rows = c1rows(); hist = rows[:F0]
base = [set(r) for r in rows[F0:24200]] + tasleg(23671, 23800)
jobs = [(s, w) for s in range(s0, s1 + 1, ss) for w in range(w0, w1 + 1)]
jobs = jobs[part::npart]
fc = core(MST); fc.save('b'); fc._ka_slot = 'b'
fo = open(out, 'a')
for i in range(0, len(jobs), 20):
    ch = jobs[i:i+20]; cands = []
    for s, w in ch:
        k = s - F0 - 1
        want = base[:k] + [set()] * w + base[k:]
        cands.append(enforce(want, hist))
    rr = fc.run_batch('b', cands, record='all', stops=[(0x8A, '>=', 0xE4)])
    for (s, w), r in zip(ch, rr):
        st = r.states; lag = 530 + w
        hp = 12; hits = []
        plat = None; bird = {}
        for t, x in enumerate(st):
            f = F0 + 1 + t; te = f - 504 - lag if f >= s else f - 504 - 530
            X, y = RXY(x)
            if x['hp65'] != hp:
                hits.append((te, X, y, hp, x['hp65'])); hp = x['hp65']
            if plat is None and y <= 96 and X >= 2436: plat = te
            if te in (23200, 23300, 23355, 23450, 23550, 23670, 23700) and x['eact'] >> 7 & 1 and x['t7'] == 11:
                hi = x['scr_hi']; hi = hi - 256 if hi >= 128 else hi
                bird[te] = (hi*256 + x['scr_lo'] + x['ex7'] - X, x['ey7'] - y)
        X, y = RXY(st[-1])
        fo.write(json.dumps(dict(s=s, w=w, plat=plat, hits=hits, bird=bird, end=(F0 + len(st), X, y))) + '\n')
    fo.flush()
fc.close()
