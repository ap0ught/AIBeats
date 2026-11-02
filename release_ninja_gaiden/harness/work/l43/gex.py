"""Exit-ladder grid: rows[:N] + R*k + A+R*2 + R*m + ladder cycle (rotation r) x14; first frame in room <room>.
python work/l43/gex.py <rows> N <room> [kmin kmax]"""
import sys, json; sys.path.insert(0, 'work/l43')
from lib import *
rows = rows_file(sys.argv[1]); N = int(sys.argv[2]); RM = int(sys.argv[3])
k0, k1 = (int(sys.argv[4]), int(sys.argv[5])) if len(sys.argv) > 5 else (0, 30)
pre = rows[:N]
fc = core(); fc.step(pre, record='last'); fc.save('b'); fc._ka_slot = 'b'
CYC = [('Right',), ('Right', 'Up'), ('Right', 'Up'), ('A', 'Left', 'Up'), ('A', 'Left')]
cands = []; meta = []
for k in range(k0, k1 + 1):
    for m in range(8, 40, 2):
        for r in range(6):
            cyc = (CYC[r:] + CYC[:r]) if r < 5 else [('Right', 'Up')]
            want = [('Right',)] * k + [('A', 'Right')] * 2 + [('Right',)] * m + cyc * (14 if r < 5 else 70)
            en = enforcer(pre)
            cands.append([tuple(sorted(en.emit(w))) for w in want][:130]); meta.append((k, m, r))
print(len(cands), 'cands', flush=True)
res = []
for i in range(0, len(cands), 80):
    for mt, r in zip(meta[i:i + 80], fc.run_batch('b', cands[i:i + 80], record='all')):
        g = next((CTL + N + q for q, s in enumerate(r.states) if s['room'] == RM), 99999)
        res.append((g, mt, r.states[-1]['hp']))
res.sort()
for q in res[:12]: print(q)
json.dump(res[:30], open(f'work/l43/gex_{RM}.json', 'w'))
fc.close()
