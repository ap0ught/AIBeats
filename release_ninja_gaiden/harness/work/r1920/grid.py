"""Grid over row specs with {a,b,..} alternatives: python work/r1920/grid.py <mst> <f0> "<cond>" "<template with {i:lo:hi}>"
Placeholders {name:lo:hi} expand to integer ranges used as repeat counts. Prints the best (earliest cond, then max X)."""
import sys, re, itertools
sys.path.insert(0, '.'); sys.path.insert(0, 'work/l31t'); sys.path.insert(0, 'work/r1920')
import fcka
from ng import fastcore as F
from gbeam import FL, X, row, Leg
mst, f0, cond, tpl = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
H = [()] * 30
cf = eval('lambda s, X: ' + cond)
ph = re.findall(r'\{(\w+):(\d+):(\d+)\}', tpl)
def spec(sp):
    out = []
    for tok in sp.split():
        k, n = tok.split(':') if ':' in tok else (tok, '1')
        out += [row(k)] * int(n)
    return out
cands = []
for vals in itertools.product(*[range(int(lo), int(hi) + 1) for _, lo, hi in ph]):
    sp = tpl
    for (nm, lo, hi), v in zip(ph, vals):
        sp = sp.replace('{%s:%s:%s}' % (nm, lo, hi), str(v))
    sp = re.sub(r'\S+:0(\s|$)', ' ', sp)
    rows = spec(sp)
    L = Leg(H); ok = all(tuple(sorted(L.emit(r))) == tuple(sorted(r)) for r in rows)
    if ok: cands.append((vals, rows))
print(len(cands), 'legal', flush=True)
fc = F.FastCore(boot_rows=None, ticks=True, fields=FL)
fc.put('s', open(mst, 'rb').read()); fc._ka_slot = 's'
res = []
for i in range(0, len(cands), 40):
    rr = fc.run_batch('s', [c[1] for c in cands[i:i + 40]], record='all')
    for (vals, rows), r in zip(cands[i:i + 40], rr):
        h = next((q for q, s in enumerate(r.states) if cf(s, X(s))), None)
        if h is None: continue
        s = r.states[h]
        res.append((f0 + h + 1, -X(s), vals, s['hp']))
res.sort()
for z in res[:8]: print(z)
fc.close()
