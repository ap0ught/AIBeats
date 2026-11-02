import sys; sys.path.insert(0,'.'); sys.path.insert(0,'work/w21'); sys.path.insert(0,'ng/stages')
from wlib import *
import a56_common as A
TR=A.tas_rows()
P3=C.rows_of('work/w21/p3c2_best.txt')
H=C.rows_of('work/l21f/h_f2_972.inputs.txt')
wants=[];labs=[]
for j in (91,100,110,115,118,120,122):
  for f in ([('B','Up'),('B','Right','Up')],):
    for d in range(0,4):
      for k0 in (4386,4387,4388,4389):
        w=list(P3); w[j:j+2]=f
        w=w+[('Right',)]*d+[tuple(r) for r in TR[k0:k0+700]]
        wants.append(w); labs.append((j,d,k0))
seen={}; cands=[]; lb=[]
for w,l in zip(wants,labs):
    lg=tuple(legal(w,H))
    if lg in seen: continue
    seen[lg]=1; cands.append(list(lg)); lb.append(l)
P=pool('states/mesen/w21_f2_4280.mst'); res=run(P,cands); P.close()
out=[]
for c,l,r in zip(cands,lb,res):
    if r is None: continue
    st=r.states
    # first index reaching room 4-entry X>=1170 y<=100 in room 3
    hit=next((i for i,s in enumerate(st) if i>300 and s['room']==3 and C.abs_x(s)>=1170 and s['y']<=100),None)
    if hit is None: 
        continue
    out.append((hit,-st[hit]['ninpo'],l,st[hit]['hp'],st[hit]['ninpo']))
out.sort()
for z in out[:12]: print(z)

