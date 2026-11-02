"""python work/l22c/bslash.py <prefix> <k0> <n> <i_from> <i_to> [hold]: TAS rows from k0 with B added on rows i..i+hold-1; report divergence"""
import sys
sys.path.insert(0,'work/l22f'); sys.path.insert(0,'.')
from lib import *
pre=C.rows_of(sys.argv[1]); k0,n,a,b=map(int,sys.argv[2:6]); h=int(sys.argv[6]) if len(sys.argv)>6 else 2
fc=core()
for i0 in range(a,b+1):
    want=[tuple(r) for r in TR[k0:k0+n]]
    for j in range(i0,i0+h):
        w=set(want[j]); w.add('B'); w.discard('Up'); want[j]=tuple(sorted(w))
    tail=legal_after(pre,want); rows=list(pre)+tail
    fc.load('s'); _,recs,_=fc.step(rows,record='all')
    div=None
    for i,s in enumerate(recs[len(pre):]):
        t=T[k0+i+1]
        if abs(ax(s)-ax(t))>2 or abs(s['y']-t['y'])>2 or s['room']!=t['room'] or s['hp']<t['hp']: div=i; break
    s=recs[len(pre)+(div if div is not None else len(tail)-1)]
    print(i0,'div',div,'X',ax(s),'y',s['y'],'hp',s['hp'],'np',s['ninpo'],'room',s['room'],flush=True)
fc.close()
