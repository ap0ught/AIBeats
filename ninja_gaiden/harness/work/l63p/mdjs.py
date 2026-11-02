"""6-4a Masked Devil with J&S + 5 (Mesen, TAS state 37277 poked: $C9=133, $64=5, $C8=0): grid over
floor jump t1, pedestal jump t2, spin t3 (B+Right x2), then a legal slash tail. Stop at $66 == 0.
python work/l63p/mdjs.py [--tail cyc|none] [--top 20]"""
import sys, itertools
sys.path.insert(0, 'work/l63p')
from lib import *
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return type(d)(v)
    return d
TAIL = opt('--tail', 'cyc'); TOP = opt('--top', 20); T1 = opt('--t1', '37283-37290'); T2 = opt('--t2', '14-26'); T3 = opt('--t3', '3-22')
SPIN = opt('--spin', 'B+Right'); PK = opt('--poke', '0xC9=133,0x64=5,0xC8=0'); F0 = opt('--f0', 37277); N = opt('--n', 160)
def rng(s): x, y = map(int, s.split('-')); return range(x, y + 1)
fc = core_at(F0)
for kv in PK.split(','):
    k, v = kv.split('='); fc.poke(int(k, 0), int(v, 0))
fc.save('b'); fc._ka_slot = 'b'
hist = [tuple(sorted(set(T(f)) - {'Up', 'Down'} - ({'Left'} if {'Left','Right'} <= set(T(f)) else set()))) for f in range(F0 - 150, F0 + 1)]
CYC = [('Down',), ('B', 'Down'), ('B', 'Right'), ('Right',), ('Right',)]
cands = {}
for t1 in rng(T1):
    for d2 in rng(T2):
        for d3 in rng(T3):
            t2 = t1 + d2; t3 = t2 + d3
            rows = []
            for f in range(F0 + 1, F0 + 1 + N):
                if f in (t1, t1 + 1, t2, t2 + 1): r = ('A', 'Right')
                elif f in (t3, t3 + 1): r = tuple(sorted(row(SPIN)))
                elif f >= t3 + 4 and TAIL == 'cyc': r = CYC[(f - t3 - 4) % 5]
                else: r = ('Right',)
                rows.append(r)
            if legal_ok(rows, hist): continue
            cands[(t1, t2, t3)] = rows
print('cands', len(cands), flush=True)
names = list(cands); res = []
for i in range(0, len(names), 64):
    rs = fc.run_batch('b', [cands[n] for n in names[i:i+64]], record='last', stops=[(0x66, '==', 0)])
    for n, r in zip(names[i:i+64], rs):
        s = r.states[-1]
        if r.status == 1: res.append((F0 + r.rows_played, s['hp65'], n))
res.sort()
for x in res[:TOP]: print(x, flush=True)
print('kills', len(res), 'of', len(cands))
fc.close()
