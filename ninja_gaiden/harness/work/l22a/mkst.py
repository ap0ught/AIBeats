"""python work/l22a/mkst.py <stage rows file> <n> <tag>  -> work/l22a/h_<tag>.inputs.txt (power-on hist) + states/mesen/l22a_<tag>.mst"""
import sys
sys.path.insert(0,'work/l22f'); sys.path.insert(0,'.')
from lib import *
rows=C.rows_of(sys.argv[1]); n=int(sys.argv[2]); tag=sys.argv[3]
rows=rows[:n]
fc=core(); fc.step(rows,record='last'); r=fc.ram()
fc.save('s'); fc.save_file('s',f'states/mesen/l22a_{tag}.mst',frame=F0+n); fc.close()
C.write_inputs(f'work/l22a/h_{tag}.inputs.txt', list(HIST)+list(rows), f'power-on hist + 2-2 rows[:{n}]')
print('frame',F0+n,'X',r[0x86],'y',r[0x8A],'BF',r[0xBF])
