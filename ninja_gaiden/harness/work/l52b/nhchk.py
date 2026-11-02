"""NesHawk vs Mesen check of rows from a matching pair of states (agent l52b).
python -u work/l52b/nhchk.py <neshawk state name> <mesen .mst> <F0> <rows file (from F0+1)> [save frames comma|-] [tag]
Compares X, y, hp, np, item, room, $5C on every frame and the full RAM at the end (no stack/OAM); saves NesHawk states
l52b_<tag>_<f>. Rows files: one row per line, '-' or '' = blank, '#' lines skipped."""
import sys
sys.path.insert(0, 'work/l52p')
from lib import *
if os.environ.get('MINGB'):
    import fcka as _fk; d = list(_fk._init.__defaults__); d[-1] = float(os.environ['MINGB']); _fk._init.__defaults__ = tuple(d)
from ng.mode import TICKS
nhs, mst, F0, rf = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
saves = [int(x) for x in sys.argv[5].split(',')] if len(sys.argv) > 5 and sys.argv[5] != '-' else []
tag = sys.argv[6] if len(sys.argv) > 6 else 'x'
rows = []
for l in open(rf):
    l = l.rstrip('\n').strip()
    if l.startswith('#'): continue
    rows.append(() if l in ('', '-') else tuple(sorted(x for x in l.split('+') if x)))
fc = core(mst); _, recs, _ = fc.step(rows, record='all'); ms_end = fc.ram(); fc.close()
ms = {F0 + 1 + i: RXY(s) + (s['hp65'], s['np64'], s['item'], s['room6e'], s['e5c']) for i, s in enumerate(recs)}
e = C.open_emu('l52b_nhchk.log')
m = None; bad = 0; f = F0
try:
    e.tick(TICKS); st = e.load(nhs); assert st['frame'] == F0, st
    for k in sorted(set(s for s in saves if F0 < s < F0 + len(rows)) | {F0 + len(rows)}):
        seg = rows[f - F0:k - F0]
        if not seg: continue
        _, rams = e.run_ram(seg)
        for i, mm in enumerate(rams):
            g = f + 1 + i
            a_ = XY(mm) + (mm[0x65], mm[0x64], mm[0xC9], mm[0x6E], mm[0x5C])
            if a_ != ms[g]:
                bad += 1
                if bad < 30: print('DIFF', g, 'neshawk', a_, 'mesen', ms[g], 'pad', mm[0x2A], flush=True)
        m = rams[-1]; f = k
        if k in saves:
            e.save(f'l52b_{tag}_{k}'); print('saved', f'l52b_{tag}_{k}', XY(m), 'hp', m[0x65], 'np', m[0x64], flush=True)
finally:
    e.close()
rd = [(hex(a_), ms_end[a_], m[a_]) for a_ in range(0x800) if ms_end[a_] != m[a_] and not (0x100 <= a_ < 0x300)]
print('END RAM diff (Mesen, NesHawk; no stack/OAM):', len(rd), rd[:20])
print('END', f, XY(m), 'hp', m[0x65], 'np', m[0x64], 'it', m[0xC9], 'rm', m[0x6E], 'BF', m[0xBF], '| frames differing', bad, flush=True)
