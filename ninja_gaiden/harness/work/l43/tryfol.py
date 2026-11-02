"""Approximate TAS follow: rows[:N] (N in [N1,N2]) + legalized TAS rows t..t2 for t = frame - lag + d (d in [-D, D]);
report the first frame in room <rm> (and hp/anim there). python work/l43/tryfol.py <rows> N1 N2 lag D t2 rm [step]"""
import sys; sys.path.insert(0, 'work/l43')
from lib import *
a = sys.argv[1:]
rows = rows_file(a[0]); N1, N2, LG, D, t2, RM = map(int, a[1:7]); ST = int(a[7]) if len(a) > 7 else 1
TR0 = A.tas_rows()
def tw(t):
    w = set(TR0[t - 1])
    if 'Up' in w and 'Down' in w: w -= {'Up', 'Down'}
    if 'Left' in w and 'Right' in w: w -= {'Left'}
    return tuple(sorted(w))
fc = core(); fc.save('b0'); fc._ka_slot = 'b0'
fc.step(rows[:N1], record='last'); fc.save('b1')
cands = []; meta = []
for N in range(N1, N2 + 1, ST):
    f = CTL + N - 1
    for d in range(-D, D + 1):
        t = f - LG + d
        en = enforcer(rows[:N]); add = [tuple(sorted(en.emit(tw(u)))) for u in range(t + 1, t2 + 1)]
        cands.append(rows[N1:N] + add); meta.append((N, f, t, f - t))
res = []
for i in range(0, len(cands), 60):
    for m, r in zip(meta[i:i + 60], fc.run_batch('b1', cands[i:i + 60], record='all')):
        g = None
        for q, s in enumerate(r.states):
            if s['room'] == RM: g = (CTL + N1 + q, s['hp'], s['anim']); break
        res.append(((g[0] if g else 99999), m, g))
res.sort()
for q in res[:12]: print(q)
fc.close()
