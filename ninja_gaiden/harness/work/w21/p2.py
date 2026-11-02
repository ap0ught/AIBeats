import sys; sys.path.insert(0,'.'); sys.path.insert(0,'work/w21')
from wlib import *
cy='R RU RU ALU AL'
wants=[];labs=[]
for a in range(0,10):
    for b in range(4,34):
        for ph in range(0,5):   # start the cycle at phase ph
            c=cy.split()
            s=f"R:{a} AR:2 R:{b} {' '.join(c[ph:])} {' '.join([cy]*13)}"
            wants.append(spec(s)); labs.append((a,b,ph))
goal=lambda s: s['room']==3
out=search('states/mesen/w21_tas4206.mst',C.rows_of('work/w21/blank.txt'),wants,goal,labs,top=10)
if out: C.write_inputs('work/w21/p2_best.txt',out[0][4],f'p2 {out[0][3]}')
