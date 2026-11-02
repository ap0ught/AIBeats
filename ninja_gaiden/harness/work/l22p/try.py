"""python -u work/l22p/try.py <mst> "<spec>" [--hist file] [--every k]  per-frame trace (legalized on hist or blank)"""
import sys; sys.path.insert(0,'.'); sys.path.insert(0,'work/w21')
from ng.solve import common as C, legality as L
from ng import fastcore as F
from wlib import spec, fmt
a=sys.argv[1:]; hist=[()]*60; ev=1
if '--hist' in a: i=a.index('--hist'); hist=C.rows_of(a[i+1]); del a[i:i+2]
if '--every' in a: i=a.index('--every'); ev=int(a[i+1]); del a[i:i+2]
want=spec(a[1]); en=L.Enforcer(list(hist)[-1900:]); rows=[tuple(sorted(en.emit(w))) for w in want]
fc=F.FastCore(boot_rows=None); fc.put('s',open(a[0],'rb').read()); fc.load('s')
_,recs,_=fc.step(rows,record='all'); fc.close()
ab={'Right':'R','Left':'L','Up':'U','Down':'D','A':'A','B':'B'}
for i,(s,r) in enumerate(zip(recs,rows)):
    if i%ev and i!=len(rows)-1: continue
    print(i+1,''.join(ab[b] for b in r) or '-','r%d'%s['room'],'X',C.abs_x(s),'x',s['x'],'y',s['y'],'vy',s['vy'],'coll',s['coll'],'anim',s['anim'],'sc',s['scroll'],'hp',s['hp'],'np',s['ninpo'],'bf',s['rng'])
