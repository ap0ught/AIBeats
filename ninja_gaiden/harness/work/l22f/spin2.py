import sys
sys.path.insert(0,'work/l22f'); sys.path.insert(0,'.')
from lib import *
rows=C.rows_of('work/l22f/v3_rows.txt')
for i in range(1077,1092):
  for k in (0,1,2):
    want=list(rows[:i])+[('B','Up')]+[('Right',)]*k+list(rows[i+1:])
    new=list(rows[:i])+legal_after(rows[:i],want[i:])
    if new[i]!=('B','Up'): continue
    r=play(new,stops=[])
    gm=[F0+j+1 for j,s in enumerate(r.states) if s['gm']==0 and s['room']==5 and j>2400]
    s=r.states[-1]
    print(i,k,'gm0',gm[0] if gm else None,'end np',s['ninpo'],'hp',s['hp'],'room',s['room'],flush=True)
    if gm: C.write_inputs(f'work/l22f/sp_{i}_{k}.txt',new[:gm[0]-F0],'spin variant')
