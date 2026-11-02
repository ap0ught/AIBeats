"""J&S lantern (144,112): B (k f) at frame s on segA rows; report the item change frame."""
import sys; sys.path.insert(0,'work/l52a')
from lib2 import *
rows = rows_file('work/l52a/segA_rows.txt'); H = chain_hist()
fc = core(BASE52); fc.step(rows[:25340 - CTL52 + 1], record='last'); fc.save('m'); fc._ka_slot = 'm'
names, cands = [], []
for s in range(25344, 25400):
    for k in (2, 3):
        for ex in (('B',), ('B', 'Down')):
            r = list(rows)
            for j in range(k):
                r[s - CTL52 + j] = tuple(sorted(set(r[s - CTL52 + j]) | set(ex)))
            if legal_ok(r[:s - CTL52 + 20], H): continue
            names.append((s, k, ex)); cands.append(r[25341 - CTL52:25420 - CTL52])
rs = fc.run_batch('m', cands, record='all')
for n, r in zip(names, rs):
    for i, st in enumerate(r.states):
        if st['item'] != 130:
            print(n, 'item', st['item'], 'at', 25341 + i, RXY(st), 'np', st['np64']); break
fc.close()
