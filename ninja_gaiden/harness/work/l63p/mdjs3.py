"""6-4a J&S + 5 (Mesen, TAS 37277 poked): lead A 37278 / A+Right 37279, pedestal jump A+Right x2 at t2, legal slash cycles
(Down | Down+B | B+Right | Right | Right) from s0 for c cycles, spin B+Right x2 at t3, then POST. Stop at $66 == 0."""
import sys
sys.path.insert(0, 'work/l63p')
from lib import *
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return type(d)(v)
    return d
N = opt('--n', 80); TOP = opt('--top', 25); T2 = [int(x) for x in opt('--t2', '37301').split(',')]
F0 = 37277
fc = core_at(F0)
for k, v in ((0xC9, 133), (0x64, 5), (0xC8, 0)): fc.poke(k, v)
fc.save('b'); fc._ka_slot = 'b'
hist = [()] * 150
cands = {}
for t2 in T2:
  for s0 in range(t2 + 4, t2 + 20):
    for c in range(1, 5):
        for g in range(2, 7):
            t3 = s0 + 5 * c + g - 2
            for post in ('-', 'Right'):
                for cr in ('-', 'Right'):
                    rows = []
                    for f in range(F0 + 1, F0 + 1 + N):
                        if f == 37278: x = ('A',)
                        elif f == 37279: x = ('A', 'Right')
                        elif f in (t2, t2 + 1): x = ('A', 'Right')
                        elif s0 <= f < s0 + 5 * c:
                            k = (f - s0) % 5
                            x = [('Down',), ('B', 'Down'), ('B',) if cr == '-' else ('B', 'Right'), () if cr == '-' else ('Right',), () if cr == '-' else ('Right',)][k]
                        elif f in (t3, t3 + 1): x = ('B', 'Right')
                        elif f < t3: x = ('Right',) if cr == 'Right' or f < s0 else ()
                        else: x = () if post == '-' else (post,)
                        rows.append(tuple(sorted(x)))
                    if legal_ok(rows, hist): continue
                    cands[(t2, s0, c, t3, post, cr)] = rows
print('cands', len(cands), flush=True)
names = list(cands); res = []
for i in range(0, len(names), 64):
    rs = fc.run_batch('b', [cands[n] for n in names[i:i+64]], record='all', stops=[(0x66, '==', 0)])
    for n, rr_ in zip(names[i:i+64], rs):
        s = rr_.states[-1]
        mb = min(x['bosshp'] for x in rr_.states)
        res.append((0 if rr_.status == 1 else 1, mb, F0 + rr_.rows_played, min(x['hp65'] for x in rr_.states), n))
res.sort()
for x in res[:TOP]: print(x, flush=True)
print('kills', sum(1 for x in res if x[0] == 0), 'of', len(res))
fc.close()
