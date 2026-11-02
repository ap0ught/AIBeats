"""Play legalized TAS rows after our power-on rows on Mesen; report divergence from the TAS line.
    python -u work/rep/mfollow.py <power-on rows file> <k0 TAS frame (auto if 'auto')> <n> [--shift-print 25] [--out f]
The legalized rows are TAS rows k0..k0+n-1 (row index k = frame k+1), legalized against our history."""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages')
from ng.solve import common as C, legality as L
from ng import fastcore as F
import a56_common as A
a = sys.argv[1:]
out = None
keep = None
if '--keep' in a:
    i = a.index('--keep'); keep = int(a[i + 1]); del a[i:i + 2]
if '--out' in a:
    i = a.index('--out'); out = a[i + 1]; del a[i:i + 2]
hist = C.rows_of(a[0]); n = int(a[2])
T = A.tas_trace(); TR = A.tas_rows()
fc = F.FastCore(boot_rows=hist)
r = fc.ram()
s0 = dict(x=r[0x86], y=r[0x8A])
if a[1] == 'auto':
    # TAS frame with the same abs X and y nearest in time
    _, recs, _ = fc.step([], record='last') if False else (0, [], 0)
    st = fc.step([()], record='last')[1][-1]  # costs one frame: undo by re-boot
    fc.close(); fc = F.FastCore(boot_rows=hist)
    X = C.abs_x(st); best = None
    for k in range(174, 2470):
        t = T[k]
        if t['stage'] != st['stage']: continue
        d = abs(C.abs_x(t) - X) + abs(t['y'] - st['y'])
        if best is None or d < best[0]: best = (d, k)
    k0 = best[1] - 1
    print('auto k0', k0, 'match dist', best[0], 'ours X', X, 'y', st['y'])
else:
    k0 = int(a[1])
rows = L.legalize(TR[k0:k0 + n], hist[-1900:])
_, recs, _ = fc.step(rows, record='all'); fc.close()
f0 = len(hist)
div = None
for i, s in enumerate(recs):
    t = T[k0 + i + 1]
    dx = C.abs_x(s) - C.abs_x(t); dy = s['y'] - t['y']
    if div is None and (abs(dx) > 2 or abs(dy) > 2 or s['hp'] != t['hp'] - (T[k0+1]['hp'] - recs[0]['hp'])):
        div = i
    if i % 25 == 0 or i == div or s['stage'] != 0:
        print(f"i {i} f {f0+i+1} X {C.abs_x(s)} y {s['y']} hp {s['hp']} np {s['ninpo']} | TAS {k0+i+1} X {C.abs_x(t)} y {t['y']} hp {t['hp']} np {t['ninpo']}" + ('  <== first divergence' if i == div else ''))
    if s['stage'] != 0: break
print('lag vs TAS (frames):', f0 - k0, 'first divergence row', div)
if out:
    m = keep if keep is not None else (div if div is not None else len(rows))
    C.write_inputs(out, list(hist[174:]) + list(rows[:m]), f'1-1 rows + legalized TAS {k0}..{k0+m}')
