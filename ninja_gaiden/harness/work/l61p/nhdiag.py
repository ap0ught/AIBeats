"""NesHawk diag: ref4751/16_6-1_control (+pokes) + rows file (row 1 = 30063); print Ryu + active enemy slots for frames a..b.
python work/l61p/nhdiag.py <rows> a b [--pokes 0xBF=v]"""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages'); sys.path.insert(0, 'work/l61p')
from ng.solve import common as C
from ng.mode import TICKS
from lib0 import XY
a = sys.argv[1:]
pk = {}
if '--pokes' in a:
    i = a.index('--pokes'); pk = {int(k, 0): int(v, 0) for k, v in (x.split('=') for x in a[i + 1].split(','))}; del a[i:i + 2]
rows = [l.strip() for l in open(a[0]) if l.strip() and not l.startswith('#')]
rows = [() if r == '-' else tuple(r.split('+')) for r in rows]
A_, B_ = int(a[1]), int(a[2])
e = C.open_emu('l61p_nhdiag.log')
try:
    e.tick(TICKS)
    st = e.load('ref4751/16_6-1_control'); f0 = st['frame']
    for k, v in pk.items(): e.poke(k, v)
    _, rams = e.run_ram(rows[f0 - 30062:B_ - 30062])
    for i, m in enumerate(rams):
        f = f0 + 1 + i
        if f < A_: continue
        scr = (m[0x52] - 256 if m[0x52] >= 128 else m[0x52]) * 256 + m[0x51]
        en = [f's{j}:t{m[0x400+j]}({scr+m[0x460+j]},{m[0x480+j]})' for j in range(8) if m[0x73] >> j & 1]
        print(f, XY(m), 'hp', m[0x65], 'BF', m[0xBF], ' '.join(en), flush=True)
finally:
    e.close()
