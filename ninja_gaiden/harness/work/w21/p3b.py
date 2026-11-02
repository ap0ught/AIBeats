import sys; sys.path.insert(0,'.'); sys.path.insert(0,'work/w21')
from wlib import *
CY={'cu':'R RU RU ALU AL'}
wants=[];labs=[]
for cn,rng in (('cu',range(6,13)),):
    for pre in ('-:3','-:2','-:4'):
      for k in rng:
        for a in range(10,40):
            for b in (0,):
                for c in (1,2,3):
                    s=f"{pre} {' '.join([CY[cn]]*k)} L:{a} -:{b} R:{c} AR:2 R:40"
                    wants.append(spec(s)); labs.append((pre,cn,k,a,b,c))
goal=lambda s: s['room']==3 and s['y']==128 and C.abs_x(s)>=158 and not (s['rflags']&4)
out=search('states/mesen/w21_tas4291.mst',C.rows_of('work/w21/blank.txt'),wants,goal,labs,top=12)
if out: C.write_inputs('work/w21/p3_best.txt',out[0][4],f'p3b {out[0][3]}')
