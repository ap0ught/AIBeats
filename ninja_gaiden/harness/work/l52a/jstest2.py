"""J&S pickup during the walk-off: insert w blank rows at frame p (on the platform or in the air), B (2-3 f) at frame s."""
import sys; sys.path.insert(0,'work/l52a')
from lib2 import *
rows = rows_file('work/l52a/segA_rows.txt'); H = chain_hist()
F0 = 25330
fc = core(BASE52); fc.step(rows[:F0 - CTL52 + 1], record='last'); fc.save('m'); fc._ka_slot = 'm'
names, cands = [], []
for w in range(0, 7):
    for p in ([25345, 25352, 25358] if w else [0]):
        for s in range(25356, 25380):
            for k in (2,):
                r = list(rows[:F0 - CTL52 + 1]) + list(rows[F0 - CTL52 + 1:])
                if w:
                    i = p - CTL52; r = r[:i] + [()] * w + r[i:]
                for j in range(k):
                    r[s - CTL52 + j] = tuple(sorted(set(r[s - CTL52 + j]) | {'B'}))
                if legal_ok(r[:s - CTL52 + 10], H): continue
                names.append((w, p, s)); cands.append(r[F0 - CTL52 + 1:25420 - CTL52])
print(len(cands))
rs = fc.run_batch('m', cands, record='all')
res = []
for n, r in zip(names, rs):
    for i, st in enumerate(r.states):
        if st['item'] == 133:
            # time-equivalent: x at frame 25,400
            s4 = r.states[25400 - F0 - 1]
            res.append((-RXY(s4)[0], n, 25331 + i, RXY(s4), s4['hp65'])); break
res.sort(key=lambda q: q[0])
for x in res[:20]: print(x)
print('found', len(res))
fc.close()
