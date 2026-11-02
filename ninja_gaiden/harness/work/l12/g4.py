import sys,pickle,itertools; sys.path.insert(0,'.'); sys.path.insert(0,'work/l12')
from lib import *
P=F.FastPool(2,boot_rows=None,ticks=True); P.put_all('s',open('states/mesen/l12_2470.mst','rb').read())
for wk in P.workers: wk.load('s')
H=96; cands=[];meta=[];seen=set()
for j1 in (36,37,38):
  for b1 in (68,70):
    for T in (76,77,78,80,81,99):
      for d2 in ('Left','',):
        for j2 in range(78,83):
          for bd in (1,2):
            w=[(),(),('Right',),('Right',)]
            for t in range(1,H+1):
                r=set(['Right'] if t<T else ([d2] if d2 else []))
                if j1<=t<j1+2: r.add('A')
                if b1<=t<b1+2: r.add('B')
                if j2<=t<j2+2: r.add('A')
                if j2+bd<=t<j2+bd+2: r.add('B')
                w.append(tuple(sorted(r)))
            en=L.Enforcer(list(HIST[:2470])[-1900:])
            lg=tuple(tuple(sorted(en.emit(x))) for x in w)
            if lg in seen: continue
            seen.add(lg);cands.append(lg);meta.append((j1,b1,T,d2,j2,bd))
print(len(cands),flush=True)
res=FS.run_chunked(P,'s',cands,chunk=8,record='all',log=lambda s:None); P.close()
out=[]
for m,c,r in zip(meta,cands,res):
    k=None
    for i,s in enumerate(r.states):
        if i>=4 and s['bosshp']==0: k=(i+1-4,s['hp'],s['ninpo']);break
    if k and k[0]<=86: out.append((k,m,c))
print(len(out))
for o in out[:60]: print(o[0],o[1])
pickle.dump(out,open('work/l12/g4.pkl','wb'))
