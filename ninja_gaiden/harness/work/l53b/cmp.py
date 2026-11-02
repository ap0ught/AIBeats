"""l53b: run TAS pad bytes (raw, banned ones included) from our state and from the TAS state, compare per frame.
python work/l53b/cmp.py <our mst> <our frame f0> <TAS frame t0> <n> [--rows file (rows from f0+1, used for both)]"""
import sys
sys.path.insert(0, 'work/l53p'); sys.path.insert(0, 'work/l53b')
from lb import *
a = sys.argv[1:]
RF = ''
if '--rows' in a: i = a.index('--rows'); RF = a[i+1]; del a[i:i+2]
mst, f0, t0, n = a[0], int(a[1]), int(a[2]), int(a[3])
if RF: rows = [row(l.strip()) for l in open(RF) if l.strip() and not l.startswith('#')][:n]
else: rows = [TM(g)[0x2A] for g in range(t0 + 1, t0 + n + 1)]
fc = core(mst); _, A_, _ = fc.step(rows, record='all'); fc.close()
fc = core_at(t0); _, B_, _ = fc.step(rows, record='all'); fc.close()
first = None; ph = None
for i, (s, t) in enumerate(zip(A_, B_)):
    ev = []
    if (RXY(s), s['hp65']) != (RXY(t), t['hp65']) and first is None: first = i; ev.append('FIRST DIFF')
    if ph and (s['hp65'] != ph[0] or s['np64'] != ph[1] or s['room6e'] != ph[2]): ev.append(f"ours hp {s['hp65']} np {s['np64']} rm {s['room6e']}")
    ph = (s['hp65'], s['np64'], s['room6e'])
    if ev or i % 25 == 0:
        print(f0 + 1 + i, t0 + 1 + i, 'ours', RXY(s), s['hp65'], 'tasst', RXY(t), t['hp65'], ' '.join(ev))
print('first diff at row', first)
