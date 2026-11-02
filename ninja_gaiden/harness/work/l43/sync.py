"""Sync a stage-rows line to the TAS: for each N in [N1, N2], find TAS frames t in [t_lo, t_hi) with the same X/y as
our frame CTL+N-1, append legalized TAS rows t+1..t2, and report how long the line matches the TAS (lag = f - t).
python work/l43/sync.py <rows> N1 N2 t_lo t_hi t2 [--write tag]"""
import sys; sys.path.insert(0, 'work/l43')
from lib import *
a = sys.argv[1:]
tag = None
if '--write' in a:
    i = a.index('--write'); tag = a[i + 1]; del a[i:i + 2]
rows = rows_file(a[0]); N1, N2, tlo, thi, t2 = map(int, a[1:6])
TR0 = A.tas_rows()
fc = core(); fc.save('b0'); fc._ka_slot = 'b0'
_, recs, _ = fc.step(rows[:N2], record='all')
cands = []; meta = []
for N in range(N1, N2 + 1):
    s = recs[N - 1]; X_, y_ = C.abs_x(s), s['y']
    for t in range(tlo, thi):
        if (TX[t], TY[t]) != (X_, y_): continue
        want = []
        for u in range(t + 1, t2 + 1):
            w = set(TR0[u - 1])
            if 'Up' in w and 'Down' in w: w -= {'Up', 'Down'}
            if 'Left' in w and 'Right' in w: w -= {'Left'}
            want.append(tuple(sorted(w)))
        en = enforcer(rows[:N]); add = [tuple(sorted(en.emit(w))) for w in want]
        cands.append(rows[:N] + add); meta.append((N, t, CTL + N - 1 - t))
res = fc.run_batch('b0', cands, record='all')
best = None
for (N, t, lag), c, r in zip(meta, cands, res):
    m = 0; first = None
    for i in range(N, len(c)):
        s = r.states[i]; f = CTL + i; u = f - lag
        if (C.abs_x(s), s['y'], s['room']) == (TX[u], TY[u], TRM[u]): m += 1
        elif first is None: first = (f, u, C.abs_x(s), s['y'], TX[u], TY[u])
    s = r.states[-1]
    print('N', N, 'frame', CTL + N - 1, 't', t, 'lag', lag, 'match', m, '/', len(c) - N, 'first diff', first, 'end X', C.abs_x(s), 'y', s['y'], 'hp', s['hp'], 'np', s['ninpo'])
    if best is None or (first or (99999,))[0] - lag > (best[0][0] if best[0] else 99999) - best[1]: best = (first or (99999,), lag, c)
if tag and best:
    write_rows(f'work/l43/s_{tag}.txt', best[2], f'sync lag {best[1]}'); print('wrote', tag, 'lag', best[1])
fc.close()
