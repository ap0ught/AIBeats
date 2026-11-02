"""Per-frame trace of stage rows on Mesen with enemies; compare TAS at lag. python work/l42a/tr.py <rows> f1 f2 [--lag 316]"""
import sys
sys.path.insert(0, 'work/l42a')
from lib import *
a = sys.argv[1:]
lag = LAG0
if '--lag' in a: i = a.index('--lag'); lag = int(a[i+1]); del a[i:i+2]
rows = [tuple(r) for r in C.rows_of(a[0])]; f1, f2 = int(a[1]), int(a[2])
fc = core(); _, recs, _ = fc.step(rows[:f2 - F0], record='all')
fc.close()
d = open('work/l42p/tas42_ram.bin', 'rb').read()[4:]
def tm(f): i = f - 16683; return d[i*2048:(i+1)*2048] if 0 <= i < len(d)//2048 else None
fc = core(); fc.step(rows[:f1 - F0 - 1], record='last')
for f in range(f1, f2 + 1):
    fc.step([rows[f - F0 - 1]], record='last'); m = fc.ram(); s = recs[f - F0 - 1]
    t = tm(f - lag)
    te = enemies(t) if t else []
    print(f, '+'.join(rows[f - F0 - 1]) or '-', 'X', X(m), 'y', m[0x8A], 'hp', m[0x65], 'np', m[0x64], 'BF', m[0xBF], '|', enemies(m), '|| TAS X', X(t) if t else None, t[0x8A] if t else None, te)
fc.close()
