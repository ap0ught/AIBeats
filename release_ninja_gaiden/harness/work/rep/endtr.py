import sys
sys.path.insert(0,'.')
from ng.solve import common as C
from ng import fastcore as F
hist=C.rows_of(sys.argv[1]); rows=C.rows_of(sys.argv[2]); a=int(sys.argv[3]); b=int(sys.argv[4])
fc=F.FastCore(boot_rows=hist)
n,recs,st=fc.step(rows,record='all'); fc.close()
prev=None
for s in recs:
    if not (a<=s['frame']<=b): continue
    k=(s['stage'],s['room'],s['gm'],s['hp'],s['timer'],s['ninpo'],s.get('gmode'))
    if k!=prev or '-v' in sys.argv:
        print(s['frame'],'x',C.abs_x(s),'y',s['y'],'st',s['stage'],'gm',s['gm'],'hp',s['hp'],'tm',s['timer'],'np',s['ninpo'],'gmode',s.get('gmode'),'rng',s.get('rng'))
        prev=k
