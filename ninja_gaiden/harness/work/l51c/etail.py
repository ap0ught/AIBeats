"""base rows with waits up to our frame cut (new axis), then c1 rows from cut+shift. Print events.
python work/l51c/etail.py "s:w,..." cut shift tend [step]"""
import sys; sys.path.insert(0, 'work/l51c')
from lc import *
F0 = 23663; MST = 'states/mesen/l51c_c1_23663.mst'
spec = [tuple(map(int, x.split(':'))) for x in sys.argv[1].split(',') if x]
cut, shift, tend = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]); st = int(sys.argv[5]) if len(sys.argv) > 5 else 4
rows = c1rows(); hist = rows[:F0]
base = [set(r) for r in rows[F0:24200]] + tasleg(23671, 24150)
want = list(base)
for s, w in sorted(spec, reverse=True):
    k = s - F0 - 1; want = want[:k] + [set()] * w + want[k:]
want = want[:cut - F0] + [set(r) for r in rows[cut + shift:]]
cand = enforce(want, hist)
print('legal:', legal_ok(cand, hist) or 'ok')
fc = core(MST)
r = fc.run_batch('s', [cand[:tend - F0]], record='all')[0]
hp = 12
for i, s in enumerate(r.states):
    f = F0 + 1 + i; X, y = RXY(s); ev = ''
    if s['hp65'] != hp: ev = f'  <<< HIT hp {hp}->{s["hp65"]}'; hp = s['hp65']
    if (f >= cut - 10 and i % st == 0) or ev or s['e5c'] == 0: print(line(f, s), '|', P(cand[i]), ev)
    if s['e5c'] == 0: print('TRIGGER', f); break
fc.close()
open('work/l51c/etail_last.txt', 'w').write('\n'.join(P(x) for x in cand) + '\n')
