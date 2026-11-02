"""On w1: add a B (2 f, with the row's own buttons) at our frame b in a window; does the X-929 type 3 die, does the
X-1,136 type 11 spawn (~23,302), any hit to 23,589?  python work/l51b/t3kill.py b1 b2"""
import sys
sys.path.insert(0, 'work/l51b')
from lb import *
b1, b2 = int(sys.argv[1]), int(sys.argv[2])
W = [set(r) for r in C.rows_of('work/l51a/w1_23589.txt')]
hist = [tuple(sorted(r)) for r in C.rows_of('logs/l44p_r1920_c2_poweron.inputs.txt')]
fc = core('states/mesen/lock_51_pre.mst')
S0 = 23150
fc.step([tuple(sorted(r)) for r in enforce(W[:S0 - 22628], hist)], record='last'); fc.save('b'); fc._ka_slot = 'b'
for b in range(b1, b2):
    w = [set(r) for r in W]
    for f in (b, b + 1): w[f - 22629] = w[f - 22629] | {'B'}
    rows = enforce(w, hist)
    lg = legal_ok(rows, hist)
    _, recs, _ = fc.run_batch('b', [rows[S0 - 22628:]], record='all')[0][:3] if False else (None, fc.run_batch('b', [rows[S0 - 22628:]], record='all')[0].states, None)
    hits = trackhits(recs, S0 + 1)
    t11 = [S0 + 1 + i for i, r in enumerate(recs) if any(r['eact'] >> j & 1 and r[f't{j}'] == 11 for j in range(8)) and S0 + 1 + i > 23280]
    t3 = [S0 + 1 + i for i, r in enumerate(recs) if any(r['eact'] >> j & 1 and r[f't{j}'] == 3 and r[f'ey{j}'] == 160 for j in range(8))]
    X, y = RXY(recs[-1])
    print(b, 'legal', lg or 'ok', 'hits', hits, 't11 from', t11[:1], 'n', len(t11), 't3(y160) last', t3[-1:] , 'end', (X, y), flush=True)
fc.close()
