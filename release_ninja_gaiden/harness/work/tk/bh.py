"""2-3 Bomberhead sword-only probe (tk): walk Left w frames, optional wait, then a 5-frame slash cycle; report kill.
    python work/tk/bh.py <state> <hist> [maxw]"""
import sys, itertools
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ng.solve import common as C, legality as L
from ng.mode import TICKS
import a56_common as A
st, hf = sys.argv[1], sys.argv[2]; maxw = int(sys.argv[3]) if len(sys.argv) > 3 else 60
hist = C.rows_of(hf)
CYC = {'crouch': [('Down',), ('Down', 'B'), ('B',), (), ()], 'stand': [('B',), ('B',), (), (), ()],
       'crouchL': [('Down',), ('Down', 'B'), ('B',), ('Left',), ('Left',)]}
e = C.open_emu('tk_bh.log'); best = None
try:
    e.tick(TICKS); e.load(st); sid = e.msave()
    for w, wait, cyc in itertools.product(range(0, maxw + 1, 4), (0, 10, 20, 30), CYC):
        want = [('Left',)] * w + [()] * wait + CYC[cyc] * 60
        en = L.Enforcer(hist[-1900:]); rows = [en.emit(x) for x in want]
        e.mload(sid); tr = A.play_trace(e, rows)
        k = next((i for i, s in enumerate(tr) if s['bosshp'] == 0), None)
        hp = min(s['hp'] for s in tr[:k + 1 if k is not None else len(tr)])
        mb = min(s['bosshp'] for s in tr)
        print(w, wait, cyc, 'kill', k, 'minboss', mb, 'hp', hp, flush=True)
        if k is not None and (best is None or k < best[0]):
            best = (k, w, wait, cyc); C.write_inputs('states/tmp/tk_bh_best.inputs.txt', rows[:k + 1], f'bh kill row {k} w {w} wait {wait} {cyc}')
finally:
    e.close()
print('BEST', best)
