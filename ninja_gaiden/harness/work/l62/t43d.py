import sys; sys.path.insert(0,'work/l62')
from lib62 import *
pre=rows_file('work/l62/pre43_37090.txt')
fc=base(mst='states/mesen/l63_35798.mst')
fc.load('b'); fc.step(pre, record='last'); fc.save('p'); fc._ka_slot='p'
hist=pre[-150:]
cands={}
for s0 in range(0,12):
  for w in range(0,16):
    for mid in ('Left','-','Right'):
      for hold in (2,4):
        rows=[()]*s0+[row('Left')]*w+[row('A+Left')]*hold+[row(mid)]*16+[row('Left')]*60
        if legal_ok(rows,hist): continue
        cands[(s0,w,mid,hold)]=rows
names=list(cands); res=[]
print('cands',len(cands),flush=True)
for i in range(0,len(names),64):
    rr=fc.run_batch('p',[cands[n] for n in names[i:i+64]],record='all')
    for n,r in zip(names[i:i+64],rr):
        miny=min((RXY(s)[1],k) for k,s in enumerate(r.states) if k>s0+w+5)
        ok=next((k for k,s in enumerate(r.states) if RXY(s)[1]<=128 and RXY(s)[0]<=1000 and r.states[k-1]['y8a']>=RXY(s)[1]),None)
        res.append((miny[0], n, ok))
res.sort(key=lambda x:x[0])
for x in res[:15]: print(x)
fc.close()
