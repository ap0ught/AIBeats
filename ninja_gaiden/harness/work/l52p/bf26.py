"""Room-26 thrower (type 2, spawns TAS 26,008 at (337,128); first throw $BF>>1 f after its spawn) vs $BF.
From the TAS state F0 (default 25,990) with $BF poked to v (all 256), play rows (TAS pad bytes, or --rows file from F0+1) to 26,340:
trigger frame ($5C 0 after 26,300), hp, first divergence vs the TAS, axe throw frames.  python work/l52p/bf26.py [F0] [--rows f]"""
import sys
sys.path.insert(0, 'work/l52p')
from lib import *
a = sys.argv[1:]
RF = ''
if '--rows' in a: i = a.index('--rows'); RF = a[i+1]; del a[i:i+2]
F0 = int(a[0]) if a else 25990; F1 = 26340
fc = core_at(F0); fc.save('b'); fc._ka_slot = 'b'
if RF: rows = [row(l.strip()) for l in open(RF) if l.strip() and not l.startswith('#')][:F1 - F0]
else: rows = [TM(g)[0x2A] for g in range(F0 + 1, F1 + 1)]
bf0 = TM(F0)[0xBF]
res = []
for v0 in range(0, 256, 32):
    vs = list(range(v0, v0 + 32))
    cands = []
    for v in vs:
        cands.append(rows)
    # poke per candidate: run_batch loads slot 'b' each time, so make one slot per v
    out = []
    for v in vs:
        fc.load('b'); fc.poke(0xBF, v); fc.save(f'p{v}')
    rr = [fc.run_batch(f'p{v}', [rows], record='all')[0] for v in vs]
    for v, r in zip(vs, rr):
        st = r.states; trig = None; div = None; throws = []
        for i, s in enumerate(st):
            f = F0 + 1 + i
            if trig is None and f > 26300 and s['e5c'] == 0: trig = f
            if div is None and RXY(s) != tas_xy(f) and not RF: div = f
            for j in range(8):
                if s[f't{j}'] == 18 and (i == 0 or st[i-1][f't{j}'] != 18): throws.append(f)
        hp = st[-1]['hp65']
        sp = (v + 26008 - F0) % 256
        res.append((v, sp, trig, hp, div, throws[:4]))
        print(f'BF@{F0} {v:3d} (spawn BF {sp:3d}, delay {sp>>1:3d}) trigger {trig} hp {hp} div {div} axes {throws[:4]}', flush=True)
    for v in vs: fc.drop(f'p{v}')
fc.close()
