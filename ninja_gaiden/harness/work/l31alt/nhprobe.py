"""NesHawk geometry probe: TAS 3-1 to frame F, then a spec (wlib syntax); print per-frame Ryu/lantern/item.
python work/l31alt/nhprobe.py F "<spec>" ["<spec>" ...]"""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages'); sys.path.insert(0, 'work/w21')
from ng.solve import common as C, hitbox as H
from ng.mode import TICKS
import a56_common as A
from wlib import spec, fmt
TR = A.tas_rows()
F = int(sys.argv[1])
e = C.open_emu('l31alt_nhprobe.log')
try:
    e.tick(TICKS); st = e.load('ref4751/05_3-1_control'); f0 = st['frame']
    e.run(TR[f0:F]); sid = e.msave()
    for sp in sys.argv[2:]:
        e.mload(sid)
        rows = spec(sp)
        _, rams = e.run_ram(rows)
        print('==', sp)
        for i, (r, m) in enumerate(zip(rows, rams)):
            sc = (m[0x52] - 256 if m[0x52] >= 128 else m[0x52]) * 256 + m[0x51]
            ry = H.ryu(m)
            ls = [(sc + l['x'], l['y'], l['item'], l['state']) for l in H.lanterns(m) if l['item'] in (10, 1)]
            print(F + i + 1, ''.join(c[0] for c in r) or '-', 'X', sc + m[0x86], 'y', m[0x8A], 'act', ry['action'], 'pose', ry['pose'], 'L' if ry['left'] else 'R', 'air' if ry['air'] else 'gnd', 'it', m[0xC9], 'np', m[0x64], 'hp', m[0x65], 'lan', ls)
finally:
    e.close()
