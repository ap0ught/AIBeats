import sys, itertools; sys.path.insert(0,'.'); sys.path.insert(0,'work/l12')
from lib import *
H=110
cands=[];meta=[]
seen=set()
for j in range(30,56):
  for ha in (2,6,14,30):
    for b in range(max(j+2,58),78):
      w=[]
      for t in range(1,H+1):
        r={'Right'}
        if j<=t<j+ha: r.add('A')
        if b<=t<b+2: r.add('B')
        w.append(tuple(sorted(r)))
      lg=legalize(w)
      if lg in seen: continue
      seen.add(lg); cands.append(lg); meta.append((j,ha,b))
print(len(cands),flush=True)
P=pool(2)
res=run(P,cands)
P.close()
out=[]
for m,r in zip(meta,res):
    k=kill(r)
    mn=min(s['bosshp'] for s in r.states) if r else 99
    out.append((k[0] if k else 999, mn, m, k))
out.sort()
for o in out[:25]: print(o)
