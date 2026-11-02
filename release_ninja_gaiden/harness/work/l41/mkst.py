"""python work/l41/mkst.py <rows> <frame> <tag> -> states/mesen/l41_<tag>.mst (Mesen, rows from l41_ctl to <frame>)"""
import sys
sys.path.insert(0, 'work/l41')
from lib import *
rf, fr, tag = sys.argv[1], int(sys.argv[2]), sys.argv[3]
rows = C.rows_of(rf)[:fr - F0]
fc = core(); fc.step(rows, record='last'); r = fc.ram(); fc.save('e'); fc.save_file('e', f'states/mesen/l41_{tag}.mst', frame=fr); fc.close()
print(tag, 'frame', fr, 'X', X(r), 'y', r[0x8A], 'hp', r[0x65], 'np', r[0x64], 'item', r[0xC9], 'BF', r[0xBF], 'room', r[0x6E])
