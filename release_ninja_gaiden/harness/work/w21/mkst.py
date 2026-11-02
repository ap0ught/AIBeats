"""python work/w21/mkst.py <in mst> <rows file> <out mst> [n rows]  -> play rows, save state, print trace tail"""
import sys; sys.path.insert(0,'.')
from ng.solve import common as C
from ng import fastcore as F
rows=C.rows_of(sys.argv[2])
if len(sys.argv)>4: rows=rows[:int(sys.argv[4])]
fc=F.FastCore(boot_rows=None); fc.put('s',open(sys.argv[1],'rb').read()); fc.load('s')
_,recs,_=fc.step(rows,record='all')
for i,s in enumerate(recs[-6:]): print(len(recs)-6+i+1, 'r',s['room'],'X',C.abs_x(s),'y',s['y'],'vy',s['vy'],'coll',s['coll'],'rf',s['rflags'],'hp',s['hp'],'np',s['ninpo'],'bf',s['rng'])
fc.save('o'); fc.save_file('o',sys.argv[3]); fc.close()
