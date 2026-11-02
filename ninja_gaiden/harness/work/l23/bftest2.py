"""python work/l23/bftest2.py <2-2 stage rows (incl. the pre-control Left)> <2-3 rows from control> <rows before 2-3 control to poke> <deltas>
Mesen: poke $BF earlier (e.g. in 2-2 room 8 / during the act cutscene, BEFORE the boss spawns), then play to the
3-1 load; compare the 2-3 part (boss, Ryu, timer, stage) row by row."""
import sys
sys.path.insert(0, 'work/l23')
from lib import *
s22 = [tuple(r) for r in C.rows_of(sys.argv[1])]
s23 = [tuple(r) for r in C.rows_of(sys.argv[2])]
back = int(sys.argv[3]); deltas = [int(d) for d in sys.argv[4].split(',')]
fc = L22.core()
fc.step(s22[:len(s22) - back]); fc.save('b')
def key(m):
    return (m[0x86], m[0x85], m[0x8A], m[0x65], m[0x64], m[0x84] & 0x40, m[0x66], m[0x6D], m[0x63], m[0x62],
            m[0x73], tuple(m[0x400:0x408]), tuple(m[0x460:0x468]), tuple(m[0x480:0x488]), tuple(m[0x438:0x440]))
res = {}
for d in deltas:
    fc.load('b'); m = fc.ram(); fc.poke(0xBF, (m[0xBF] + d) & 255)
    fc.step(s22[len(s22) - back:])
    bfc = fc.ram()[0xBF]
    ks = []; kill = st5 = None
    for i, r in enumerate(s23):
        fc.step([r]); m = fc.ram(); ks.append(key(m))
        if kill is None and m[0x66] == 0 and m[0x6D] == 4: kill = i + 1
        if st5 is None and m[0x6D] == 5: st5 = i + 1
    res[d] = ks
    print(f'delta {d:3d}: BF at 2-3 control {bfc:3d}, kill row {kill}, stage 5 at row {st5}', flush=True)
for d in deltas[1:]:
    diff = next((i + 1 for i, (a, b) in enumerate(zip(res[deltas[0]], res[d])) if a != b), None)
    print('delta', d, 'first difference at 2-3 row', diff)
fc.close()
