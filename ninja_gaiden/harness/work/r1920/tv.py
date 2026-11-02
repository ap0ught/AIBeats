"""Try row specs from a Mesen state; print a compact trace + the first frame meeting a condition.
python work/r1920/tv.py <mst> <f0> "<cond expr on s, X>" "<spec>" ... [--trace]"""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'work/l31t'); sys.path.insert(0, 'work/r1920')
import fcka
from ng import fastcore as F
from gbeam import FL, X, row
a = sys.argv[1:]; tr = '--trace' in a; a = [x for x in a if x != '--trace']
def spec(sp):
    out = []
    for tok in sp.split():
        k, n = tok.split(':') if ':' in tok else (tok, '1')
        out += [row(k)] * int(n)
    return out
fc = F.FastCore(boot_rows=None, ticks=True, fields=FL)
fc.put('s', open(a[0], 'rb').read()); fc._ka_slot = 's'
f0 = int(a[1]); cond = eval('lambda s, X: ' + a[2])
for sp in a[3:]:
    rows = spec(sp)
    r = fc.run_batch('s', [rows], record='all')[0]
    hit = next((i for i, s in enumerate(r.states) if cond(s, X(s))), None)
    s = r.states[-1]
    print(f'{sp!r}: cond at', None if hit is None else f0 + hit + 1, '| end X', X(s), 'y', s['y'], 'hp', s['hp'], 'np', s['np'])
    if tr:
        for i, (s, w) in enumerate(zip(r.states, rows)):
            print('  ', f0 + i + 1, '+'.join(w) or '-', 'X', X(s), 'y', s['y'], 'vy', s['vy'], 'an', s['anim'], 'co', s['coll'], 'rf', hex(s['rf']), 'hp', s['hp'], 'np', s['np'])
fc.close()
