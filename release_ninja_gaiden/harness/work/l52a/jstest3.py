"""J&S: w blanks at p (any frame 25,330-25,395) + B (2 f) at s; find the cheapest (X at 25,400 max)."""
import sys; sys.path.insert(0,'work/l52a')
from lib2 import *
rows = rows_file('work/l52a/segA_rows.txt'); H = chain_hist()
F0 = 25329
fc = core(BASE52); fc.step(rows[:F0 - CTL52 + 1], record='last'); fc.save('m'); fc._ka_slot = 'm'
names, cands = [], []
for w in (1, 2, 3, 4):
    for p in range(25331, 25396, 2):
        for s in range(25358, 25372):
            r = list(rows); i = p - CTL52; r = r[:i] + [()] * w + r[i:]
            for j in range(2):
                r[s - CTL52 + j] = tuple(sorted(set(r[s - CTL52 + j]) | {'B'}))
            if legal_ok(r[:25402 - CTL52], H): continue
            names.append((w, p, s)); cands.append(r[F0 - CTL52 + 1:25402 - CTL52])
print(len(cands), flush=True)
res = []
for k in range(0, len(cands), 256):
    rs = fc.run_batch('m', cands[k:k+256], record='all')
    for n, r in zip(names[k:k+256], rs):
        got = [F0 + 1 + i for i, st in enumerate(r.states) if st['item'] == 133][:1]
        if got: res.append((-RXY(r.states[-1])[0], n, got, RXY(r.states[-1]), min(st['hp65'] for st in r.states)))
res.sort(key=lambda q: -q[0])
for x in res[:15]: print(x)
print('found', len(res))
fc.close()
