import sys; sys.path.insert(0,'.'); sys.path.insert(0,'work/w21')
from wlib import *
cy='R RU RU ALU AL'
mst,histf,out_f=sys.argv[1:4]
wants=[];labs=[]
for pre in ('-:14','-:15','-:16','-:17'):
  for k in range(9,10):
    for a in range(18,32):
      for c in (1,2):
        for tail in ('', 'R RU'):   # optional partial cycle before exit
          s=f"{pre} {' '.join([cy]*k)} {tail} L:{a} R:{c} AR:2 R:40"
          wants.append(spec(s)); labs.append((pre,k,tail,a,c))
goal=lambda s: s['room']==3 and s['y']==128 and C.abs_x(s)>=158 and not (s['rflags']&4)
out=search(mst,C.rows_of(histf),wants,goal,labs,top=8)
if out: C.write_inputs(out_f,out[0][4],f'p3c {out[0][3]}')
