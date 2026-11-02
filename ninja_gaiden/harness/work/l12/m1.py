import sys,pickle; sys.path.insert(0,'.'); sys.path.insert(0,'work/l12')
from lib import *
meta,cands,out=pickle.load(open('work/l12/g3.pkl','rb'))
c=cands[meta.index((2,37,70,0,80))]
P=F.FastPool(1,boot_rows=None,ticks=True); P.put_all('s',open('states/mesen/l12_2470.mst','rb').read()); P.workers[0].load('s')
r=P.run_batch('s',[c],record='all')[0]; P.close()
for i in range(76,84):
    s=r.states[i+3]; print(i, c[i+3], 'pad',s['pad'],'new',s['padnew'],s['anim'],s['rflags'],s['vy'],s['ninpo'],s['bosshp'])
