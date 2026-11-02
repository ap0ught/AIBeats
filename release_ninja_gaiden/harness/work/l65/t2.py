import sys
sys.path.insert(0, 'work/l65')
sys.argv = ['x']
exec(open('work/l65/jplan65.py').read().split("prefix = rows_of")[0])
from lib65 import *
fc = core65(243)
r1 = step_rows(28, 'R', '-', 0, 'all')[:72]
L = K.Legal(HIST)
for r in r1:
    w_ = L.why(r)
    if w_: print('illegal1', w_)
    L.push(r)
fc.step(r1); fc.save('s1')
for w in [0, 1, 2, 3, 4, 6]:
    for o in range(5):
        for d in ['-', 'R', 'L']:
            r2 = step_rows(w, '-', d, o, 'all')
            L2 = L.copy(); bad = ''
            for i, r in enumerate(r2):
                x = L2.why(r)
                if x: bad = f'{i}:{x}'; break
                L2.push(r)
            st = fc.run_batch('s1', [r2], record='all')[0].states
            hits = [72 + i + 1 for i in range(1, len(st)) if st[i]['eh6'] != st[i-1]['eh6']]
            pk = next((72 + i + 1 for i, s in enumerate(st) if pod_dead(s)), None)
            print(w, o, d, 'illegal' if bad else 'ok', bad, 'pod', st[-1]['eh6'], 'hits', hits, 'dead', pk, 'hp', st[-1]['hp65'], 'y', st[-1]['y8a'])
fc.close()
