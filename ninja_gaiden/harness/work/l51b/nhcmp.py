"""NesHawk vs Mesen per-frame compare incl. enemy slots and pad, stage rows from lock_51_pre, frames a..b.
python work/l51b/nhcmp.py <stage rows> a b"""
import sys
sys.path.insert(0, 'work/l51b')
from lb import *
from ng.mode import TICKS
rows = [tuple(sorted(r)) for r in C.rows_of(sys.argv[1])]; a, b = int(sys.argv[2]), int(sys.argv[3])
def info(m):
    X, y = XY(m); scr = X - m[0x86]
    return (X, y, m[0x65], m[0x2A]), tuple((j, m[0x400+j], scr + m[0x460+j], m[0x480+j]) for j in range(8) if m[0x73] >> j & 1)
fc = core('states/mesen/lock_51_pre.mst')
fc.step(rows[:23588 - 22628], record='last'); fc.poke(0x47D, 118)
fc.step(rows[23588 - 22628:a - 1 - 22628], record='last')
mm = []
for r in rows[a - 1 - 22628:b - 22628]:
    fc.step([r], record='last'); mm.append(info(fc.ram()))
fc.close()
e = C.open_emu('l51b_nhcmp.log')
try:
    e.tick(TICKS); e.load('lock_51_pre')
    e.run_ram(rows[:a - 1 - 22628])
    _, rams = e.run_ram(rows[a - 1 - 22628:b - 22628])
    for i, m in enumerate(rams):
        n = info(m); f = a + i
        flag = '' if n == mm[i] else '  <<<'
        print(f, 'row', P(rows[f - 22629]), 'NH', n, flag)
        if flag: print('        MS', mm[i])
finally:
    e.close()
