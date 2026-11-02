"""emulator test: base rows (c1 to 24,200 + legal TAS rows from 23,671) with blank waits inserted.
python work/l51c/etest.py "s:w,s2:w2" tend [step] [tasfrom]   (s = our frame on the base axis; the row s gets the blanks before it)"""
import sys; sys.path.insert(0, 'work/l51c')
from lc import *
F0 = 23663; MST = 'states/mesen/l51c_c1_23663.mst'
spec = [tuple(map(int, x.split(':'))) for x in sys.argv[1].split(',') if x]
tend = int(sys.argv[2]); st = int(sys.argv[3]) if len(sys.argv) > 3 else 4
rows = c1rows(); hist = rows[:F0]
base = [set(r) for r in rows[F0:24200]] + tasleg(23671, 24150)
want = list(base); W = 0
for s, w in sorted(spec, reverse=True):
    k = s - F0 - 1; want = want[:k] + [set()] * w + want[k:]; W += w
cand = enforce(want, hist)
n = tend + 530 + W - F0
fc = core(MST)
r = fc.run_batch('s', [cand[:n]], record='all')[0]
hp = 12
for i, s in enumerate(r.states):
    f = F0 + 1 + i; X, y = RXY(s)
    ev = ''
    if s['hp65'] != hp: ev = f'  <<< HIT hp {hp}->{s["hp65"]}'; hp = s['hp65']
    if (i % st == 0 and f - 530 - W >= tend - 400) or ev: print(line(f, s), '|', P(cand[i]), ev)
fc.close()
open('work/l51c/etest_last.txt', 'w').write('\n'.join(P(x) for x in cand[:n]) + '\n')
