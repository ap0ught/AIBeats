"""python work/l22a/var.py <rows file> "<edits r1=ROW,r2-r3=ROW,...>" [print from-to] [legalize 0/1]
Play stage rows (1-based row numbers) with edits; print item/ninpo/room summary + rows in range."""
import sys
sys.path.insert(0,'work/l22f'); sys.path.insert(0,'.')
from lib import *
rows=C.rows_of(sys.argv[1])
rows=[tuple(r) for r in rows]
if len(sys.argv)>2 and sys.argv[2] not in ('','-'):
    for e in sys.argv[2].split(','):
        k,v=e.split('=')
        a,b=(k.split('-')+[k])[:2]
        for i in range(int(a),int(b)+1): rows[i-1]=row(v)
pr=(0,0)
if len(sys.argv)>3 and sys.argv[3]!='-':
    a,b=sys.argv[3].split('-'); pr=(int(a),int(b))
if len(sys.argv)>4 and sys.argv[4]=='1':
    rows=legal_after([],rows)
r=play(rows,stops=[])
prev=None
for i,s in enumerate(r.states):
    n=i+1
    key=(s['room'],s['item'],s['ninpo'],s['hp'],s['lives'])
    if pr[0]<=n<=pr[1] or key!=prev:
        print(n,F0+n,'+'.join(rows[i]) or '-',f"r{s['room']} X {ax(s)} x {s['x']} y {s['y']} vy {s['vy']} anim {s['anim']} coll {s['coll']} hp {s['hp']} np {s['ninpo']} item {s['item']} lives {s['lives']} dead {s['dead']} BF {s['rng']}")
    prev=key
