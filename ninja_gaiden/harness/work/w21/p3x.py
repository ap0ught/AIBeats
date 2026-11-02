import sys; sys.path.insert(0,'.'); sys.path.insert(0,'work/w21')
from wlib import *
cy='R RU RU ALU AL'.split()
cyc2='L AL AR R R'.split()
mst,histf,out_f=sys.argv[1:4]
wants=[];labs=[]
for a in range(0,5):
  for c,nm in ((cy,'cu'),(cyc2,'c5')):
    for ph in range(5):
      s=f"R:{a} {' '.join(c[ph:])} {' '.join(c*5)}"
      wants.append(spec(s)); labs.append((a,nm,ph))
  for u in range(1,30):
      wants.append(spec(f"R:{a} RU:{u} U:30")); labs.append((a,'U',u))
goal=lambda s: s['room']==4
out=search(mst,C.rows_of(histf),wants,goal,labs,top=8)
if out: C.write_inputs(out_f,out[0][4],f'p3x {out[0][3]}')
