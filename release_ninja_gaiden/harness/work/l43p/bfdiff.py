"""Which enemy types change with $BF on the TAS line: per value, frames where a slot differs, by (TAS type, our type)."""
import sys; sys.path.insert(0, 'work/l43p')
from lib import *
from collections import Counter
for j in range(8): FLD[f'ex{j}'] = 0x460 + j; FLD[f'ey{j}'] = 0x480 + j
END = 21074
pads = [TPAD[f] for f in range(18961, END + 1)]
fc = core(tas_mst(18960)); fc.save('b')
def en(m): return tuple((m[0x400+j] if m[0x73] >> j & 1 else 0, m[0x460+j], m[0x480+j]) for j in range(8))
def en_r(r): return tuple((r[f't{j}'] if r['eact'] >> j & 1 else 0, r[f'ex{j}'], r[f'ey{j}']) for j in range(8))
for v in [int(x) for x in sys.argv[1:]]:
    fc.load('b'); fc.poke(0xBF, v)
    _, recs, _ = fc.step(pads, record='all')
    cnt = Counter(); first = {}
    for i, r in enumerate(recs):
        f = 18961 + i; a = en_r(r); b = en(TM(f))
        for j in range(8):
            if a[j] != b[j]:
                k = (b[j][0], a[j][0]); cnt[k] += 1; first.setdefault(k, (f, j, b[j], a[j]))
    print('BF', v, 'diff frames by (TAS type, our type):', dict(cnt))
    for k, z in sorted(first.items(), key=lambda kv: kv[1][0]): print('   first', k, z)
fc.close()
