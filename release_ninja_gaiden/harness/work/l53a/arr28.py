"""l53a: room-28 arrival: Mesen state after the ch1 rows + pad on e4, compare Ryu RAM with the TAS at the same offset from
the room change. python work/l53a/arr28.py"""
import sys
sys.path.insert(0, 'work/l53p')
from lib import *
RF = sys.argv[1] if len(sys.argv) > 1 else 'work/l53a/ch1_rows.txt'; TAG = sys.argv[3] if len(sys.argv) > 3 else 'e4'
rows = [row(l.strip()) for l in open(RF) if l.strip()]
F = 27360; RC = int(sys.argv[2]) if len(sys.argv) > 2 else 27835; TRC = 27013
fc = core('states/mesen/l53a_e4_27359.mst')
pad = RC + 23 - (F + len(rows) - 1)        # rows to the room-28 control row - 1 (TAS 27035)
_, st, _ = fc.step(rows + [()] * (pad - 1), record='all')
fc.save('x'); open(f'states/mesen/l53a_{TAG}_{RC + 22}.mst', 'wb').write(fc.get('x'))
m = fc.ram(); t = TM(TRC + 22)
print('saved', f'states/mesen/l53a_{TAG}_{RC + 22}.mst', 'XY', XY(m), 'TAS', XY(t))
d = [(hex(a), m[a], t[a]) for a in list(range(0x80, 0x9F)) + [0x64, 0x65, 0xC9, 0x6E, 0x6D, 0x5C, 0x51, 0x52, 0xBF] if m[a] != t[a]]
print('Ryu/page diffs vs TAS at room change + 22:', d)
fc.close()
