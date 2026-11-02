"""python work/l22f/trial.py <stage rows prefix|-> <n> "<grammar ROW*n;...>" [every] : play prefix[:n]+legalized grammar, print states"""
import sys
sys.path.insert(0,'work/l22f'); sys.path.insert(0,'.')
from lib import *
pre=[] if sys.argv[1]=='-' else C.rows_of(sys.argv[1])[:int(sys.argv[2])]
g=[]
for sg in sys.argv[3].split(';'):
    r,n=sg.rsplit('*',1); g+=[row(r)]*int(n)
ev=int(sys.argv[4]) if len(sys.argv)>4 else 1
tail=legal_after(pre,g); rows=pre+tail
r=play(rows,stops=[])
for i in range(len(pre),len(rows)):
    s=r.states[i]
    if (i-len(pre))%ev==0 or s['dead']&0x80 or i==len(rows)-1:
        print(F0+i+1,'+'.join(rows[i]) or '-',f"r{s['room']} X {ax(s)} sx {s['x']} y {s['y']} vy {s['vy']} coll {s['coll']} anim {s['anim']} hp {s['hp']} np {s['ninpo']} dead {s['dead']} BF {s['rng']}")
    if s['dead']&0x80: break
