"""Room-18 exit grid: rows[:N0] + legalized TAS rows t0..t1 (lag L) with the two run jumps shifted (d1, d2) and an
optional spin at TAS frame sp; reports the room-19 frame and hp.  python work/l43/g18x.py <rows> <lag> <t0> <t1>"""
import sys, json; sys.path.insert(0, 'work/l43')
from lib import *
rows = rows_file(sys.argv[1]); LG = int(sys.argv[2]); t0, t1 = int(sys.argv[3]), int(sys.argv[4])
N0 = t0 - 1 + LG - CTL + 1
pre = rows[:N0]
TR0 = A.tas_rows()
def tas_want(t):
    w = set(TR0[t - 1])
    if 'Up' in w and 'Down' in w: w -= {'Up', 'Down'}
    if 'Left' in w and 'Right' in w: w -= {'Left'}
    return w
J = [t for t in range(t0, t1 + 1) if 'A' in TR0[t - 1] and 'Right' in TR0[t - 1]]
print('N0', N0, 'jumps', J)
fc = core(); fc.step(pre, record='last'); fc.save('b'); fc._ka_slot = 'b'
cands = []; meta = []
D = range(-4, 5)
SP = [None] + list(range(t0, min(t1, t0 + 70), 3))
for d1 in D:
    for d2 in D:
        for sp in SP:
            want = [set(tas_want(t)) - {'A'} if t in J else set(tas_want(t)) for t in range(t0, t1 + 1)]
            for jj, d in zip(J[:2], (d1, d2)):
                k = jj + d - t0
                if 0 <= k < len(want): want[k] |= {'A', 'Right'}
            if sp is not None:
                want[sp - t0] |= {'B'}
            en = enforcer(pre)
            cands.append([tuple(sorted(en.emit(tuple(sorted(w))))) for w in want]); meta.append((d1, d2, sp))
print(len(cands), 'cands', flush=True)
res = []
for i in range(0, len(cands), 60):
    for j, r in enumerate(fc.run_batch('b', cands[i:i + 60], record='all')):
        g = None
        for q, s in enumerate(r.states):
            if s['room'] == 19: g = (CTL + N0 + q, s['hp'], s['ninpo'], s['y'], s['vy']); break
        res.append(((g[0] if g else 99999), -(g[1] if g else 0), meta[i + j], g))
res.sort(key=lambda q: (q[0], q[1]))
for q in res[:15]: print(q)
json.dump([[q[0], q[2]] for q in res[:50]], open('work/l43/g18x.json', 'w'))
fc.close()
