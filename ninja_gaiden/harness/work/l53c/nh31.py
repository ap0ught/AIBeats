"""l53c: NesHawk vs Mesen for a row file starting at F0+1 from the TAS line (TAS rows to F0 from ref4751/14_5-3_control),
with pokes applied after F0 on both. python work/l53c/nh31.py rows.txt F0 [--poke '64=20,65=3'] [--save f1,f2]"""
import sys
sys.path.insert(0, 'work/l53p')
from lib import *
from ng.mode import TICKS
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return type(d)(v)
    return d
POKE = opt('--poke', ''); SAVES = [int(x) for x in opt('--save', '').split(',') if x]
rows = [row(l.strip()) for l in open(a[0]) if l.strip() and not l.startswith('#')]
F0 = int(a[1])
pk = [(int(k, 16), int(v)) for k, v in (p.split('=') for p in POKE.split(',') if p)]
fc = core_at(F0)
for k, v in pk: fc.poke(k, v)
_, recs, _ = fc.step(rows, record='all'); ms_end = fc.ram(); fc.close()
ms = {F0 + 1 + i: RXY(s) + (s['hp65'], s['np64'], s['item'], s['room6e'], s['st6d']) for i, s in enumerate(recs)}
e = C.open_emu('l53c_nh31.log')
bad = 0
try:
    e.tick(TICKS); st = e.load('ref4751/14_5-3_control'); f = st.get('frame'); print('NesHawk state frame', f, flush=True)
    TR = A.tas_rows()
    e.run_ram([TR[g - 1] for g in range(f + 1, F0 + 1)])
    m0 = e.ram_all(); print('NesHawk at', F0, XY(m0), 'BF', m0[0xBF], 'TAS dump', tas_xy(F0), TM(F0)[0xBF], flush=True)
    for k, v in pk: e.poke(k, v)
    f = F0
    for k in sorted(set(s for s in SAVES if F0 < s < F0 + len(rows)) | {F0 + len(rows)}):
        seg = rows[f - F0:k - F0]
        _, rams = e.run_ram(seg)
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
