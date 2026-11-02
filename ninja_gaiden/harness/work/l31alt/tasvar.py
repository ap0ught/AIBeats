"""prefix rows[:N] + legalized TAS rows (lag 165) for n rows; print per-10 rows and the first hit.
python work/l31alt/tasvar.py <rows> N n [lag]"""
import sys
sys.path.insert(0, 'work/l31alt')
from lib import *
rows = [tuple(r) for r in C.rows_of(sys.argv[1])]
N = int(sys.argv[2]); n = int(sys.argv[3]); lag = int(sys.argv[4]) if len(sys.argv) > 4 else 165
TR = A.tas_rows(); TT = A.tas_trace()
want = [tuple(TR[F0 + N + k - lag]) for k in range(n)]
if '--nothrow' in sys.argv: want = [('Right',) if ('Up' in w and 'B' in w) else w for w in want]
lg = legal_after(rows[:N], want)
fc = core(); fc.step(rows[:N], record='last'); m = fc.ram(); hp0 = m[0x65]
for k, r in enumerate(lg):
    fc.step([r], record='last'); m = fc.ram(); t = TT[F0 + N + k + 1 - lag]
    if k % 10 == 0 or m[0x65] < hp0 or r != want[k]:
        print(N + k + 1, F0 + N + k + 1, '+'.join(r) or '-', ('(want ' + '+'.join(want[k]) + ')') if r != want[k] else '', 'X', X(m), 'y', m[0x8A], 'hp', m[0x65], 'np', m[0x64], 'it', m[0xC9], '| TAS X', C.abs_x(t), 'y', t['y'], 'np', t['ninpo'], 'it', t['item'])
    if m[0x65] < hp0: break
fc.close()
