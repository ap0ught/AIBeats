import sys
sys.path.insert(0, 'work/l63p')
from lib import *
F0 = 38932; v = int(sys.argv[1]); RF = sys.argv[2] if len(sys.argv) > 2 else 'work/l63p/dm_r2d5_kill.txt'
rows = [row(l.strip()) for l in open(RF) if not l.startswith('#')]
fc = core_at(F0); fc.poke(0xBF, v)
_, st, _ = fc.step(rows, record='all')
fc.close()
prev = None
for i, s in enumerate(st):
    f = F0 + 1 + i
    ev = []
    if prev and s['hp65'] != prev['hp65']: ev.append(f"hp {prev['hp65']}->{s['hp65']}")
    if prev and s['bosshp'] != prev['bosshp']: ev.append(f"boss {s['bosshp']}")
    if ev or f % 20 == 0:
        print(f, P(rows[i]), RXY(s), ' '.join(ev), [(s[f't{j}'], s[f'ex{j}'], s[f'ey{j}']) for j in range(4, 8)])
    prev = s
