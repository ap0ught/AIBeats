"""6-4a J&S + 5 (Mesen, TAS 37277 poked $C9=133 $64=5 $C8=0). Floor jump A 37279 / A+Right 37280 onto the left pedestal,
pedestal jump A+Right x2 at t2, spin B+Right x2 at t3, Right held to r, then POST until the end (n rows). Stop at $66 == 0.
Reports kills, else the lowest boss HP. python work/l63p/mdjs2.py [--t2 37301,37302] [--n 75]"""
import sys
sys.path.insert(0, 'work/l63p')
from lib import *
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return type(d)(v)
    return d
T2 = [int(x) for x in opt('--t2', '37301,37302').split(',')]; N = opt('--n', 75); TOP = opt('--top', 25)
D3 = opt('--d3', '2-14'); DR = opt('--dr', '2-26'); STEP = opt('--step', 2)
def rng(s): x, y = map(int, s.split('-')); return range(x, y + 1)
F0 = 37277
fc = core_at(F0)
for k, v in ((0xC9, 133), (0x64, 5), (0xC8, 0)): fc.poke(k, v)
fc.save('b'); fc._ka_slot = 'b'
hist = [tuple(sorted(set(T(f)) - {'Up', 'Down'} - ({'Left'} if {'Left','Right'} <= set(T(f)) else set()))) for f in range(F0 - 150, F0 + 1)]
CYC = [('Down',), ('B', 'Down'), ('B',), (), ()]
cands = {}
for lead in ('-', 'A'):
  for t2 in T2:
    for d3 in rng(D3):
        t3 = t2 + d3
        for dr in range(int(DR.split('-')[0]), int(DR.split('-')[1]) + 1, STEP):
            r = t3 + dr
            for post in ('-', 'Left', 'cyc', 'Rcyc'):
                rows = []
                for f in range(F0 + 1, F0 + 1 + N):
                    if lead == '-' and f == 37278: x = ()
                    elif lead == '-' and f == 37279: x = ('A',)
                    elif lead == '-' and f == 37280: x = ('A', 'Right')
                    elif lead == 'A' and f == 37278: x = ('A',)
                    elif lead == 'A' and f == 37279: x = ('A', 'Right')
                    elif f in (t2, t2 + 1): x = ('A', 'Right')
                    elif f in (t3, t3 + 1): x = ('B', 'Right')
                    elif f < r: x = ('Right',)
                    elif post == '-': x = ()
                    elif post == 'Left': x = ('Left',)
                    elif post == 'cyc': x = CYC[(f - r) % 5]
                    else: x = tuple(sorted(set(CYC[(f - r) % 5]) | ({'Right'} if (f - r) % 5 >= 2 else set())))
                    rows.append(x)
                if legal_ok(rows, hist): continue
                cands[(lead, t2, t3, r, post)] = rows
print('cands', len(cands), flush=True)
names = list(cands); res = []
for i in range(0, len(names), 64):
    rs = fc.run_batch('b', [cands[n] for n in names[i:i+64]], record='all', stops=[(0x66, '==', 0)])
    for n, rr_ in zip(names[i:i+64], rs):
        s = rr_.states[-1]
        mb = min(x['bosshp'] for x in rr_.states)
        res.append((0 if rr_.status == 1 else 1, mb, F0 + rr_.rows_played, s['hp65'], n))
res.sort()
for x in res[:TOP]: print(x, flush=True)
print('kills', sum(1 for x in res if x[0] == 0), 'of', len(res))
fc.close()
