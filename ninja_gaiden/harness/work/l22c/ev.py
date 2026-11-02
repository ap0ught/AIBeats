"""python work/l22c/ev.py <mst> <hist> "<goal expr on s,X>" "<spec>" ["<spec>" ...]  first row meeting goal per spec"""
import sys; sys.path.insert(0,'.'); sys.path.insert(0,'work/w21')
from ng.solve import common as C, legality as L
from ng import fastcore as F
from wlib import spec
mst,hf,g=sys.argv[1:4]
hist=C.rows_of(hf)
fc=F.FastCore(boot_rows=None); fc.put('s',open(mst,'rb').read())
for sp in sys.argv[4:]:
    en=L.Enforcer(list(hist)[-1900:]); rows=[tuple(sorted(en.emit(w))) for w in spec(sp)]
    fc.load('s'); _,recs,_=fc.step(rows,record='all')
    hit=None
    for i,s in enumerate(recs):
        X=C.abs_x(s)
        if eval(g): hit=(i+1,X,s['y'],s['hp'],s['ninpo']); break
    print(sp,'->',hit)
fc.close()
