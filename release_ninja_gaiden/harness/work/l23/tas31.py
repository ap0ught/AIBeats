"""NesHawk analysis: TAS 3-1 from ref4751/05_3-1_control: lantern breaks / pickups, enemy deaths, star throws, with
Ryu's absolute X, y, inputs. python work/l23/tas31.py [n frames]"""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages')
from ng.solve import common as C
from ng.mode import TICKS
import a56_common as A
n = int(sys.argv[1]) if len(sys.argv) > 1 else 1500
TR = A.tas_rows()
e = C.open_emu('l23_tas31.log')
try:
    e.tick(TICKS)
    st = e.load('ref4751/05_3-1_control')
    f0 = st['frame']
    print('TAS 3-1 control state frame', f0)
    rows = TR[f0:f0 + n]
    _, rams = e.run_ram(rows)
finally:
    e.close()
prev = None
for i, m in enumerate(rams):
    f = f0 + i + 1
    X = m[0x52] * 256 + m[0x51] + m[0x86]
    lan = [(m[0x4D9 + j] + 0, m[0x4E1 + j], m[0x4D1 + j] & 0x0C, m[0x4C9 + j] & 15) for j in range(4) if m[0xC0] & (1 << j)]
    en = [(j, m[0x400 + j], m[0x490 + j]) for j in range(8) if m[0x73] & (1 << j)]
    k = (m[0x64], m[0xC9], m[0x65], m[0xC8], tuple(l[2] for l in lan), tuple(e_[0] for e_ in en))
    if prev is not None and k != prev:
        print(f, 'X', X, 'y', m[0x8A], 'in', '+'.join(rows[i]) or '-', 'np', m[0x64], 'item', m[0xC9], 'hp', m[0x65],
              'thrown', m[0xC8], 'lanterns(scr x,y,state,item)', lan, 'enemies(slot,type,hp)', en)
    prev = k
    if m[0x6D] != 5:
        print('stage change at', f); break
