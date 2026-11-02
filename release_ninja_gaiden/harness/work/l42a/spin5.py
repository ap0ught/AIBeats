"""Poke ninpo 5 on the s1499 line at frame P (default 18,478), continue legal TAS rows (lag 316; TAS B -> Down+B), add a
J&S spin (air B, 2 rows) at k; report hits and the TAS-distance at checkpoints. python work/l42a/spin5.py [P] [k1-k2]"""
import sys
sys.path.insert(0, 'work/l42a')
from lib import *
P = int(sys.argv[1]) if len(sys.argv) > 1 else 18478
k1, k2 = map(int, (sys.argv[2] if len(sys.argv) > 2 else '18480-18530').split('-'))
END = int(sys.argv[3]) if len(sys.argv) > 3 else 18760
base = [tuple(r) for r in C.rows_of('work/l42a/s1499.txt')]
fc = core(); fc.step(base[:P - F0], record='last'); fc.poke(0x64, 5); fc.save('b'); fc._ka_slot = 'b'
def tasrow(f):
    w = set(unud(TR[f - 316 - 1]))
    if 'B' in w and 'Up' not in w: w |= {'Down'}
    if 'Up' in w and 'B' in w: w = {'Right'}
    return w
batch = []; meta = []
for k in [None] + list(range(k1, k2 + 1)):
    want = []
    for f in range(P + 1, END + 1):
        w = set(base[f - F0 - 1]) if f - F0 - 1 < len(base) else tasrow(f)
        if 'B' in w: w |= {'Down'}
        if k and f in (k, k + 1): w = (w - {'Down'}) | {'B'}
        want.append(tuple(sorted(w)))
    batch.append(legal_after(base[:P - F0], want)); meta.append(k)
rr = fc.run_batch('b', batch, record='all')
for k, r in zip(meta, rr):
    st = r.states; hits = [(P + 1 + i, s['hp']) for i, s in enumerate(st) if i and s['hp'] < st[i - 1]['hp']]
    spin = [P + 1 + i for i, s in enumerate(st) if i and s['ninpo'] < st[i - 1]['ninpo']]
    div = next((P + 1 + i for i, s in enumerate(st) if abs(C.abs_x(s) - C.abs_x(TT[P + 1 + i - 316])) > 4), None)
    e = st[-1]
    print(k, 'spin', spin[:2], 'hits', hits[:4], 'div>4px', div, 'end X', C.abs_x(e), 'y', e['y'], 'hp', e['hp'], 'np', e['ninpo'], 'it', e['item'], 'TAS X', C.abs_x(TT[END - 316]), flush=True)
fc.close()
