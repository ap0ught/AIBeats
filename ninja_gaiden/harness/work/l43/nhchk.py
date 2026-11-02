"""NesHawk vs Mesen check of 4-3 stage rows on the locked chain (k932b, control row 19,297).
python -u work/l43/nhchk.py <stage rows> [save frames comma|-] [tag]
NesHawk: states/l42a_k18932 + k932b rows 18,933..19,296 (saved once as states/l43_k932b19296.State), then the rows.
Mesen: base state + the rows. Prints differing frames (X, y, hp, np, room, BF) and saves NesHawk states l43_<tag>_<f>."""
import sys, os
sys.path.insert(0, 'work/l43')
from lib import *
from ng.mode import TICKS
rows = rows_file(sys.argv[1])
saves = [int(x) for x in sys.argv[2].split(',')] if len(sys.argv) > 2 and sys.argv[2] != '-' else []
tag = sys.argv[3] if len(sys.argv) > 3 else 'x'
fc = core(); _, recs, _ = fc.step(rows, record='all'); fc.close()
ms = {CTL + i: (C.abs_x(s), s['y'], s['hp'], s['ninpo'], s['room'], s['bf']) for i, s in enumerate(recs)}
Pw = C.rows_of(CHAIN_POW)
e = C.open_emu('l43_nhchk.log')
def xy(m):
    hi = m[0x52] - 256 if m[0x52] >= 128 else m[0x52]
    return hi*256 + m[0x51] + m[0x86], m[0x8A]
try:
    e.tick(TICKS)
    if os.path.exists(f'states/l43_k932b{CTL - 1}.State'):
        e.load(f'l43_k932b{CTL - 1}')
    else:
        e.load('l42a_k18932'); e.run(Pw[18932:CTL - 1]); e.save(f'l43_k932b{CTL - 1}'); print('saved base', f'l43_k932b{CTL - 1}', flush=True)
    f = CTL - 1; bad = 0
    for k in sorted(set(s for s in saves if s < CTL + len(rows)) | {CTL - 1 + len(rows)}):
        seg = rows[f - CTL + 1:k - CTL + 1]
        if not seg: continue
        _, rams = e.run_ram(seg)
        for i, m in enumerate(rams):
            g = f + 1 + i
            a = xy(m) + (m[0x65], m[0x64], m[0x6E], m[0xBF])
            if a != ms.get(g):
                bad += 1
                if bad < 40: print('DIFF', g, 'neshawk', a, 'mesen', ms.get(g), 'pad', m[0x2A], flush=True)
        f = k
        if k in saves:
            e.save(f'l43_{tag}_{k}'); print('saved', f'l43_{tag}_{k}', xy(rams[-1]), 'hp', rams[-1][0x65], flush=True)
    m = rams[-1]
    print('END', f, 'X/y', xy(m), 'hp', m[0x65], 'np', m[0x64], 'rm', m[0x6E], 'item', m[0xC9], '| frames differing', bad, flush=True)
finally:
    e.close()
