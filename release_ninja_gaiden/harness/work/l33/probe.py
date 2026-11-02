"""python work/l33/probe.py <tag> <rows file or 'tas'> [n] [--legal] : per-frame trace from 3-3 control (Mesen)."""
import sys
sys.path.insert(0, 'work/l33'); sys.path.insert(0, 'ng/stages')
from lib import *
tag, src = sys.argv[1], sys.argv[2]
n = int(sys.argv[3]) if len(sys.argv) > 3 and not sys.argv[3].startswith('-') else 200
if src == 'tas':
    import a56_common as A
    rows = [tuple(sorted(r)) for r in A.tas_rows()[13740:13740 + n]]
else:
    rows = [tuple(sorted(r)) for r in C.rows_of(src)][:n]
if '--legal' in sys.argv:
    rows = legal_after([], rows, hist(tag))
fc = core(tag)
_, recs, _ = fc.step(rows, record='all')
fc.close()
for i, (w, s) in enumerate(zip(rows, recs)):
    sl = ' '.join(f"{s[f't{k}']:02x}" for k in range(8))
    print(f"{i+1:3d} {'+'.join(w) or '-':14s} x{s['x']:3d} y{s['y']:3d} an{s['anim']:2d} hp{s['hp']:2d} np{s['ninpo']:2d} boss{s['boss_real']:2d} bh{s['bosshp']:2d} tm{s['timer']:3d}.{s['subtimer']:2d} st{s['stage']} bf{s['bf']:3d} e{s['eact']:02x} inv{s['inv']:3d} | {sl}")
