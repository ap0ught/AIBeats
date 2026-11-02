"""Round 2 sweep b: from p4t[:K]: d1 (stand/Right) a rows, jump A+d2 (d2 none/Left/Right) held to landing, run Right,
last wheel at T (optionally after a jump 6 rows before). Report M."""
import sys, json
sys.path.insert(0, 'work/l33')
from sw import Ctx, C, spec
p4 = [tuple(sorted(r)) for r in C.rows_of('work/l33/p4t.txt')]
X = Ctx('cB')
allr = []
for K in (100, 106, 112, 118, 124):
    wants, meta = [], []
    for d1 in (None, 'Right'):
        for a_ in range(0, 31, 3):
            for d2 in (None, 'Left', 'Right'):
                w0 = [((d1,) if d1 else ())] * a_
                dd = (d2,) if d2 else ()
                w0 += [tuple(sorted(('A',) + dd))] * 2 + [dd] * 42
                for T in range(138, 176, 3):
                    for jmp in (0, 6):
                        n = T - K - len(w0)
                        if n < 0:
                            # throw inside the jump window: truncate
                            w = w0[:T - K] if T - K > 2 else None
                            if w is None or jmp: continue
                            w = [x if 'A' in x else () for x in w[:T - K]] if False else list(w)
                            w = w[:T - K]
                        else:
                            w = list(w0) + [('Right',)] * n
                            if jmp and n > jmp + 2:
                                w[-jmp] = ('A', 'Right'); w[-jmp + 1] = ('A', 'Right')
                        w += spec('Up+B*2') + [()] * 40
                        wants.append(w); meta.append((K, d1, a_, d2, T, jmp))
    res = X.run_from(p4[:K], wants)
    for r, m in zip(res, meta):
        allr.append((r['M'] or 9999, r['kill'] or 0, str(m), r['np'], r['boss'], r['rhit'][:3]))
    allr.sort()
    print(K, len(wants), allr[:3], flush=True)
X.close()
for q in allr[:25]: print(q)
json.dump(allr[:300], open('logs/l33/r2b.json', 'w'))
