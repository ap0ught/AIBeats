"""print our per-frame trace: python work/rep/ptr.py hist rows a b"""
import sys
sys.path.insert(0,'.')
from ng.solve import common as C
from ng import fastcore as F
hist=C.rows_of(sys.argv[1]); rows=C.rows_of(sys.argv[2]); a=int(sys.argv[3]); b=int(sys.argv[4])
fc=F.FastCore(boot_rows=hist)
n,recs,st=fc.step(rows[:b-len(hist)+1],record='all'); fc.close()
for s in recs:
    if a<=s['frame']<=b:
        r=rows[s['frame']-len(hist)-1]
        print(s['frame'],'t',s['frame']-174,'x',C.abs_x(s),'y',s['y'],'vy',s['vy'],'anim',s['anim'],'hp',s['hp'],'np',s['ninpo'],'in','+'.join(r))
