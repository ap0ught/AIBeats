"""Chain test on the REAL state: head start (pre51) + legalized TAS rows at lag LAG to TAS END.
python work/l51b/ch.py LAG END [mods like 22793-22794=Left,23279-23280=A+Right]"""
import sys
sys.path.insert(0, 'work/l51b')
from lb import *
LAG = int(sys.argv[1]); END = int(sys.argv[2])
mods = {22793: {'Left'}, 22794: {'Left'}, 23279: {'A', 'Right'}, 23280: {'A', 'Right'}}
if len(sys.argv) > 3:
    for it in sys.argv[3].split(','):
        k, v = it.split('='); k1, k2 = (k.split('-') + [k])[:2]
        for t in range(int(k1), int(k2) + 1): mods[t] = set(row(v))
head = [set(r) for r in C.rows_of('work/l51p/pre51_22490.txt')]
want = head + tasleg(22490 - LAG + 1, END, mods)
hist = powhist(); rows = enforce(want, hist)
print('legal', legal_ok(rows, hist) or 'ok', len(rows), flush=True)
fc = core(REAL0)
_, recs, _ = fc.step(rows, record='all')
print('hits', trackhits(recs, CTL))
for i, r in enumerate(recs):
    t = 22125 + i - (LAG if i >= 366 else 2)
    if t % 20 == 0 or i == len(recs) - 1:
        X, y = RXY(r); print(CTL + i, 'TASeq', t, 'X,y', (X, y), 'TAS', tas_xy(t) if t > 22125 else '', 'hp', r['hp65'], 'np', r['np64'])
fc.close()
