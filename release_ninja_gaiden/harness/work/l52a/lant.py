"""+10 lantern X 352 y 96 (room 23): add a B (2 f) at frame f on the b_r23a line; report np and X at 25,272."""
import sys; sys.path.insert(0,'work/l52a')
from lib2 import *
pre = rows_file('work/l52p/pre52_24625.txt'); b = rows_file('work/l52p/b_r23a.txt')
base = pre[:174] + b; H = chain_hist()
fc = core(BASE52); fc.step(base[:200], record='last'); fc.save('m'); fc._ka_slot = 'm'   # after row 25,197
names, cands = [], []
for f in range(25200, 25262):
    for k in (2, 3):
        for extra in ('B', 'B+Up'):
            rows = list(base)
            for j in range(k):
                i = f - CTL52 + j
                rows[i] = tuple(sorted(set(rows[i]) | set(extra.split('+'))))
            if legal_ok(rows, H): continue
            names.append((f, k, extra)); cands.append(rows[200:])
print('cands', len(cands))
rs = fc.run_batch('m', cands, record='all')
best = []
for n, r in zip(names, rs):
    s = r.states[-1]; npm = max(x['np64'] for x in r.states)
    xs = [RXY(x)[0] for x in r.states]
    if npm > 40: print(n, 'np max', npm, 'end', RXY(s), 'np', s['np64'], 'hp', s['hp65'], 'it', s['item'])
fc.close()
