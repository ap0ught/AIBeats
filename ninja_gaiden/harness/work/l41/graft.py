"""prefix rows (to frame P) + legalized TAS rows at lag d (our f = TAS f + TASOFF + d), Mesen check vs TAS trace.
python work/l41/graft.py <prefix rows> <P> <d> <end frame> [--out f] [--set "f=ROW,.."] [--show]"""
import sys
sys.path.insert(0, 'work/l41'); sys.path.insert(0, 'ng/stages')
from lib import *
import a56_common as A
TR = A.tas_rows(); TT = A.tas_trace()
def opt(a, n, dflt):
    if n in a:
        i = a.index(n); v = a[i + 1]; del a[i:i + 2]; return v
    return dflt
def compose(pf, P, d, E, sets=''):
    pre = list(C.rows_of(pf))[:P - F0]
    want = [tuple(TR[f - TASOFF - d - 1]) for f in range(P + 1, E + 1)]
    for q in sets.split(','):
        if q:
            k, v = q.split('='); want[int(k) - P - 1] = row(v)
    return pre + legal_after(pre, want)
if __name__ == '__main__':
    a = sys.argv[1:]
    out = opt(a, '--out', ''); sets = opt(a, '--set', ''); show = '--show' in a
    a = [q for q in a if q != '--show']
    pf, P, d, E = a[0], int(a[1]), int(a[2]), int(a[3])
    rows = compose(pf, P, d, E, sets)
    fc = core(); _, recs, _ = fc.step(rows, record='all'); fc.close()
    div = None; r14 = None
    for i, s in enumerate(recs):
        f = F0 + i + 1
        if f <= P: continue
        t = TT[f - TASOFF - d]
        if s['room'] == 14 and r14 is None: r14 = f
        if div is None and (C.abs_x(s), s['y'], s['room']) != (C.abs_x(t), t['y'], t['room']):
            div = (f, C.abs_x(s), s['y'], s['hp'], 'tas', C.abs_x(t), t['y'])
        if show and (f - P) % 4 == 0: print(f, '+'.join(rows[i]), C.abs_x(s), s['y'], s['hp'], '| tas', C.abs_x(t), t['y'], t['hp'])
    s = recs[-1]
    print('d', d, 'first div', div, 'room14', r14, 'end', C.abs_x(s), s['y'], s['room'], 'hp', s['hp'], 'np', s['ninpo'], 'item', s['item'])
    if out: C.write_inputs(out, rows, f'graft {pf}[:{P}] + TAS rows lag {d}')
