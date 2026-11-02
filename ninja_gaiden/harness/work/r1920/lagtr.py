"""Trace stage rows from a Mesen state and print the TAS-path lag (f - nearest TAS frame) every k frames.
python work/r1920/lagtr.py <mst> <F> <rows> <t1> <t2> [step]"""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'work/l31t'); sys.path.insert(0, 'work/r1920'); 
sys.path.insert(0, 'work/l43p')
import fcka
from ng import fastcore as F
from ng.solve import common as C
from gbeam import FL, X
import importlib.util as _u
_sp=_u.spec_from_file_location('l43plib','work/l43p/lib.py'); _m=_u.module_from_spec(_sp); _sp.loader.exec_module(_m); TM, XY = _m.TM, _m.XY
mst, F0, rf, t1, t2 = sys.argv[1], int(sys.argv[2]), sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
st = int(sys.argv[6]) if len(sys.argv) > 6 else 10
rows = [tuple(r) for r in C.rows_of(rf)]
fc = F.FastCore(boot_rows=None, ticks=True, fields=FL)
fc.put('s', open(mst, 'rb').read()); fc.load('s'); fc._ka_slot = 's'
_, recs, _ = fc.step(rows, record='all'); fc.close()
T = [(t,) + XY(TM(t)) + (TM(t)[0x6E],) for t in range(t1, t2 + 1)]
for i, s in enumerate(recs):
    if i % st and i != len(recs) - 1: continue
    x, y = X(s), s['y']
    bt, bd = min(((t, abs(x - tx) + 0.5 * abs(y - ty)) for t, tx, ty, rm in T if rm == s['room']), key=lambda z: z[1], default=(0, 0))
    print(F0 + i + 1, '+'.join(rows[i]) or '-', 'rm', s['room'], 'X', x, 'y', y, 'hp', s['hp'], 'np', s['np'], '| nearest TAS', bt, 'd', round(bd, 1), 'lag', F0 + i + 1 - bt)
