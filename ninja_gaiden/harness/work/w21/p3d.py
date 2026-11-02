import sys; sys.path.insert(0,'.'); sys.path.insert(0,'work/w21')
from wlib import *
cy='R RU RU ALU AL'
mst,histf,out_f=sys.argv[1:4]
wants=[];labs=[]
starts=['R RU RU ALU AL','RU RU ALU AL','RU ALU AL','ALU AL','U ALU AL','AL','U AL','UR UL AL AR R','R:2 AL']
for pre in ('-:18','-:19','-:20'):
  for st in starts:
    for k in (7,8,9):
      for a in range(20,30):
          s=f"{pre} {st} {' '.join([cy]*k)} L:{a} R:1 AR:2 R:40"
          wants.append(spec(s)); labs.append((pre,st,k,a))
goal=lambda s: s['room']==3 and s['y']==128 and C.abs_x(s)>=158 and not (s['rflags']&4)
out=search(mst,C.rows_of(histf),wants,goal,labs,top=8)
if out: C.write_inputs(out_f,out[0][4],f'p3d {out[0][3]}')
