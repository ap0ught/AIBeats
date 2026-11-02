"""python work/l22p/play.py <mst> <rows file> [n] [--every k] [--from i]: play rows, print trace + room changes"""
import sys; sys.path.insert(0,'.')
from ng.solve import common as C
from ng import fastcore as F
a=sys.argv[1:]; ev=10**9; fr=0
if '--every' in a: i=a.index('--every'); ev=int(a[i+1]); del a[i:i+2]
if '--from' in a: i=a.index('--from'); fr=int(a[i+1]); del a[i:i+2]
rows=C.rows_of(a[1]); n=int(a[2]) if len(a)>2 else len(rows); rows=rows[:n]
fc=F.FastCore(boot_rows=None); fc.put('s',open(a[0],'rb').read()); fc.load('s')
_,recs,_=fc.step(rows,record='all'); fc.close()
p=None
for i,s in enumerate(recs):
    k=(s['room'],s['stage'])
    if k!=p or (i>=fr and (i-fr)%ev==0) or i==len(recs)-1:
        print(i+1,'+'.join(rows[i]) or '-','st',s['stage'],'r',s['room'],'X',C.abs_x(s),'x',s['x'],'y',s['y'],'coll',s['coll'],'anim',s['anim'],'hp',s['hp'],'np',s['ninpo'],'bf',s['rng'],'item',s.get('item'))
    p=k
