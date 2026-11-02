"""On w1: move the air turn (Left x n at our f) and check the X-1,136 type-11 spawn + hits/death to 23,589."""
import sys
sys.path.insert(0, 'work/l51b')
from lb import *
W = [set(r) for r in C.rows_of('work/l51a/w1_23589.txt')]
hist = [tuple(sorted(r)) for r in C.rows_of('logs/l44p_r1920_c2_poweron.inputs.txt')]
fc = core('states/mesen/lock_51_pre.mst')
S0 = 23280
fc.step(enforce(W[:S0 - 22628], hist), record='last'); fc.save('b'); fc._ka_slot = 'b'
for n in (2, 3):
    for f in range(23294, 23310):
        w = [set(r) for r in W]
        w[23298 - 22629] = {'Right'}; w[23299 - 22629] = {'Right'}
        for g in range(f, f + n): w[g - 22629] = {'Left'}
        rows = enforce(w, hist); lg = legal_ok(rows, hist)
        recs = fc.run_batch('b', [rows[S0 - 22628:]], record='all')[0].states
        hits = trackhits(recs, S0 + 1)
        sp = next((S0 + 1 + i for i, r in enumerate(recs) if any(r['eact'] >> j & 1 and r[f't{j}'] == 11 for j in range(8))), None)
        X, y = RXY(recs[-1]); dead = next((S0 + 1 + i for i, r in enumerate(recs) if r['y8a'] >= 232), None)
        print(n, f, f - 509, 'legal', lg or 'ok', 't11 spawn', sp, 'hits', hits, 'dead', dead, 'end', (X, y), flush=True)
fc.close()
