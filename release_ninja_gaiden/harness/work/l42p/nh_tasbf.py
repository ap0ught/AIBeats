"""NesHawk: TAS rows (or a rows file) from ref4751/09_4-2_control with $BF poked at control; misreads + divergence vs the
TAS dump. python work/l42p/nh_tasbf.py <c> [rows file (rows[0] = control row)] [to]"""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages')
from ng.solve import common as C
from ng.mode import TICKS
from ng.inputs import to_mask
import a56_common as A
c = int(sys.argv[1]); TO = int(sys.argv[3]) if len(sys.argv) > 3 else 17620
if len(sys.argv) > 2 and sys.argv[2] != 'tas': rows = [tuple(r) for r in C.rows_of(sys.argv[2])][1:]
else: rows = [tuple(r) for r in A.tas_rows()[16682:TO]]
rows = rows[:TO - 16682]
d = open('work/l42p/tas42_ram.bin', 'rb').read()[4:]
e = C.open_emu('l42p_nhtb.log')
try:
    e.tick(TICKS); e.load('ref4751/09_4-2_control'); e.poke(0xBF, c)
    _, rams = e.run_ram(rows)
finally:
    e.close()
mis = []; hp = 16; div = None
for i, m in enumerate(rams):
    f = 16683 + i
    if m[0x2A] != to_mask(rows[i]): mis.append(f)
    t = d[i*2048:(i+1)*2048]
    X = m[0x52]*256 + m[0x51] + m[0x86]; tX = t[0x52]*256 + t[0x51] + t[0x86]
    if div is None and (X, m[0x8A]) != (tX, t[0x8A]): div = (f, X, m[0x8A], tX, t[0x8A])
    if m[0x65] < hp: print('hit', f, m[0x65], 'X', X)
    hp = m[0x65]
print('c', c, 'misreads', mis[:20], 'first divergence from the TAS (f, X, y, tasX, tasy)', div, 'end X', X, 'hp', hp)
