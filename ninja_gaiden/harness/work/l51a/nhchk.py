"""NesHawk vs Mesen check of 5-1 stage rows (row 1 = control row 22,629) from states/lock_51_pre (after row 22,628).
python -u work/l51a/nhchk.py <stage rows> [save frames comma|-] [tag]
Prints differing frames (X, y, hp, np, item, BF) and saves NesHawk states l51a_<tag>_<f>."""
import sys
sys.path.insert(0, 'work/l51a')
from lib import *
from ng.mode import TICKS
rows = rows_file(sys.argv[1])
saves = [int(x) for x in sys.argv[2].split(',')] if len(sys.argv) > 2 and sys.argv[2] != '-' else []
tag = sys.argv[3] if len(sys.argv) > 3 else 'x'
ms = {t[0]: (t[1], t[2], t[3], t[4], t[5], t[6]) for t in trace(rows)}
e = C.open_emu('l51a_nhchk.log')
def xy(m):
    hi = m[0x52] - 256 if m[0x52] >= 128 else m[0x52]
    return hi*256 + m[0x51] + m[0x86], m[0x8A]
try:
    e.tick(TICKS)
    st = e.load('lock_51_pre'); assert st['frame'] == CTL - 1, st
    f = CTL - 1; bad = 0; rams = None
    for k in sorted(set(s for s in saves if s < CTL + len(rows)) | {CTL - 1 + len(rows)}):
        seg = rows[f - CTL + 1:k - CTL + 1]
        if not seg: continue
        _, rams = e.run_ram(seg)
        for i, m in enumerate(rams):
            g = f + 1 + i
            a = xy(m) + (m[0x65], m[0x64], m[0xC9], m[0xBF])
            if g in ms and a != ms.get(g):
                bad += 1
                if bad < 30: print('DIFF', g, 'neshawk', a, 'mesen', ms.get(g), 'pad', m[0x2A], flush=True)
        f = k
        if k in saves:
            e.save(f'l51a_{tag}_{k}'); print('saved', f'l51a_{tag}_{k}', xy(rams[-1]), 'hp', rams[-1][0x65], 'np', rams[-1][0x64], flush=True)
    m = rams[-1]
    fc, k = start_core(rows); fc.step(rows[k:], record='last'); mm = fc.ram(); fc.close()
    rd = [(hex(a_), mm[a_], m[a_]) for a_ in range(0x800) if mm[a_] != m[a_] and not (0x100 <= a_ < 0x300)]
    print('END RAM diff (Mesen, NesHawk; no stack/OAM):', rd[:20], flush=True)
    print('END', f, 'X/y', xy(m), 'hp', m[0x65], 'np', m[0x64], 'rm', m[0x6E], 'item', m[0xC9], 'BF', m[0xBF], '| frames differing', bad, flush=True)
finally:
    e.close()
