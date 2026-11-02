"""Free frames at the 4-2 start: c3b rows to frame P0, then variants of Right before/at control 17,020, then Right.
Prints X per frame 17,015-17,030 and X at 17,060."""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'work/l31t')
import fcka
from ng import fastcore as F
from ng.solve import common as C
S = C.rows_of('logs/l41_c3b.inputs.txt')
fc = F.FastCore(boot_rows=None, ticks=True)
fc.put('q', open('states/mesen/l41q_ctl.mst', 'rb').read()); fc._ka_slot = 'q'; fc.load('q')
P0 = 16870
fc.step(S[1:P0 - 14848 + 1], record='last'); fc.save('p'); fc.save_file('p', 'states/mesen/l42p_c3b16870.mst', frame=P0)
print('rows 16860-16870', S[16860 - 14848:16871 - 14848])
def X(r): return r['x'] + (r['scroll'] if 'scroll' in r else 0)
base = [S[f - 14848] for f in range(P0 + 1, 17021)]
for k in [0, 1, 2, 3, 5, 10, 30, 60, 100, 150]:
    rows = list(base)
    for j in range(k): rows[-1 - j] = ('Right',)
    rows += [('Right',)] * 60
    res = fc.run_batch('p', [rows], record='all', record_ram=True)[0]
    st = res.states if hasattr(res, 'states') else res[2]
    out = []
    for s in st:
        f = s['frame'] if s.get('frame') else None
    xs = [(P0 + 1 + i, s['x'], s['xsub'], s['y'], s['stage'], s['room']) for i, s in enumerate(st)]
    sel = [t for t in xs if t[0] in (17015, 17018, 17019, 17020, 17021, 17022, 17030, 17060, 17080)]
    print('Right on last', k, 'rows before/at 17,020:', sel, flush=True)
fc.close()
