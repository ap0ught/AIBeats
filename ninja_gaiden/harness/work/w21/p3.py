import sys; sys.path.insert(0,'.'); sys.path.insert(0,'work/w21')
from wlib import *
CY={'c5':'L AL AR R R','c8':'AL:2 R:6'}
wants=[];labs=[]
for cn,rng in (('c5',range(6,15)),('c8',range(4,11))):
    for k in rng:
        for a in range(0,25):
            for b in (0,2):
                for c in (1,2,3):
                    s=f"-:3 {' '.join([CY[cn]]*k)} AL:2 L:{a} -:{b} R:{c} AR:2 R:40"
                    wants.append(spec(s)); labs.append((cn,k,a,b,c))
goal=lambda s: s['room']==3 and s['y']==128 and C.abs_x(s)>=158 and not (s['rflags']&4)
out=search('states/mesen/w21_tas4291.mst',C.rows_of('work/w21/blank.txt'),wants,goal,labs,top=12)
if out: C.write_inputs('work/w21/p3_best.txt',out[0][4],f'p3 {out[0][3]}')
