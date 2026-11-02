"""Test: with 5 ninpo poked at TAS 18,060 (chain 18,376), the legal TAS rows' B at 18,075-76 becomes a J&S spin.
Does the line then stay in TAS sync past 18,196? Also variants of the spin frame."""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'work/l31t')
import fcka
from ng import fastcore as F
from ng.solve import common as C
S = [tuple(r) for r in C.rows_of('work/l42p/s42_to18180.inputs.txt')]
L = [tuple(r) for r in C.rows_of('work/l42p/lt18700.inputs.txt')]
d = open('work/l42p/tas42_ram.bin', 'rb').read(); f0 = int.from_bytes(d[:4], 'little'); d = d[4:]
def tm(f): return d[(f - f0 - 1)*2048:(f - f0)*2048]
FL = {'x': 0x86, 'sl': 0x51, 'sh': 0x52, 'y': 0x8A, 'hp': 0x65, 'np': 0x64, 'it': 0xC9}
fc = F.FastCore(boot_rows=None, ticks=True, fields=FL)
fc.put('s', open('states/mesen/l42p_lock16997.mst', 'rb').read()); fc._ka_slot = 's'; fc.load('s')
P0 = 18060
fc.step(S[:P0 - 16682 + 1], record='last'); fc.poke(0x64, 5); fc.save('p'); fc._ka_slot = 'p'
END = 18640
base = list(S[P0 - 16682 + 1:])
for f in range(18181, END + 1):
    r = set(L[f - 16682]); r.discard('Left') if ('Left' in r and 'Right' in r) else None
    base.append(tuple(sorted(r)))
def at(f): return f - P0 - 1
for k in [18075, 18082]:
    rows = list(base)
    for f in (18075, 18076): rows[at(f)] = ('Right',)
    rows[at(k)] = ('B', 'Right'); rows[at(k + 1)] = ('B', 'Right')
    st = fc.run_batch('p', [rows], record='all')[0].states
    hits = []; hp = st[0]['hp']; div = None; xs = {}
    for i, s in enumerate(st):
        f = P0 + 1 + i; t = tm(f)
        X = s['sh']*256 + s['sl'] + s['x']; tX = t[0x52]*256 + t[0x51] + t[0x86]
        if div is None and abs(X - tX) > 3: div = (f, X, tX)
        if s['hp'] < hp: hits.append((f, s['hp']))
        hp = s['hp']
        if f in range(18072, 18100, 3): print('   ', f, 'X', X, 'y', s['y'], 'np', s['np'], 'hp', s['hp'], 'row', rows[i])
        if f in (18200, 18300, 18400, 18500, 18600, 18640): xs[f] = X - tX
    print('spin', k, 'hits', hits[:4], 'off>3px at', div, 'X-TAS', xs, 'np/item end', st[-1]['np'], st[-1]['it'], flush=True)
fc.close()
