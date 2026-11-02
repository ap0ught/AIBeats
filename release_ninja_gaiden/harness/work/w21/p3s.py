import sys; sys.path.insert(0,'.'); sys.path.insert(0,'work/w21')
from wlib import *
P3=C.rows_of('work/w21/p3c2_best.txt'); R3=C.rows_of('work/w21/r3f_rows.txt')
H=C.rows_of('work/l21f/h_f2_972.inputs.txt')
wants=[list(P3)+list(R3)];labs=[('base',)]
forms={'UB,UBR':[('B','Up'),('B','Right','Up')],'UB,BR':[('B','Up'),('B','Right')],'UB,UB':[('B','Up'),('B','Up')]}
for j in range(60,124):
    for fn,f in forms.items():
        w=list(P3)+list(R3)
        w[j:j+2]=f
        wants.append(w); labs.append((j,fn))
# also inside the r3f part (first 40 rows)
for j in range(124,124+0):
    for fn,f in forms.items():
        w=list(P3)+list(R3); w[j:j+2]=f; wants.append(w); labs.append((j,fn))
T={}
def goal(s): return False
seen={}; cands=[]; lb=[]
for w,l in zip(wants,labs):
    lg=tuple(legal(w,H))
    if lg in seen: continue
    seen[lg]=1; cands.append(list(lg)); lb.append(l)
P=pool('states/mesen/w21_f2_4280.mst')
res=run(P,cands); P.close()
ok=[]
base=None
for c,l,r in zip(cands,lb,res):
    if r is None or len(r.states)<len(c): continue
    s=r.states[-1]; s2=r.states[123]
    ok.append((s['ninpo'], -abs(C.abs_x(s)-0), l, C.abs_x(s), s['y'], s['hp'], C.abs_x(s2), s2['y']))
ref=None
ok.sort(key=lambda z:(-z[0], -z[3]))
for z in ok[:15]: print(z)
