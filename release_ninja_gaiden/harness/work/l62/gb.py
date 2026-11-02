"""l62: ghoul/axe boost grid from 35,300 (X 494 floor): wait w (blank), run Right j, jump (A+Right x2), Right x tail; also double-jump variant.
Goal: on the y-128 block (636<=X<=690, y<=128) or the far floor (X>=704, y 208)."""
import sys; sys.path.insert(0,'work/l62')
from lib62 import *
pre=rows_file('work/l62/pre_r40_35300.txt')
fc=base(mst='states/mesen/l62_33589.mst')
fc.load('b'); fc.step(pre, record='last'); fc.save('p'); fc._ka_slot='p'
hist=pre[-150:]
cands={}
for w in range(0,46):
  for j in range(0,70):
    for tail in ('Right','A2'):
      t=[row('Right')]*130 if tail=='Right' else ([row('Right')]*16+[row('A+Right')]*2+[row('Right')]*112)
      rows=[()]*w+[row('Right')]*j+[row('A+Right')]*2+t
      if legal_ok(rows,hist): continue
      cands[(w,j,tail)]=rows
names=list(cands); res=[]; best=(0,None)
print('cands',len(cands),flush=True)
for i in range(0,len(names),64):
    rr=fc.run_batch('p',[cands[n] for n in names[i:i+64]],record='all')
    for n,r in zip(names[i:i+64],rr):
        for k,s in enumerate(r.states):
            X,y=RXY(s)
            if s['item']!=133: break
            if (636<=X<=690 and y<=128) or (X>=704 and y==208):
                res.append((35301+k,n,X,y,s['hp65'])); break
        mx=max((RXY(s)[0] for s in r.states if RXY(s)[1]<=208),default=0)
        if mx>best[0]: best=(mx,n)
res.sort()
for x in res[:15]: print(x)
print('n goals',len(res),'max X',best)
fc.close()
