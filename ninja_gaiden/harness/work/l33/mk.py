"""python work/l33/mk.py <tag>  -> states/mesen/l33_<tag>_ctl.mst (3-3 control) from lock_32_ctl.mst + the 3-2 stage rows."""
import sys
sys.path.insert(0, 'work/l33')
from lib import *
tag = sys.argv[1]
c = CANDS[tag]
rows = C.rows_of(c['stage'])
fc = F.FastCore(boot_rows=None, ticks=True, fields=FLD); fc.put('s', open(L32_MST, 'rb').read()); fc.load('s')
fc.step(rows, record='last')
r = fc.ram(); fc.save('e'); fc.save_file('e', mst(tag), frame=L32_F0 + len(rows)); fc.close()
print(tag, 'frame', L32_F0 + len(rows), 'x', r[0x86], 'y', r[0x8A], 'hp', r[0x65], 'np', r[0x64], 'item', r[0xC9], 'BF', r[0xBF], '62', r[0x62], 'timer', r[0x63], 'stage', r[0x6D], '73', hex(r[0x73]), 'vx', r[0xAD], r[0xAC])
print('slots', ' '.join(f"{r[0x400+i]:02x}:{r[0x460+i]},{r[0x480+i]}" for i in range(8)))
