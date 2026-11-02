"""python work/l22a/cmp.py <rows A> <rows B> [editsB]: play both, report first divergence of Ryu pos/hp/room and item/ninpo changes"""
import sys
sys.path.insert(0,'work/l22f'); sys.path.insert(0,'.')
from lib import *
def load(f,ed=None):
    rows=[tuple(r) for r in C.rows_of(f)]
    if ed:
        for e in ed.split(','):
            k,v=e.split('='); a,b=(k.split('-')+[k])[:2]
            for i in range(int(a),int(b)+1): rows[i-1]=row(v)
    return rows
A=load(sys.argv[1]); B=load(sys.argv[2], sys.argv[3] if len(sys.argv)>3 else None)
ra=play(A,stops=[]).states; rb=play(B,stops=[]).states
first=None
for i in range(min(len(ra),len(rb))):
    a,b=ra[i],rb[i]
    ka=(a['room'],ax(a),a['y'],a['hp']); kb=(b['room'],ax(b),b['y'],b['hp'])
    if ka!=kb and first is None:
        first=i+1; print('first pos diff row',i+1,'frame',F0+i+1,ka,kb)
    if (a['item'],a['ninpo'])!=(ra[i-1]['item'],ra[i-1]['ninpo']) or (b['item'],b['ninpo'])!=(rb[i-1]['item'],rb[i-1]['ninpo']):
        print(i+1,F0+i+1,'A',a['room'],ax(a),a['y'],'it',a['item'],'np',a['ninpo'],'hp',a['hp'],'| B',b['room'],ax(b),b['y'],'it',b['item'],'np',b['ninpo'],'hp',b['hp'])
n=min(len(ra),len(rb))-1
for nm,s in (('A',ra[n]),('B',rb[n])): print('end',nm,n+1,F0+n+1,'room',s['room'],'X',ax(s),'y',s['y'],'hp',s['hp'],'np',s['ninpo'],'item',s['item'],'BF',s['rng'])
