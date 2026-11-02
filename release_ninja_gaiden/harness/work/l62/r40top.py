import sys; sys.path.insert(0,'work/l62')
from lib62 import *
pats=['Left A+Left A+Right A+Right Right','Left A+Left A+Right Right Right','Left A+Left A A+Right A+Right Right','Left A+Left A A+Right Right Right','Left A+Left A+Right A+Right A+Right Right']
tails={'R':['Right']*60,'AR':['A+Right']*2+['Right']*58,'bR':['-']*2+['Right']*58,'AAR':['A']*2+['A+Right']*2+['Right']*56,'UR':['Up+Right']*60, 'U':['Up']*10+['Right']*50}
fc=base(33735,pokes={0xC9:133,0x64:0})
res=[]
for p in pats:
  cyc=[row(x) for x in p.split()]
  for m in range(30,80):
    for tn,t in tails.items():
      rows=(cyc*20)[:m]+[row(x) for x in t]
      if legal_ok(rows): continue
      st=run(fc,rows)
      g=next((33736+i for i,s in enumerate(st) if s['room6e']==40 and RXY(s)[0]>=164 and RXY(s)[1]<=144),None)
      if g and RXY(st[-1])[0]>200 and st[-1]['room6e']==40: res.append((g,p,m,tn,RXY(st[-1]),st[-1]['hp65']))
res.sort(); 
for r in res[:15]: print(r)
fc.close()
