import sys, time
sys.path.insert(0, '.'); sys.path.insert(0, 'work/l11r')
from lib import *
from ng.solve import fast as FS
t0=time.time()
hist = INTRO + BASE[:421]
w=[[("A","Right")]*2+[("Right",)]*(90+k%3) for k in range(40)]
c=FS.legal_cands(w,hist); print('cands',time.time()-t0,flush=True)
P=FS.pool(hist); print('pool',time.time()-t0,flush=True)
P.save_all('s')
r=FS.run_chunked(P,'s',c,chunk=8,record='all'); print('run',time.time()-t0,flush=True)
P.close()
