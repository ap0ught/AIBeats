"""Get onto the y-96 platform (X 2,336-2,431) from the y-160 step by a bird hit: enumerate waits/jumps.
python work/l51b/p96.py <mst> F0 <hist>   (rows: P*w + J1 + drift + [P2*w2 + J2 + drift2] + R...)"""
import sys, itertools
sys.path.insert(0, 'work/l51b')
from lb import *
mst, F0, H = sys.argv[1], int(sys.argv[2]), sys.argv[3]
hist = [tuple(sorted(r)) for r in C.rows_of(H)]
R_, N_, L_ = ('Right',), (), ('Left',)
D = {'R': R_, '-': N_, 'L': L_}
cands = []; seen = set()
for w in range(0, 44, 2):
    for wd in ('-', 'L', 'R'):
        if wd == 'R' and w > 6: continue
        for jd in ('R', '-', 'L'):
            for w2 in (None, 0, 4, 8):
                for jd2 in (('R', '-') if w2 is not None else ('R',)):
                    rows = [D[wd]] * w + [('A',) + D[jd]] * 2 + [D[jd]] * 30
                    if w2 is not None:
                        rows += [N_] * w2 + [('A',) + D[jd2]] * 2 + [D[jd2]] * 30
                    rows = (rows + [R_] * 140)[:140]
                    rows = enforce([set(r) for r in rows], hist)
                    if legal_ok(rows, hist) or tuple(rows) in seen: continue
                    seen.add(tuple(rows)); cands.append(((w, wd, jd, w2, jd2), rows))
print('cands', len(cands), flush=True)
fc = core(mst); fc.save('b'); fc._ka_slot = 'b'
res = []
for i in range(0, len(cands), 100):
    ch = cands[i:i+100]
    rr = fc.run_batch('b', [r for _, r in ch], record='all')
    for (k, rows), r in zip(ch, rr):
        st = r.states
        g = next((t for t, s in enumerate(st) if s['y8a'] == 96 and 2336 <= RXY(s)[0] <= 2440 and s['rf84'] & 4 == 0), None)
        # progress: first frame X >= 2436 on y 96 (jump-off point)
        g2 = next((t for t, s in enumerate(st) if s['y8a'] <= 96 and RXY(s)[0] >= 2436), None)
        res.append((F0 + 1 + g2 if g2 is not None else 99999, F0 + 1 + g if g is not None else 99999, k, min(s['hp65'] for s in st)))
res.sort(key=lambda q: q[:2])
for x in res[:25]: print(x, flush=True)
fc.close()
