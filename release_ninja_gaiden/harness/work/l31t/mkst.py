"""python work/l31t/mkst.py <stage rows file> <n> <tag>  -> work/l31t/h_<tag>.inputs.txt (power-on hist) + states/mesen/l31t_<tag>.mst"""
import sys
sys.path.insert(0, 'work/l31t'); sys.path.insert(0, '.')
from lib import *
rows = C.rows_of(sys.argv[1]); n = int(sys.argv[2]); tag = sys.argv[3]
rows = rows[:n]
fc = core(); fc.step(rows, record='last'); r = fc.ram()
fc.save('s'); fc.save_file('s', f'states/mesen/l31t_{tag}.mst', frame=F0 + n); fc.close()
C.write_inputs(f'work/l31t/h_{tag}.inputs.txt', list(HIST) + list(rows), f'power-on hist + 3-1 rows[:{n}]')
X = r[0x52] * 256 + r[0x51] + r[0x86]
print('frame', F0 + n, 'X', X, 'y', r[0x8A], 'hp', r[0x65], 'np', r[0x64], 'item', r[0xC9], 'BF', r[0xBF])
