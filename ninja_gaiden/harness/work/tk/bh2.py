"""2-3 Bomberhead sword-only (tk): wait/approach, then repeat [slash cycle x m, Right x r, Left x 2] (back off as he
walks in). Prints kill row, Ryu hp. Writes the best rows to states/tmp/tk_bh2_best.inputs.txt.
    python work/tk/bh2.py <state> <hist>"""
import sys, itertools
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ng.solve import common as C, legality as L
from ng.mode import TICKS
import a56_common as A
st, hf = sys.argv[1], sys.argv[2]; hist = C.rows_of(hf)
SL = {'crouch': [('Down',), ('Down', 'B'), ('B',), (), ()], 'stand': [('B',), ('B',), (), (), ()]}
e = C.open_emu('tk_bh2.log'); best = None
try:
    e.tick(TICKS); e.load(st); sid = e.msave()
    for pre, m, r, cyc, lb in itertools.product((0, 20, 40, 60), (1, 2, 3, 4), (3, 5, 7, 9), SL, (2, 3)):
        want = [('Left',)] * pre + (SL[cyc] * m + [('Right',)] * r + [('Left',)] * lb) * 40
        en = L.Enforcer(hist[-1900:]); rows = [en.emit(x) for x in want[:700]]
        e.mload(sid); tr = A.play_trace(e, rows)
        k = next((i for i, s in enumerate(tr) if s['bosshp'] == 0), None)
        lim = k + 1 if k is not None else len(tr)
        hp = min(s['hp'] for s in tr[:lim]); mb = min(s['bosshp'] for s in tr[:lim])
        dead = any(s['hp'] == 0 for s in tr[:lim])
        print(pre, m, r, cyc, lb, 'kill', k, 'minboss', mb, 'hp', hp, 'dead' if dead else '', flush=True)
        if k is not None and not dead and (best is None or k < best[0]):
            best = (k, pre, m, r, cyc, lb)
            C.write_inputs('states/tmp/tk_bh2_best.inputs.txt', rows[:k + 1], f'bh2 kill row {k} {best[1:]}')
finally:
    e.close()
print('BEST', best)
