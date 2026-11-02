"""simulate stage rows from the 2-1 control Mesen state; print room changes + end. python work/w21/fullsim.py <rows file>"""
import sys; sys.path.insert(0,'.'); sys.path.insert(0,'work/w21')
from wlib import *
R=C.rows_of(sys.argv[1])
fc=F.FastCore(boot_rows=None); fc.put('s',open('states/mesen/w21_ctl.mst','rb').read()); fc.load('s')
_,recs,_=fc.step(R,record='all'); fc.close()
prev=None
for i,s in enumerate(recs):
    k=(s['stage'],s['room'])
    if k!=prev: print('row',i+1,'frame',3308+i+1,k,'X',C.abs_x(s),'y',s['y'],'hp',s['hp'],'np',s['ninpo']); prev=k
s=recs[-1]; print('end frame',3308+len(R),'X',C.abs_x(s),'y',s['y'],'hp',s['hp'],'np',s['ninpo'])
