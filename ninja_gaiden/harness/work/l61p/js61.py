"""6-1 thrower fix with the 6-1 J&S (X 528 y 128): pre61 rows + B+Left at s (slash the lantern) + B+Left at p (spin at the thrower).
From TAS state 30062 with $BF poked so that c ($BF on the 6-1 control row) = each value in --cs; play to F1 (default 31487).
Reports item/np, hits, first position difference vs the TAS.
python work/l61p/js61.py --s 31015,31017 --p 31040 --cs 84,73,75 [--f1 31487] [--rows file]"""
import sys
sys.path.insert(0, 'work/l61p')
from lib import *
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return type(d)(v)
    return d
SS = [int(x) for x in opt('--s', '31019').split(',')]; PP = [int(x) for x in opt('--p', '0').split(',')]
CS = opt('--cs', '84'); F1 = opt('--f1', 31487); RF = opt('--rows', 'work/l61p/pre61_32595.txt')
if '-' in CS and ',' not in CS: lo, hi = map(int, CS.split('-')); CS = list(range(lo, hi + 1))
else: CS = [int(x) for x in CS.split(',')]
base = [row(l.strip()) for l in open(RF) if l.strip() and not l.startswith('#')]
fc = core(tas_mst(30062)); fc.save('b'); fc._ka_slot = 'b'
for c in CS:
    fc.load('b'); fc.poke(0xBF, (c - 1) % 256); fc.save(f'c{c}')
for s in SS:
    for p in PP:
        r = list(base)
        for f in (s, s + 1): r[f - 30063] = ('B', 'Left')
        if p:
            for f in (p, p + 1): r[f - 30063] = ('B', 'Left')
        rows = r[:F1 - 30062]
        lg = legal_ok(rows)
        res = []
        for c in CS:
            st = fc.run_batch(f'c{c}', [rows], record='all')[0].states
            hits = [30063 + i for i in range(1, len(st)) if st[i]['hp65'] < st[i-1]['hp65']]
            d = next((30063 + i for i, q in enumerate(st) if RXY(q) != tas_xy(30063 + i) and not 30684 <= 30063 + i <= 30733), None)
            jsf = next((30063 + i for i, q in enumerate(st) if q['item'] == 133), None)
            npl = [(30063 + i, st[i]['np64']) for i in range(1, len(st)) if st[i]['np64'] != st[i-1]['np64']]
            res.append((c, hits[:3], d, st[-1]['hp65'], st[-1]['np64'], st[-1]['item'], RXY(st[-1])))
            print(f's {s} p {p} c {c}: J&S {jsf} hits {hits[:3]} first-diff {d} end hp {st[-1]["hp65"]} np {st[-1]["np64"]} it {st[-1]["item"]} X,y {RXY(st[-1])} np-changes {npl[:8]} {lg}', flush=True)
        ok = [x[0] for x in res if not x[1] and x[6] == (23, 144)]
        print(f'== s {s} p {p}: clean {len(ok)}/{len(CS)}', flush=True)
fc.close()
