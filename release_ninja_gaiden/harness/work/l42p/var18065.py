"""Chain (c 81) variants of the TAS's 18,065-18,108 section (1-frame Left, L+R jump). Mesen from l42p_lock16997 + sync rows.
TAS axis frames; chain = TAS + 316. Prints for each variant: first divergence from the TAS, hits, X at TAS 18,300 / 18,500."""
import sys, itertools
sys.path.insert(0, '.'); sys.path.insert(0, 'work/l31t')
import fcka
from ng import fastcore as F
from ng.solve import common as C
from ng.solve.legality import check
OFF = 316
S = [tuple(r) for r in C.rows_of('work/l42p/s42_sync81.inputs.txt')]       # rows for TAS 16,682..18,064
L = [tuple(r) for r in C.rows_of('work/l42p/lt18700.inputs.txt')]          # legalized TAS rows (U+D dropped, A/B 2 f) 16,682..
d = open('work/l42p/tas42_ram.bin', 'rb').read(); f0 = int.from_bytes(d[:4], 'little'); d = d[4:]
def tm(f): i = f - f0 - 1; return d[i*2048:(i+1)*2048]
def tXY(f): m = tm(f); return (m[0x52]*256 + m[0x51] + m[0x86], m[0x8A])
FL = {'x': 0x86, 'sl': 0x51, 'sh': 0x52, 'y': 0x8A, 'hp': 0x65, 'np': 0x64, 'it': 0xC9}
fc = F.FastCore(boot_rows=None, ticks=True, fields=FL)
fc.put('s', open('states/mesen/l42p_lock16997.mst', 'rb').read()); fc._ka_slot = 's'; fc.load('s')
P0 = 18050
fc.step(S[:P0 - 16682 + 1], record='last'); fc.save('p'); fc._ka_slot = 'p'
END = 18560
def tail(f1):   # legal TAS rows from f1 on, L+R -> Right
    out = []
    for f in range(f1, END + 1):
        r = set(L[f - 16682])
        if 'Left' in r and 'Right' in r: r.discard('Left')
        out.append(tuple(sorted(r)))
    return out
def var(name, mid, f1):
    rows = list(S[P0 - 16682 + 1:18064 - 16682 + 1])   # 18,051..18,064
    rows = rows[:18064 - P0 - len(mid) + 0] if False else rows
    return name, rows, mid, f1
cands = []
R = ('Right',); RA = ('A', 'Right'); LL = ('Left',); N = ()
base = list(S[P0 - 16682 + 1:18064 - 16682 + 1])  # frames 18,051..18,064
def mk(pre_override, mid, f1):
    rows = list(base)
    for f, r in pre_override.items(): rows[f - P0 - 1] = r
    return rows + mid + tail(f1)
cands.append(('drop Left (Right), A 18066-67', mk({}, [R, RA, RA], 18068)))
cands.append(('Left 18064-65, A 18066-67', mk({18064: LL}, [LL, RA, RA], 18068)))
cands.append(('Left 18065-66, A 18067-68', mk({}, [LL, LL, RA, RA], 18069)))
cands.append(('blank 18064-65, A 18066-67', mk({18064: N}, [N, RA, RA], 18068)))
cands.append(('blank 18065-66, A 18067-68', mk({}, [N, N, RA, RA], 18069)))
cands.append(('Right, A 18065-66', mk({}, [RA, RA], 18067)))
cands.append(('Right, A 18067-68', mk({}, [R, R, RA, RA], 18069)))
for name, rows in cands:
    full = S[:P0 - 16682 + 1] + rows
    lg = check(full, [()] * 300)['pass']
    st = fc.run_batch('p', [rows], record='all')[0].states
    div = None; hits = []; hp = st[0]['hp']; xs = {}
    for i, s in enumerate(st):
        f = P0 + 1 + i
        X = s['sh']*256 + s['sl'] + s['x']
        if div is None and (X, s['y']) != tXY(f): div = (f, X, s['y'], tXY(f))
        if s['hp'] < hp: hits.append(f)
        hp = s['hp']
        if f in (18200, 18300, 18400, 18500, 18560): xs[f] = (X - tXY(f)[0])
    print(f'{name:32s} legal {lg} div {div} hits {hits[:6]} X-TAS {xs} item {st[-1]["it"]}', flush=True)
fc.close()
