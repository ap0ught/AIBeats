# variant: Right pressed on the last k rows of the locked 1-1 file (frames 2475-k..2474), then 1-2 rows
import sys, itertools, os; sys.path.insert(0,'.'); sys.path.insert(0,'work/l12')
from lib import *
B0=2470
mst='states/mesen/l12_2470.mst'
if not os.path.exists(mst):
    fc=FS.boot(HIST[:B0],'logs/l12_base.trace.csv'); fc.save('s'); fc.save_file('s',mst,frame=B0); fc.close()
P=F.FastPool(2,boot_rows=None,ticks=True); P.put_all('s',open(mst,'rb').read())
for wk in P.workers: wk.load('s')
H=100
cands=[];meta=[];seen=set()
for k in (0,1,2,3,4):
  for j1 in range(33,42):
    for b1 in range(66,73):
      for j2d in (0,):   # second jump: on landing (detected later) - use fixed offsets grid instead
        for j2 in range(78,83):
          w=[()]*(4-k)+[('Right',)]*k
          for t in range(1,H+1):
            r=set()
            if t< 79: r.add('Right')
            else: r.add('Left' if j2d==0 else 'Right')
            if j1<=t<j1+2: r.add('A')
            if b1<=t<b1+2: r.add('B')
            if j2<=t<j2+2: r.add('A')
            if j2+1<=t<j2+3: r.add('B')
            w.append(tuple(sorted(r)))
          en=L.Enforcer(list(HIST[:B0])[-1900:])
          lg=tuple(tuple(sorted(en.emit(x))) for x in w)
          if lg in seen: continue
          seen.add(lg);cands.append(lg);meta.append((k,j1,b1,j2d,j2))
print(len(cands),flush=True)
import time
N=int(sys.argv[1]) if len(sys.argv)>1 else len(cands); CH=int(sys.argv[2]) if len(sys.argv)>2 else 32
cands=cands[:N]; meta=meta[:N]
t0=time.time()
res=FS.run_chunked(P,"s",cands,chunk=CH,record='all',log=lambda s: print(s,flush=True)); P.close()
print('t',time.time()-t0)
def kill(r):
    for i,s in enumerate(r.states):
        if i>=4 and s['bosshp']==0: return i+1,s['hp'],s['ninpo']
    return None
out=[]
for m,r in zip(meta,res):
    kk=kill(r)
    out.append(((kk[0]-4 if kk else 999), m, kk))
out.sort()
for o in out[:20]: print(o)
import pickle; pickle.dump((meta,cands,[o for o in out]),open('work/l12/g3.pkl','wb'))
