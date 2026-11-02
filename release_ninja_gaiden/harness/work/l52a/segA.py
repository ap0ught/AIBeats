"""segment A: b_r23a (+B 25,218-19 for the +10) to 25,272, then legalized TAS rows 24,689.. at lag L, walk off the y-96 platform
(Left only after TAS 24,766), then a B slash at frame s for the J&S. Prints the trace."""
import sys; sys.path.insert(0,'work/l52a')
from lib2 import *
L = int(sys.argv[1]) if len(sys.argv) > 1 else 584
pre = rows_file('work/l52p/pre52_24625.txt'); b = rows_file('work/l52p/b_r23a.txt')
base = pre[:174] + b
for f in (25218, 25219): base[f - CTL52] = tuple(sorted(set(base[f - CTL52]) | {'B'}))
H = chain_hist()
en = A.Enforcer(H + base)
want = []
for t in range(24689, 24767):
    w = set(T(t)); want.append(w)
want += [{'Left'}] * 80
rows = base + [tuple(sorted(en.emit(tuple(sorted(w))))) for w in want]
print('legal', repr(legal_ok(rows, H)))
FLD.update(dict(act=0x80, tch=0x8C, fl=0x84))
fc = core(BASE52)
_, recs, _ = fc.step(rows, record='all'); fc.close()
for i, s in enumerate(recs):
    f = CTL52 + i
    if f >= 25270: print(f, RXY(s), 'hp', s['hp65'], 'np', s['np64'], 'it', s['item'], 'act', s['act'], 'tch', hex(s['tch']), P(rows[i]))
wr('work/l52a/segA_rows.txt', rows, 'segA from row 24998')
