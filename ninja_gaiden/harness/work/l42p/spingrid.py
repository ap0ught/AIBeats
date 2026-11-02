"""Chain (c 81): thrower-3 spin frame grid. Rows = s42_to18180 with the spin (B 2 f) moved to TAS frame k (17,500-17,523),
then legal TAS rows (L+R -> Right) to 18,560. Report: hits, first divergence from the TAS, enemy types at 18,170 vs TAS."""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'work/l31t')
import fcka
from ng import fastcore as F
from ng.solve import common as C
S = [tuple(r) for r in C.rows_of('work/l42p/s42_to18180.inputs.txt')]
L = [tuple(r) for r in C.rows_of('work/l42p/lt18700.inputs.txt')]
d = open('work/l42p/tas42_ram.bin', 'rb').read(); f0 = int.from_bytes(d[:4], 'little'); d = d[4:]
def tm(f): return d[(f - f0 - 1)*2048:(f - f0)*2048]
FL = {'x': 0x86, 'sl': 0x51, 'sh': 0x52, 'y': 0x8A, 'hp': 0x65, 'np': 0x64, 'en': 0x73}
for j in range(8): FL[f't{j}'] = 0x400 + j
fc = F.FastCore(boot_rows=None, ticks=True, fields=FL)
fc.put('s', open('states/mesen/l42p_lock16997.mst', 'rb').read()); fc._ka_slot = 's'; fc.load('s')
P0 = 17490
fc.step(S[:P0 - 16682 + 1], record='last'); fc.save('p'); fc._ka_slot = 'p'
END = 18560
base = list(S[P0 - 16682 + 1:])
for f in range(18181, END + 1):
    r = set(L[f - 16682]); r.discard('Left') if ('Left' in r and 'Right' in r) else None
    base.append(tuple(sorted(r)))
def at(f): return f - P0 - 1
tm18170 = sorted(tm(18170)[0x400 + j] for j in range(8) if tm(18170)[0x73] >> j & 1)
for k in [None] + list(range(17500, 17524)):
    rows = list(base)
    rows[at(17512)] = ('Right',); rows[at(17513)] = ('Right',)
    if k is not None: rows[at(k)] = ('B', 'Right'); rows[at(k + 1)] = ('B', 'Right')
    st = fc.run_batch('p', [rows], record='all')[0].states
    hits = []; hp = st[0]['hp']; div = None
    for i, s in enumerate(st):
        f = P0 + 1 + i; t = tm(f)
        X = s['sh']*256 + s['sl'] + s['x']; tX = t[0x52]*256 + t[0x51] + t[0x86]
        if div is None and abs(X - tX) > 3: div = (f, X, tX)
        if s['hp'] < hp: hits.append(f)
        hp = s['hp']
    s = st[18170 - P0 - 1]
    ours = sorted(s[f't{j}'] for j in range(8) if s['en'] >> j & 1)
    print('spin', k, 'hits', hits[:5], 'X>3px off at', div, 'enemies@18170', ours, 'TAS', tm18170, 'np', st[-1]['np'], flush=True)
fc.close()
