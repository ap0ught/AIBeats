"""Bird phase test: arrival rows + climb rows (+ shift) + legal TAS rows at lag LG; prints Ryu X and wall-bird X every 20 f."""
import sys; sys.path.insert(0, 'work/l51a')
from rep import *
arr = rows_file(sys.argv[1]); cl = rows_file(sys.argv[2]); LG = int(sys.argv[3]); END = int(sys.argv[4]); drop = len(sys.argv) > 5
pre = arr + cl
R = Rep(pre, len(pre), LG, END, {23355: {'Right'}, 23356: {'Right'}} if drop else {})
rows = pre + R.rows({})
fc, _k = start_core(rows); _, recs, _ = fc.step(rows[_k:], record='all'); fc.close()
recs = [None] * _k + list(recs)
hp = None
for i, s in enumerate(recs):
    f = CTL + i
    if s is None or f < CTL + len(arr) - 5: continue
    X, y = RXY(s); scr = X - s['x86']
    birds = [(scr + s[f'ex{j}'], s[f'ey{j}']) for j in range(8) if s['eact'] >> j & 1 and s[f't{j}'] == 11]
    if (f - CTL) % 15 == 0 or s['hp65'] != hp:
        print(f, 'tas', f - LG, 'X,y', X, y, 'hp', s['hp65'], 'np', s['np64'], 'birds', birds, flush=True)
    hp = s['hp65']
    if y >= 240: break
