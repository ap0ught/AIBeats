"""l53c: NesHawk vs Mesen for rows from F0+1 on the real line. NesHawk from state <nh> (after row Fn <= F0; blanks Fn+1..F0),
Mesen from <mst> (after row F0). python work/l53c/nhv.py rows.txt <nh name> Fn <mst> F0 [--save f1,f2] [--poke ..]"""
import sys
sys.path.insert(0, 'work/l53p')
from lib import *
from ng.mode import TICKS
a = sys.argv[1:]
SAVES = []
BR = ''
if '--bridge' in a: i = a.index('--bridge'); BR = a[i+1]; del a[i:i+2]
if '--save' in a: i = a.index('--save'); SAVES = [int(x) for x in a[i+1].split(',')]; del a[i:i+2]
rows = [row(l.strip()) for l in open(a[0]) if l.strip() and not l.startswith('#')]
nh, Fn, mst, F0 = a[1], int(a[2]), a[3], int(a[4])
fc = core(mst); _, recs, _ = fc.step(rows, record='all'); ms_end = fc.ram(); fc.close()
ms = {F0 + 1 + i: RXY(s) + (s['hp65'], s['np64'], s['item'], s['room6e'], s['st6d']) for i, s in enumerate(recs)}
e = C.open_emu('l53c_nhv.log'); bad = 0
try:
    e.tick(TICKS); st = e.load(nh); print('NesHawk state', nh, 'frame', st.get('frame'), flush=True)
    fs = st.get('frame') or Fn
    if BR:
        from ng.inputs import read_inputs
        pr = list(read_inputs(BR)); pr += [()] * max(0, F0 - len(pr))
        e.run_ram(pr[fs:F0])
    elif F0 > fs: e.run_ram([()] * (F0 - fs))
    m0 = e.ram_all(); print('NesHawk at', F0, XY(m0), 'BF', m0[0xBF], 'np', m0[0x64], 'hp', m0[0x65], flush=True)
    f = F0
    for k in sorted(set(s for s in SAVES if F0 < s < F0 + len(rows)) | {F0 + len(rows)}):
        _, rams = e.run_ram(rows[f - F0:k - F0])
        for i, mm in enumerate(rams):
            g = f + 1 + i
            q = XY(mm) + (mm[0x65], mm[0x64], mm[0xC9], mm[0x6E], mm[0x6D])
            if q != ms[g]:
                bad += 1
                if bad < 20: print('DIFF', g, 'neshawk', q, 'mesen', ms[g], flush=True)
        m = rams[-1]; f = k
        if k in SAVES: e.save(f'l53c_{k}'); print('saved NesHawk', f'l53c_{k}', XY(m), flush=True)
finally:
    e.close()
rd = [(hex(a_), ms_end[a_], m[a_]) for a_ in range(0x800) if ms_end[a_] != m[a_] and not (0x100 <= a_ < 0x300)]
print('END RAM diff (Mesen, NesHawk; no stack/OAM):', len(rd), rd[:20])
print('END', f, XY(m), 'hp', m[0x65], 'np', m[0x64], 'it', m[0xC9], 'rm', m[0x6E], 'st', m[0x6D], '| frames differing', bad)
