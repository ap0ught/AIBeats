"""Edit stage rows (--set row=SPEC,..; row = stage row number, 1 = frame 16,998) -> out; play on Mesen and print where
it first differs from the TAS (lag) and the end. python work/l42a/ed.py <in> <out> --set 77=Right,78=A+Right [--lag 316]"""
import sys
sys.path.insert(0, 'work/l42a')
from lib import *
a = sys.argv[1:]
lag = LAG0; sets = {}
if '--lag' in a: i = a.index('--lag'); lag = int(a[i+1]); del a[i:i+2]
if '--set' in a:
    i = a.index('--set')
    for q in a[i+1].split(','):
        k, v = q.split('='); sets[int(k)] = row(v)
    del a[i:i+2]
rows = [tuple(r) for r in C.rows_of(a[0])]
for k, v in sets.items(): rows[k - 1] = v
chk = L.check(rows, HIST)
fc = core(); _, recs, _ = fc.step(rows, record='all'); fc.close()
div = None
for i, s in enumerate(recs):
    t = TT[F0 + 1 + i - lag]
    if (C.abs_x(s), s['y']) != (C.abs_x(t), t['y']): div = (F0 + 1 + i, C.abs_x(s), s['y'], 'TAS', C.abs_x(t), t['y']); break
s = recs[-1]
print('legal', chk.get('pass'), 'first TAS div', div, 'end', F0 + len(rows), 'X', C.abs_x(s), 'y', s['y'], 'hp', s['hp'], 'np', s['ninpo'], 'it', s['item'])
C.write_inputs(a[1], rows, f'ed {" ".join(sys.argv[1:])}')
