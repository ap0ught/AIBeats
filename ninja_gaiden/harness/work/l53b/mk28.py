"""l53b: real e4 room-28 arrival. l53a_e4_27359.mst + l53a ch1_rows (476 rows, row 1 = 27,360) + blanks -> states
states/mesen/l53b_e4_<f>.mst for f in 27835 (room change), 27857 (room-28 control - 1). Compare Ryu vs TAS at lag 822."""
import sys
sys.path.insert(0, 'work/l53p'); sys.path.insert(0, 'work/l53b')
from lb import *
rows = [row(l.strip()) for l in open('work/l53a/ch1_rows.txt') if l.strip() and not l.startswith('#')]
fc = core('states/mesen/l53a_e4_27359.mst')
fc.step(rows, record='last')
m = fc.ram(); print('27835', XY(m), 'hp', m[0x65], 'np', m[0x64], 'it', m[0xC9], 'rm', m[0x6E], 'BF', m[0xBF])
fc.save('a'); fc.save_file('a', 'states/mesen/l53b_e4_27835.mst', 27835)
fc.step([()] * 22, record='last')
m = fc.ram(); print('27857', XY(m), 'hp', m[0x65], 'np', m[0x64], 'rm', m[0x6E], 'BF', m[0xBF], '5C', m[0x5C])
fc.save('b'); fc.save_file('b', 'states/mesen/l53b_e4_27857.mst', 27857)
t = TM(27035)
print('TAS 27035', XY(t), 'BF', t[0xBF], '5C', t[0x5C])
d = [(hex(a), m[a], t[a]) for a in range(0x800) if m[a] != t[a] and not (0x100 <= a < 0x300)]
print('diffs vs TAS 27035 (no stack/OAM):', len(d)); print(d[:80])
fc.close()
