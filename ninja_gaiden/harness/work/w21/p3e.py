import sys; sys.path.insert(0,'.'); sys.path.insert(0,'work/w21')
from wlib import *
cy='R RU RU ALU AL'
mst,histf,out_f=sys.argv[1:4]
wants=[];labs=[]
for k in (8,9):
  for a in (23,24,25):
    base=spec(f"-:19 {' '.join([cy]*k)} L:{a} R:1 AR:2 R:40")
    for j in range(19,19+5*k):
        for form in ('UB:2','UB:2 R','U B'):
            w=list(base); ins=spec(form)
            w[j:j+len(ins)]=ins
            wants.append(w); labs.append((k,a,j,form))
goal=lambda s: s['room']==3 and s['y']==128 and C.abs_x(s)>=158 and not (s['rflags']&4)
out=search(mst,C.rows_of(histf),wants,goal,labs,top=10)
out=[z for z in out if z[5]['ninpo']==15]
print('with spin:'); 
for z in out[:10]: print(' ',z[0]+1,z[3])
if out: C.write_inputs(out_f,out[0][4],f'p3e {out[0][3]}')
