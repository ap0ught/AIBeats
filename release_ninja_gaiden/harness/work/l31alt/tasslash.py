"""TAS rows (lag 165, no throws) after prefix rows[:N], with B added on chosen rows; greedy: find slash rows that
avoid hits. python work/l31alt/tasslash.py <rows> N n [fixed slash rows comma] [scan lo hi]"""
import sys
sys.path.insert(0, 'work/l31alt')
from lib import *
rows = [tuple(r) for r in C.rows_of(sys.argv[1])]
N = int(sys.argv[2]); n = int(sys.argv[3])
fixed = [int(q) for q in sys.argv[4].split(',') if q] if len(sys.argv) > 4 else []
lo, hi = (int(sys.argv[5]), int(sys.argv[6])) if len(sys.argv) > 6 else (N, N)
TR = A.tas_rows()
base = [tuple(TR[F0 + N + k - 165]) for k in range(n)]
base = [('Right',) if ('Up' in w and 'B' in w) else w for w in base]
fc = core(); fc.step(rows[:N], record='last'); fc.save('p'); hp0 = fc.ram()[0x65]
def ev(sl):
    want = [tuple(sorted(set(w) | {'B'})) if (N + k + 1) in sl else w for k, w in enumerate(base)]
    lg = legal_after(rows[:N], want)
    fc.load('p'); _, recs, _ = fc.step(lg, record='all')
    hit = next((k for k, s in enumerate(recs) if s['hp'] < hp0), None)
    return hit, recs[-1], lg
h, s, _ = ev(set(fixed)); print('fixed', fixed, 'first hit row', None if h is None else N + h + 1, 'end X', C.abs_x(s), 'hp', s['hp'])
for j in range(lo, hi + 1):
    h, s, lg = ev(set(fixed) | {j})
    print('add', j, 'first hit row', None if h is None else N + h + 1, 'end X', C.abs_x(s), 'y', s['y'], 'hp', s['hp'], 'np', s['ninpo'], 'it', s['item'])
fc.close()
