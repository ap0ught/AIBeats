"""generic Mesen grammar search with a python goal.
python -u work/l22p/xsearch.py <hist> <mst> <gramfile.py> <tag>
gramfile defines: cands() -> list of (label, want rows); goal(states, i) -> bool (state i reaches goal); ok(states,i)->bool
optional: H (rows per candidate). Prints top 15 by goal index; writes work/l22p/x_<tag>.txt (best rows to goal)."""
import sys, time, runpy
sys.path.insert(0,'.'); sys.path.insert(0,'work/w21')
from ng.solve import common as C, legality as L, fast as FS
from ng import fastcore as F
from wlib import fmt
hf, mst, gf, tag = sys.argv[1:5]
hist = C.rows_of(hf); G = runpy.run_path(gf)
base = L.Enforcer(hist[-1900:])
seen = {}; cands = []; labs = []
for lab, w in G['cands']():
    en = base.copy(); lg = tuple(tuple(sorted(en.emit(x))) for x in w)
    if lg in seen: continue
    seen[lg] = 1; cands.append(list(lg)); labs.append(lab)
print(f'{tag}: {len(cands)} unique candidates', flush=True)
P = F.FastPool(2, boot_rows=None, ticks=True)
d = open(mst, 'rb').read()
for wk in P.workers: wk.put('s', d); wk.load('s')
t0 = time.time()
L0 = max(len(c) for c in cands); ch = max(2, min(48, 2 * (500 // max(1, L0))))
res = FS.run_chunked(P, 's', cands, chunk=ch, record='all', stops=[(0x6D, 'changed', 0), (0x65, '==', 0)], log=lambda s: print(s, flush=True))
P.close()
out = []
for c, lb, r in zip(cands, labs, res):
    if r is None: continue
    st = r.states
    for i in range(len(st)):
        if G['goal'](st, i):
            if G.get('ok', lambda s, i: True)(st, i): out.append((i, -st[i]['hp'], -st[i]['ninpo'], lb, c))
            break
out.sort(key=lambda z: z[:3])
print(f'{len(out)} reach, {time.time()-t0:.0f}s')
for z in out[:15]: print(z[0] + 1, -z[1], -z[2], z[3], fmt(z[4][:z[0] + 1]))
if out:
    C.write_inputs(f'work/l22p/x_{tag}.txt', list(out[0][4][:out[0][0] + 1]), f'xsearch {tag} {out[0][3]}')
