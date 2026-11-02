"""Round 2 sweep: from p4t[:K] dodge the crawling shot (stand/jump in place), run right, last wheel at T (opt. jump J first)."""
import sys, itertools, json
sys.path.insert(0, 'work/l33')
from sw import Ctx, C, spec
p4 = [tuple(sorted(r)) for r in C.rows_of('work/l33/p4t.txt')]
X = Ctx('cB')
allr = []
for K in (112, 116, 120, 124):
    wants, meta = [], []
    for wait in range(0, 31, 3):
        for wtype in ('stand', 'jump', 'left'):
            if wait == 0 and wtype != 'stand': continue
            if wtype == 'stand': w0 = [()] * wait
            elif wtype == 'left': w0 = [('Left',)] * wait
            else: w0 = [('A',), ('A',)] + [()] * max(0, wait - 2)
            for T in range(140, 166, 2):
                for jmp in (None, 4, 8):
                    w = list(w0)
                    n_to_T = T - K - len(w)
                    if n_to_T < 3: continue
                    run = [('Right',)] * n_to_T
                    if jmp and n_to_T > jmp + 2:
                        j = n_to_T - jmp
                        run[j] = ('A', 'Right'); run[j + 1] = ('A', 'Right')
                    w += run
                    w += spec('Up+B*2') + [()] * 45
                    wants.append(w); meta.append((K, wtype, wait, T, jmp))
    res = X.run_from(p4[:K], wants)
    for r, m in zip(res, meta):
        allr.append((r['M'] or 9999, r['kill'] or 0, str(m), r['np'], r['boss'], r['rhit'][:3]))
    print(K, len(wants), sorted(allr)[:3], flush=True)
X.close()
allr.sort()
for q in allr[:20]: print(q)
json.dump(allr[:200], open('logs/l33/r2a.json', 'w'))
