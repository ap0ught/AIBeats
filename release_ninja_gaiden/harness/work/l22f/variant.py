"""python work/l22f/variant.py <rows> <out|-> "i:ROW;i:ROW;..." [check frames comma]  -> replace rows (re-legalize whole tail), report"""
import sys
sys.path.insert(0,'work/l22f'); sys.path.insert(0,'.')
from lib import *
rows=list(C.rows_of(sys.argv[1])); outf=sys.argv[2]
want=list(rows)
for spec in sys.argv[3].split(';'):
    i,rw=spec.split(':'); want[int(i)]=row(rw)
lo=min(int(s.split(':')[0]) for s in sys.argv[3].split(';'))
new=list(rows[:lo])+legal_after(rows[:lo],want[lo:])
chg=[(i,want[i],new[i]) for i in range(lo,len(new)) if new[i]!=want[i]]
print('legalizer changed',len(chg),chg[:6])
r=play(new)
fr=[int(x) for x in sys.argv[4].split(',')] if len(sys.argv)>4 else []
for f in fr:
    i=f-F0-1
    if i<len(r.states): s=r.states[i]; print('f',f,'X',ax(s),'y',s['y'],'hp',s['hp'],'np',s['ninpo'],'room',s['room'])
s=r.states[-1]; print('end f',F0+len(r.states),'X',ax(s),'y',s['y'],'hp',s['hp'],'np',s['ninpo'],'room',s['room'])
if outf!='-': C.write_inputs(outf,new,'variant'); print('wrote',outf,len(new))
