"""J&S via a Windmill throw: rows Up+B, Left+Up+B at frame s (or Up+B x2) on segA rows; report pickup, X at 25,400, np, hp."""
import sys; sys.path.insert(0,'work/l52a')
from lib2 import *
rows = rows_file('work/l52a/segA_rows.txt'); H = chain_hist()
F0 = 25300
fc = core(BASE52); fc.step(rows[:F0 - CTL52 + 1], record='last'); fc.save('m'); fc._ka_slot = 'm'
names, cands = [], []
for s in range(25305, 25372):
    for v in ('a', 'b'):
        r = list(rows)
        i = s - CTL52
        if v == 'a': r[i] = ('B', 'Up'); r[i+1] = ('B', 'Left', 'Up')
        else: r[i] = ('B', 'Up'); r[i+1] = ('B', 'Up')
        if legal_ok(r[:i + 10], H): continue
        names.append((s, v)); cands.append(r[F0 - CTL52 + 1:25420 - CTL52])
rs = fc.run_batch('m', cands, record='all')
for n, r in zip(names, rs):
    got = [F0 + 1 + i for i, st in enumerate(r.states) if st['item'] == 133][:1]
    s4 = r.states[25400 - F0 - 1]
    print(n, 'J&S at', got, 'X@25400', RXY(s4), 'np', s4['np64'], 'hp', min(st['hp65'] for st in r.states))
fc.close()
