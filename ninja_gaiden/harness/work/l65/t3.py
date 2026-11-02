import sys, os
sys.path.insert(0, 'work/l65')
sys.argv = ['x']
exec(open('work/l65/jplan65.py').read().split("prefix = rows_of")[0])
fc = core65(243)
best = []
for s1 in [(24, 'R', 'R', 0, 'nob'), (24, 'R', 'R', 2, 'nob'), (24, 'R', 'R', 4, 'nob'), (28, 'R', '-', 0, 'all')]:
    for n1 in range(66, 76):
        r1 = step_rows(*s1)[:n1]
        for s2 in [(0, '-', d, o, dm) for d in '-LR' for o in range(5) for dm in ('all', 'nob') if not (dm == 'nob' and d == '-')] + [(1, '-', '-', o, 'all') for o in range(5)]:
            rows = r1 + step_rows(*s2)[:60]
            L = K.Legal(HIST); bad = False
            for r in rows:
                if L.why(r): bad = True; break
                L.push(r)
            if bad: continue
            fc.load('c0'); fc.save('x')
            st = fc.run_batch('x', [rows], record='all')[0].states
            pk = next((i + 1 for i, s in enumerate(st) if pod_dead(s)), None)
            hp = st[-1]['hp65']
            if pk: best.append((pk, -hp, s1, n1, s2))
best.sort()
for b in best[:10]: print(b)
fc.close()
