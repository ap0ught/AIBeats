import sys; sys.path.insert(0,'work/l62')
from lib62 import *
pre=rows_file('work/l62/pre43_37090.txt')
fc=base(mst='states/mesen/l63_35798.mst')
fc.load('b'); fc.step(pre, record='last'); fc.save('p'); fc._ka_slot='p'
hist=pre[-150:]
cands={}
for w in range(0,50):
  for h in (2,8):
    for t1 in ('Left','-'):
      for w2 in (0,10):
        rows=[row('Left')]*w+[row('A+Left')]*h+[row('Left')]*w2+[row(t1)]*30+[row('Left')]*60
        if legal_ok(rows,hist): continue
        cands[(w,h,w2,t1)]=rows
names=list(cands); res=[]
print('cands',len(cands),flush=True)
for i in range(0,len(names),64):
    rr=fc.run_batch('p',[cands[n] for n in names[i:i+64]],record='all')
    for n,r in zip(names[i:i+64],rr):
        for k,s in enumerate(r.states):
            X,y=RXY(s)
            if s['item']!=133 or y>=236: break
            if (X<=905 and y==208) or (y<=128 and 930<=X<=1000):
                res.append((37091+k,n,X,y,s['hp65'])); break
res.sort()
for x in res[:15]: print(x)
print('n',len(res))
fc.close()
