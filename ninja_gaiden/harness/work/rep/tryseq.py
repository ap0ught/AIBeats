"""python work/rep/tryseq.py <mst> <hist> "<grammar fixed lengths ROW*n;...>" [a b]  - print trace with coll"""
import sys
sys.path.insert(0,'.')
from ng.solve import common as C, legality as L
from ng import fastcore as F
mst,hf,g=sys.argv[1:4]; a=int(sys.argv[4]) if len(sys.argv)>4 else 0; b=int(sys.argv[5]) if len(sys.argv)>5 else 999
hist=C.rows_of(hf)
w=[]
for sg in g.split(';'):
    r,n=sg.rsplit('*',1); w+=[() if r=='-' else tuple(r.split('+'))]*int(n)
en=L.Enforcer(hist[-1900:]); lg=[tuple(sorted(en.emit(x))) for x in w]
fc=F.FastCore(boot_rows=None, ticks=True); fc.put('s',open(mst,'rb').read()); fc.load('s')
r=fc.run_batch('s',[lg],record='all',stops=[(0x6D,'changed',0)]); fc.close()
f0=len(hist)
for i,s in enumerate(r[0].states):
    if a<=i<=b: print(f0+i+1,'x',C.abs_x(s),'y',s['y'],'vy',s['vy'],'coll',s['coll'],'rfl',s['rflags'],'anim',s['anim'],'hp',s['hp'],'np',s['ninpo'],'in','+'.join(lg[i]),'(want '+'+'.join(w[i])+')' if lg[i]!=tuple(sorted(w[i])) else '')
