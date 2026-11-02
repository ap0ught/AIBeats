"""Mesen twin of nhpre61.py: TAS state 30062 (l61p_tas30062.mst) + pokes + rows -> per-frame listing (same format)."""
import sys, random
sys.path.insert(0, 'work/l61p')
from lib import *
a = sys.argv[1:]
pk = {}; JS = -1
if '--pokes' in a:
    i = a.index('--pokes'); pk = {int(k, 0): int(v, 0) for k, v in (x.split('=') for x in a[i + 1].split(','))}; del a[i:i + 2]
if '--junk' in a:
    i = a.index('--junk'); JS = int(a[i + 1]); del a[i:i + 2]
rows = [row(l.strip()) for l in open(a[0]) if l.strip() and not l.startswith('#')]
fc = core(tas_mst(30062))
for k, v in pk.items(): fc.poke(k, v)
if JS >= 0:
    rng = random.Random(JS)
    for ad in range(0x400, 0x4A8): fc.poke(ad, rng.randrange(256))
_, st, _ = fc.step(rows, record='all')
with open(a[1], 'w') as fo:
    for i, s in enumerate(st):
        X, y = RXY(s)
        fo.write(f'{30063 + i} {X} {y} {s["hp65"]} {s["np64"]} {s["item"]} {s["room6e"]} {s["bf"]}\n')
fc.close()
