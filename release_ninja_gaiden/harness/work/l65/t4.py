import sys, os
sys.path.insert(0, 'work/l65')
sys.argv = ['x']
exec(open('work/l65/jplan65.py').read().split("prefix = rows_of")[0])
fc = core65(243)
res = []
s1 = (28, 'R', '-', 0, 'all')
for n1 in (71, 72, 73):
    r1 = step_rows(*s1)[:n1]
    for w2 in (0, 1):
        for o in range(5):
            base = step_rows(w2, '-', '-', o, 'all')[:62]
            for ts in (0, 10, 15, 20, 25, 30, 35, 40, 99):
                for mode in ('nob', 'all'):
                    r2 = []
                    for t, r in enumerate(base):
                        r = set(r)
                        if t >= w2 + ts and (mode == 'all' or not (r & {'Down', 'B'})): r.add('Right')
                        r2.append(tuple(sorted(r)))
                    rows = r1 + r2
                    L = K.Legal(HIST); bad = False
                    for r in rows:
                        if L.why(r): bad = True; break
                        L.push(r)
                    if bad: continue
                    fc.load('c0'); fc.save('x')
                    st = fc.run_batch('x', [rows], record='all')[0].states
                    pk = next((i + 1 for i, s in enumerate(st) if pod_dead(s)), None)
                    if pk: res.append((pk, st[pk - 1]['x86'], st[-1]['hp65'], n1, w2, o, ts, mode, st[-1]['x86'], st[-1]['y8a'], len(st)))
res.sort()
for r in res[:40]: print(r)
fc.close()
