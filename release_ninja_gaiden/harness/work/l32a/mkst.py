"""python work/l32a/mkst.py <rows file> <n> <tag>  -> states/mesen/l32a_<tag>.mst + work/l32a/h_<tag>.inputs.txt (power-on history)"""
import sys
sys.path.insert(0, 'work/l32a')
from lib import *
rf, n, tag = sys.argv[1], int(sys.argv[2]), sys.argv[3]
rows = C.rows_of(rf)[:n]
fc = core(); fc.step(rows, record='last')
r = fc.ram(); fc.save('e'); fc.save_file('e', f'states/mesen/l32a_{tag}.mst', frame=F0 + n); fc.close()
C.write_inputs(f'work/l32a/h_{tag}.inputs.txt', list(HIST) + list(rows), f'power-on {POW} + {rf}[:{n}]')
print(tag, 'frame', F0 + n, 'X', X(r), 'y', r[0x8A], 'hp', r[0x65], 'np', r[0x64], 'BF', r[0xBF], 'anim', r[0x80], '62', r[0x62])
