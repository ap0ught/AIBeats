"""Body-boost scan at tosser 1: base rows[:k0] then Right with a jump A+Right at row j (held h rows), Right after.
python work/l32a/bscan.py rows k0 jlo jhi [--h 2] [--n 60] [--face j2]"""
import sys
sys.path.insert(0, 'work/l32a')
from lib import *
a = sys.argv[1:]
def opt(nm, d):
    if nm in a:
        i = a.index(nm); v = a[i + 1]; del a[i:i + 2]; return type(d)(v)
    return d
hh = opt('--h', 2); n = opt('--n', 60); lft = opt('--left', '')
rows = [tuple(r) for r in C.rows_of(a[0])]; k0, jlo, jhi = int(a[1]), int(a[2]), int(a[3])
fc = core(); fc.step(rows[:k0], record='last'); fc.save('p')
for j in range(jlo, jhi + 1):
    want = []
    for k in range(k0, k0 + n):
        r = ('Right',)
        if j <= k + 1 < j + hh: r = ('A', 'Right')
        want.append(r)
    lg = legal_after(rows[:k0], want)
    fc.load('p'); _, recs, _ = fc.step(lg, record='all')
    hit = next((i for i, s in enumerate(recs) if s['hp'] < 16), None)
    br = next((i for i, s in enumerate(recs) if s['y'] == 128 and 1050 <= C.abs_x(s) <= 1090 and s['anim'] in (0, 1)), None)
    top = next((i for i, s in enumerate(recs) if s['y'] <= 96 and C.abs_x(s) >= 1090), None)
    hs = recs[hit] if hit is not None else None
    miny = min(s['y'] for s in recs)
    print('jump row', j, 'hit', (k0 + hit + 1, C.abs_x(hs), hs['y']) if hs else None, 'branch', (k0 + br + 1) if br is not None else None, 'top', (k0 + top + 1) if top is not None else None, 'miny', miny, 'end', C.abs_x(recs[-1]), recs[-1]['y'], recs[-1]['anim'])
fc.close()
