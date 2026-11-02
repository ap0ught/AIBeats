"""NesHawk trace of stage rows from a state: python work/r15/nhtrace.py <rows> <state> <to> [out.bin]
prints: frame X y hp np item an pad (pad = $2A)"""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages')
from ng.solve import common as C
from ng.mode import TICKS
F0 = 14848
rows = C.rows_of(sys.argv[1]); stn = sys.argv[2]; to = int(sys.argv[3])
e = C.open_emu('r15_nh.log')
try:
    e.tick(TICKS); st = e.load(stn); f0 = st['frame']
    _, rams = e.run_ram(rows[f0 - F0:to - F0])
finally:
    e.close()
for j, m in enumerate(rams):
    f = f0 + j + 1
    X = m[0x52] * 256 + m[0x51] + m[0x86]
    print(f, '+'.join(rows[f - F0 - 1]) or '-', 'X', X, 'y', m[0x8A], 'hp', m[0x65], 'np', m[0x64], 'it', m[0xC9], 'an', m[0x80], 'pad', m[0x2A])
if len(sys.argv) > 4:
    with open(sys.argv[4], 'wb') as fo:
        fo.write(f0.to_bytes(4, 'little'))
        for m in rams: fo.write(m)
