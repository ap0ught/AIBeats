"""python work/l23/bftest.py <2-3 rows file (from control)> <deltas> [pre-row e.g. Left|-]
Mesen: play the rows from the 2-3 control-1 state (first the pre-control row) with $BF poked by each delta at the
start. Compares per row: Ryu x/y/hp/ninpo/facing, boss slot 7 x/y/hp/pose, $66, stage $6D, timer $63/$62, all enemy
slots (type/x/y). Reports the kill row, the row where stage becomes 5, and the first difference vs delta 0."""
import sys
sys.path.insert(0, 'work/l23')
from lib import *
rows = [tuple(r) for r in C.rows_of(sys.argv[1])]
deltas = [int(d) for d in sys.argv[2].split(',')]
pre = sys.argv[3] if len(sys.argv) > 3 else 'Left'
rows = [row(pre)] + rows
fc = core('p'); fc.save('b')
def key(m):
    return (m[0x86], m[0x85], m[0x8A], m[0x65], m[0x64], m[0x84] & 0x40, m[0x66], m[0x6D], m[0x63], m[0x62],
            m[0x73], tuple(m[0x400:0x408]), tuple(m[0x460:0x468]), tuple(m[0x480:0x488]), tuple(m[0x438:0x440]))
res = {}
for d in deltas:
    fc.load('b')
    m = fc.ram()
    fc.poke(0xBF, (m[0xBF] + d) & 255)
    bf0 = fc.ram()[0xBF]
    ks = []
    kill = st5 = None
    for i, r in enumerate(rows):
        fc.step([r]); m = fc.ram(); ks.append(key(m))
        if kill is None and m[0x66] == 0 and m[0x6D] == 4: kill = i
        if st5 is None and m[0x6D] == 5: st5 = i
    res[d] = ks
    print(f'delta {d:3d} BF at control-1 = {bf0:3d}: kill row {kill} (from control), stage 5 at row {st5}, last {ks[-1][:8]}', flush=True)
for d in deltas[1:]:
    diff = next((i for i, (a, b) in enumerate(zip(res[deltas[0]], res[d])) if a != b), None)
    print('delta', d, 'first difference vs delta', deltas[0], 'at row', diff, '' if diff is None else (res[deltas[0]][diff], res[d][diff]))
fc.close()
