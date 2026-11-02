"""python work/l21f/mkst.py <stage rows file> <n> <tag>  -> work/l21f/h_<tag>.inputs.txt (power-on hist) + states/mesen/l21f_<tag>.mst"""
import sys
sys.path.insert(0,'work/l21f'); sys.path.insert(0,'.')
from lib import *
rows=C.rows_of(sys.argv[1]); n=int(sys.argv[2]); tag=sys.argv[3]
rows=rows[:n]
fc=core(); fc.step(rows,record='last'); r=fc.ram()
fc.save('s'); fc.save_file('s',f'states/mesen/l21f_{tag}.mst',frame=F0+n); fc.close()
C.write_inputs(f'work/l21f/h_{tag}.inputs.txt', list(HIST)+list(rows), f'power-on hist + 2-1 rows[:{n}]')
print('frame',F0+n,'X',r[0x86],'y',r[0x8A],'BF',r[0xBF])
