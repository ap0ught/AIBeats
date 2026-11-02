"""NesHawk vs Mesen check of 5-2 rows (file rows from 24,998) from NesHawk state l52a_c3d_24997.
python -u work/l52a/nhchk.py <rows file> [extra blank rows] [save frames comma|-] [tag]"""
import sys; sys.path.insert(0, 'work/l52a')
from lib2 import *
from ng.mode import TICKS
rows = rows_file(sys.argv[1]); extra = int(sys.argv[2]) if len(sys.argv) > 2 else 0
rows = rows + [()] * extra
saves = [int(x) for x in sys.argv[3].split(',')] if len(sys.argv) > 3 and sys.argv[3] != '-' else []
tag = sys.argv[4] if len(sys.argv) > 4 else 'x'
fc = core(BASE52); _, recs, _ = fc.step(rows, record='all'); ms_end = fc.ram(); fc.close()
ms = {CTL52 + i: RXY(s) + (s['hp65'], s['np64'], s['item'], s['room6e']) for i, s in enumerate(recs)}
e = C.open_emu('l52a_nhchk.log')
try:
    e.tick(TICKS); st = e.load('l52a_c3d_24997'); assert st['frame'] == CTL52 - 1, st
    f = CTL52 - 1; bad = 0; m = None
    for k in sorted(set(s for s in saves if s < CTL52 + len(rows)) | {CTL52 - 1 + len(rows)}):
        seg = rows[f - CTL52 + 1:k - CTL52 + 1]
        if not seg: continue
        _, rams = e.run_ram(seg)
        for i, mm in enumerate(rams):
            g = f + 1 + i
            a = XY(mm) + (mm[0x65], mm[0x64], mm[0xC9], mm[0x6E])
            if a != ms[g]:
                bad += 1
                if bad < 30: print('DIFF', g, 'neshawk', a, 'mesen', ms[g], flush=True)
        m = rams[-1]; f = k
        if k in saves:
            e.save(f'l52a_{tag}_{k}'); print('saved', f'l52a_{tag}_{k}', XY(m), 'hp', m[0x65], 'np', m[0x64], flush=True)
finally:
    e.close()
rd = [(hex(a_), ms_end[a_], m[a_]) for a_ in range(0x800) if ms_end[a_] != m[a_] and not (0x100 <= a_ < 0x300)]
print('END RAM diff (Mesen, NesHawk; no stack/OAM):', len(rd), rd[:20])
print('END', f, XY(m), 'hp', m[0x65], 'np', m[0x64], 'it', m[0xC9], 'rm', m[0x6E], 'BF', m[0xBF], '| frames differing', bad)
