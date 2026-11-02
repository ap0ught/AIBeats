import sys; sys.path.insert(0,'.'); sys.path.insert(0,'work/w21')
from wlib import *
cy='R RU RU ALU AL'
wants=[];labs=[]
for a in (0,1,2):
  for b in range(10,19):
    for c in (2,3):
      for d in (1,2):
        for e in range(0,14):
          for ph in range(0,5):
            cc=cy.split()
            s=f"R:{a} AR:2 R:{b} L:{c} AR:{d} R:{e} {' '.join(cc[ph:])} {' '.join([cy]*13)}"
            wants.append(spec(s)); labs.append((a,b,c,d,e,ph))
goal=lambda s: s['room']==3
out=search('states/mesen/w21_tas4206.mst',C.rows_of('work/w21/blank.txt'),wants,goal,labs,top=10)
if out: C.write_inputs('work/w21/p2k_best.txt',out[0][4],f'p2k {out[0][3]}')
