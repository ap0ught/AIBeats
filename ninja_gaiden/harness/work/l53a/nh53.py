"""l53a: NesHawk check of 5-3 stage rows (row 1 = control row F) from NesHawk state <name> (= after row F, so row 1 must equal
the chain's row F) vs Mesen from <mst before F>. python work/l53a/nh53.py rows.txt <nh state> <mst F-1> <F> [pad] [save frames]"""
import sys
sys.path.insert(0, 'work/l53p')
from lib import *
from ng.mode import TICKS
rows = [row(l.strip()) for l in open(sys.argv[1]) if l.strip() and not l.startswith('#')]
nh, mst, F = sys.argv[2], sys.argv[3], int(sys.argv[4])
pad = int(sys.argv[5]) if len(sys.argv) > 5 else 0
saves = [int(x) for x in sys.argv[6].split(',')] if len(sys.argv) > 6 else []
rows = rows + [()] * pad
fc = core(mst); _, recs, _ = fc.step(rows, record='all'); ms_end = fc.ram(); fc.close()
ms = {F + i: RXY(s) + (s['hp65'], s['np64'], s['item'], s['room6e']) for i, s in enumerate(recs)}
e = C.open_emu('l53a_nh53.log')
bad = 0
try:
    e.tick(TICKS); st = e.load(nh); print('NesHawk state frame', st.get('frame'), flush=True)
    f = F; m = None
    for k in sorted(set(s for s in saves if F < s < F + len(rows) - 1) | {F + len(rows) - 1}):
        seg = rows[f - F + 1:k - F + 1]
        _, rams = e.run_ram(seg)
        for i, mm in enumerate(rams):
            g = f + 1 + i
            a = XY(mm) + (mm[0x65], mm[0x64], mm[0xC9], mm[0x6E])
            if a != ms[g]:
                bad += 1
                if bad < 20: print('DIFF', g, 'neshawk', a, 'mesen', ms[g], flush=True)
        m = rams[-1]; f = k
        if k in saves: e.save(f'l53a_{k}'); print('saved NesHawk', f'l53a_{k}', XY(m), flush=True)
finally:
    e.close()
rd = [(hex(a_), ms_end[a_], m[a_]) for a_ in range(0x800) if ms_end[a_] != m[a_] and not (0x100 <= a_ < 0x300)]
print('END RAM diff (Mesen, NesHawk; no stack/OAM):', len(rd), rd[:20])
print('END', f, XY(m), 'hp', m[0x65], 'np', m[0x64], 'it', m[0xC9], 'rm', m[0x6E], 'BF', m[0xBF], '| frames differing', bad)
